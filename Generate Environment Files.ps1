Write-Host "Generating Backend env file..."
Write-Host "Please enter the following information:`n"

$alchemyAPIURL = Read-Host "Enter Alchemy API link:"
$walletSecretKey = Read-Host "Enter Owner Wallet Secret Key (the same wallet that deployed the smart contract)"
$contractAddress = Read-Host "Enter deployed smart contract address (leave blank if you have not deployed a smart contract yet)"
