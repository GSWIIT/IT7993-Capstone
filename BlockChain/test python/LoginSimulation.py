from web3 import Web3
import hashlib
import json
import os

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
    """Simulates hashing of password (should match how it's stored in contract)."""
    return hashlib.sha256(password.encode()).hexdigest()

# Connect to Sepolia
w3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))

if w3.is_connected() == True:
    print("W3 Connection to contract successful!")
else:
    print("W3 connection failed!")
    exit

#if script connected and did not exit, we should be able to load contract into variable
# Load contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

#to interact with the contract, we have to prove we are the owners by using the private key of the wallet that deployed the contract
owner_account = w3.eth.account.from_key(PRIVATE_KEY)
owner_address = owner_account.address
w3.eth.default_account = owner_address

print("\nLogin User Simulation")
username = input("Enter username: ")
password = input("Enter password: ")

#get hashed version of PW
password = hash_password(password) 

print("We would send this data to the backend here...")

#this would be done in backend but for sim purposes, we do in in client
userExists = False
passwordLoginSuccess = False
faceHashLoginSuccess = False

user_obj = contract.functions.getUser(username).call()
print(user_obj)
if user_obj[0] == "":
    userExists = False
    print("The username and/or password is incorrect.")
    exit
else:
    userExists = True
    #now we compare the password hashes to see if they match
    if password == user_obj[1]:
        print("Username and password match! First portion of login was successful!")
        passwordLoginSuccess = True
    else:
        print("The password entered is incorrect.")
        exit


print("\nThis is where we would ask for the face hash...")
print("User face hash: " + user_obj[2])
print("We will assume that we were able to match the face.")
faceHashLoginSuccess = True

if passwordLoginSuccess == True and faceHashLoginSuccess == True:
    print("Simulated login successful!")
else:
    print("Simulated login failed!")