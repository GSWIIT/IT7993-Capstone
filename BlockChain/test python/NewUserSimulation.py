from web3 import Web3
import hashlib
import random
import json
import os
import time

# Configurations
ALCHEMY_API_URL = "https://eth-sepolia.g.alchemy.com/v2/Dv7X6LhBni2gxlcUzAPs51cKqdUHK-8Y"
CONTRACT_ADDRESS = "0x427461725DD56ed90fB89101B2434D760D601ecb"
PRIVATE_KEY = "9ea2167fb16f55f70f2afca8644f9903b8f05f45c6268cf5c435b5df777c82a5"  # Owner's private key, need to delete later
#need to set up dotenv
#PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Owner's private key

abi_file_path = os.path.abspath("../BlockChain/artifacts/contracts/FaceGuard.sol/FaceGuard.json")
print(f"Loading ABI from: {abi_file_path}")

with open(abi_file_path, "r") as f:
    abiJSONContent = json.load(f)

CONTRACT_ABI = abiJSONContent["abi"]

def hash_password(password: str) -> str:
    #Simulates hashing of password (should match how it's stored in contract)
    return hashlib.sha256(password.encode()).hexdigest()

# Connect to Sepolia
w3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))

if w3.is_connected() == True:
    print("W3 Connection to contract successful!")
else:
    print("W3 connection failed!")
    exit

#if script connected to Web3 successfully and did not exit, we should be able to load contract into variable
# Load contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

#to write to the contract, we have to prove we are the owner by using the private key of the wallet that deployed the contract
owner_account = w3.eth.account.from_key(PRIVATE_KEY)
owner_address = owner_account.address
w3.eth.default_account = owner_address

# Debug: Check contract owner (cant do this because our smart contract has the owner as a private variable)
#contract_owner = contract.functions.owner().call()
#print(f"Contract Owner: {contract_owner}")
#print(f"Your Address: {owner_address}")
#print("If the two addresses match above, then we have permission to write to the contract!")

print("Register User Simulation\n")
username = input("Enter username: ")
password = input("Enter password: ")
test_GUID = "616f0529-ea40-4ca6-9cfd-f32535b0f462"

#this would be done in backend but for sim purposes, we do in in client
password = hash_password(password)
hashedFace = hash_password(str(random.random())) #simulates a face hash (just mades a hash made with a random number)

print("\nNew User going to be added to blockchain:")
print("User: " + username)
print("Pass Hash: " + password)
print("Face Hash: " + hashedFace)

#should be done in backend
print("\nChecking if user already exists...")

userExists = False

user_obj = contract.functions.getUser(username).call()
print(user_obj)
if user_obj[0] == "":
    userExists = False
else:
    userExists = True

if userExists == True:
    print("User exists. Cannot register new user.")
    exit
else:
    print("User does not exist! Proceeding to register user...")

if userExists == False:
    #estimate the cost of the ethereum transaction by predicting gas
    estimated_gas = contract.functions.registerUser(username, password, hashedFace, test_GUID).estimate_gas({"from": owner_address})

    #register user (use estimated gas & add an extra 50000 buffer to make sure transaction goes through)
    tx = contract.functions.registerUser(
        username, password, hashedFace, test_GUID
    ).build_transaction({
        "from": owner_address,
        "nonce": w3.eth.get_transaction_count(owner_address),
        "gas": estimated_gas + 50000, 
        "gasPrice": w3.to_wei("10", "gwei")
    })

    # Sign transaction with private key
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

    # Send transaction to blockchain
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    # Wait for confirmation of transaction
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Print transaction status
    if receipt.status == 1:
        print(f"Transaction successful! Block: {receipt.blockNumber}")
        print("Waiting a few more seconds...")
        time.sleep(15)

        print("Checking to see if user exists now...")
        user_obj = contract.functions.getUser(username).call()
        print(user_obj)
        if user_obj[0] == "":
            userExists = False
            #this should not happen if transaction went through
            print("The transaction went through but the user is still not found. It will show up eventually I guess")
        else:
            userExists = True
            print("The user is now on the blockchain! The script was successful.")
    else:
        print("Transaction failed! User was not created.")