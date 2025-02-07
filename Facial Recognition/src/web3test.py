from web3 import Web3
import json


# Connect to your Ethereum node (use Infura or your local node)
w3 = Web3(Web3.HTTPProvider("https://eth-sepolia.g.alchemy.com/v2/Dv7X6LhBni2gxlcUzAPs51cKqdUHK-8Y"))  # Replace with your provider

with open("./blockchain/artifacts/contracts/FaceGuard.sol/FaceGuard.json", 'r') as file:
    contract_data = json.load(file)

# Extract the ABI from the loaded contract data
abi = contract_data['abi']
bytecode = contract_data['bytecode']

# Set up your account (use your account's private key here)
#my_account = w3.eth.account.privateKeyToAccount('9ea2167fb16f55f70f2afca8644f9903b8f05f45c6268cf5c435b5df777c82a5')
my_account = w3.eth.account.from_key('9ea2167fb16f55f70f2afca8644f9903b8f05f45c6268cf5c435b5df777c82a5')

# The ABI and address of your deployed contract
contract_address = '0x4320b36B3EfCe78468f4c10FB2536786339673D4'
contract_abi = abi  # Replace with the ABI of your contract

# Set up the contract object
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

"""
# Function to store the image hash in the contract
def store_image_hash(image_hash):
    # Build the transaction to call storeImageHash
    tx = contract.functions.storeImageHash(image_hash).buildTransaction({
        'from': my_account.address,
        'gas': 2000000,
        'gasPrice': w3.toWei('20', 'gwei'),
        'nonce': w3.eth.getTransactionCount(my_account.address),
    })

    # Sign the transaction with your private key
    signed_tx = w3.eth.account.signTransaction(tx, private_key='9ea2167fb16f55f70f2afca8644f9903b8f05f45c6268cf5c435b5df777c82a5')

    # Send the transaction
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # Wait for transaction to be mined
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print("Transaction receipt:", receipt)

# Store the image hash
#store_image_hash("asdfasdfyasorhnasgdlasdfpt")
"""

   # Build the transaction to call storeImageHash
tx = contract.functions.getUserByUsername('DeploymentUser123456789').build_transaction({
        'from': my_account.address,
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(my_account.address),
    })

    # Sign the transaction with your private key
signed_tx = w3.eth.account.sign_transaction(tx, private_key='9ea2167fb16f55f70f2afca8644f9903b8f05f45c6268cf5c435b5df777c82a5')

    # Send the transaction
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    # Wait for transaction to be mined
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Transaction receipt:", receipt)
print(receipt.values)