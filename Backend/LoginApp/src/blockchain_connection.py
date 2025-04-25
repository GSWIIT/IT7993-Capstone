import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
from threading import Lock
import time

# Start from the current script's directory
script_dir = Path(__file__).resolve().parent

load_dotenv()

#the lock is used to only process one transaction at a time, to keep the nonce updated properly
tx_lock = Lock()

# Configurations
#ALCHEMY_API_URL = "https://eth-sepolia.g.alchemy.com/v2/Dv7X6LhBni2gxlcUzAPs51cKqdUHK-8Y"
#CONTRACT_ADDRESS = "0x0bAD6741146CdF278CAEcf26EF977b8b99Cf0D31"
#PRIVATE_KEY = "9ea2167fb16f55f70f2afca8644f9903b8f05f45c6268cf5c435b5df777c82a5"  # Owner's private key, need to delete later
#need to set up dotenv
ALCHEMY_API_URL = os.getenv("ALCHEMY_API_URL")  # Owner's private key
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")  # Owner's private key
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Owner's private key

# Start from the current script's directory
script_dir = Path(__file__).resolve().parent

# Search project directory for ABI file until we find FaceGuard.json or reach the filesystem root
def find_file(start_path, target_file):
    for root, _, files in os.walk(start_path):
        if target_file in files:
            return os.path.join(root, target_file)
    return None

# Get the directory three levels up from the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
start_dir = os.path.abspath(os.path.join(current_dir, "../../.."))

# Search for the file
file_path = find_file(start_dir, "FaceGuard.json")

abi_file_path = os.path.abspath(file_path)
print(f"Loading ABI from: {abi_file_path}")

with open(abi_file_path, "r") as f:
    abiJSONContent = json.load(f)

CONTRACT_ABI = abiJSONContent["abi"]

# Connect to Sepolia
w3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))

if w3.is_connected() == True:
    print("W3 Connection to contract successful!")
else:
    print("W3 connection failed! Please make sure the API URL is correct in the .env file!")
    exit

#if script connected, we should be able to load contract into variable
# Load contract
CONTRACT = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

#to interact with the contract, we have to prove we are the owners by using the private key of the wallet that deployed the contract
owner_account = w3.eth.account.from_key(PRIVATE_KEY)
owner_address = owner_account.address
w3.eth.default_account = owner_address

#we must keep track of the nonce manually to allow for true asynchronous transactions
current_nonce = w3.eth.get_transaction_count(owner_address)

def get_contract():
    return CONTRACT

def get_w3_object():
    return w3

def get_owner_address():
    return owner_address

def get_private_key():
    return PRIVATE_KEY

def write_to_blockchain(w3_function, w3_arguments):
    global current_nonce #referencing the variable created above the function

    with tx_lock:
        nonce = current_nonce
        
        try:
            print(f"Estimating gas for function [{w3_function}] with arguments [{w3_arguments}]...")
            estimated_gas = w3_function(*w3_arguments).estimate_gas({"from": owner_address})
            print(f"Estimated gas: {estimated_gas}...")
        except Exception as e:
            raise Exception("Blockchain exception caught! Error:" + str(e.args[0]) + "!")
        
        try:
            # Get the suggested gas price
            gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
            max_priority_fee = w3.to_wei("4", "gwei")  # Priority fee (adjust based on congestion)
            max_fee_per_gas = gas_price + max_priority_fee

            tx = w3_function(*w3_arguments).build_transaction({
                "from": owner_address,
                "nonce": nonce,
                "gas": estimated_gas + 50000,
                "maxFeePerGas": max_fee_per_gas,  # Total fee
                "maxPriorityFeePerGas": max_priority_fee,  # Tip for miners
            })

            # Sign transaction with private key
            signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
            print("Sending transaction...")
            # Send transaction to blockchain
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            current_nonce += 1 #add to the global variable to ensure that every transaction has a unique nonce. Needed for true async processing.
            print("Transaction sent! Nonce variable updated, new nonce is:", current_nonce)
            return tx_hash
        except Exception as e:
            #make sure nonce is up to date, this may be the cause of the error.
            current_nonce = w3.eth.get_transaction_count(owner_address)
            raise Exception("Python exception occurred! Error:" + str(e.args[0]) + "! Please try again in a few moments...")