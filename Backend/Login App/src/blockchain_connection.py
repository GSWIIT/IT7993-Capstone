import os
import json
from web3 import Web3
from pathlib import Path

# Start from the current script's directory
script_dir = Path(__file__).resolve().parent

# Configurations
ALCHEMY_API_URL = "https://eth-sepolia.g.alchemy.com/v2/Dv7X6LhBni2gxlcUzAPs51cKqdUHK-8Y"
CONTRACT_ADDRESS = "0xff9D0ec83F1EF3626Cbc975d340E69D65BF83cC6"
PRIVATE_KEY = "9ea2167fb16f55f70f2afca8644f9903b8f05f45c6268cf5c435b5df777c82a5"  # Owner's private key, need to delete later
#need to set up dotenv
#PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Owner's private key

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
    print("W3 connection failed!")
    exit

#if script connected, we should be able to load contract into variable
# Load contract
CONTRACT = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

#to interact with the contract, we have to prove we are the owners by using the private key of the wallet that deployed the contract
owner_account = w3.eth.account.from_key(PRIVATE_KEY)
owner_address = owner_account.address
w3.eth.default_account = owner_address

def get_contract():
    return CONTRACT

def get_w3_object():
    return w3

def get_owner_address():
    return owner_address

def get_private_key():
    return PRIVATE_KEY