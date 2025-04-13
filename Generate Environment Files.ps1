Write-Host "Generating Backend env file..."
Write-Host "Please enter the following information:`n"

$envContent = @()

$alchemyAPIURL = Read-Host "Enter Alchemy API link"
$envContent += "ALCHEMY_API_URL=$($alchemyAPIURL)"

$walletSecretKey = Read-Host "Enter Owner Wallet Secret Key (the same wallet that deployed the smart contract)"
$envContent += "PRIVATE_KEY=$($walletSecretKey)"

$contractAddress = Read-Host "Enter deployed smart contract address (leave blank if you have not deployed a smart contract yet)"
$envContent += "CONTRACT_ADDRESS=$($contractAddress)"

$choice = $host.UI.PromptForChoice("Would you like to run the Flask API locally?", "If not, you can enter a domain name.", @([System.Management.Automation.Host.ChoiceDescription]::new("&Yes"), [System.Management.Automation.Host.ChoiceDescription]::new("&No")), 0)

if($choice -eq 0)
{
    $envContent += "RUN_FLASK_LOCALLY=True"
    $backendDomainName = "http://localhost:5000"
}
else 
{
    $envContent += "RUN_FLASK_LOCALLY=False"

    $backendDomainName = Read-Host "Enter ONLY the domain name of the website (with http:// or https://) (example: https://faceguard-it7993.com)"
    $envContent += "BACKEND_DOMAIN_NAME=$($backendDomainName)"
}

Write-Host "`nGenerating file..."
New-Item -Path "$($PSScriptRoot)\Backend\LoginApp\src\" -Name ".env" -ItemType File -Force
$envContent | Set-Content -Path "$($PSScriptRoot)\Backend\LoginApp\src\.env"

Write-Host "-----------------------------------------"
Write-Host "`nGenerating Blockchain environment file..."

$envContent = @()

$envContent += "API_URL=$($alchemyAPIURL)"
$envContent += "PRIVATE_KEY=$($walletSecretKey)"

Write-Host "`nGenerating file..."
New-Item -Path "$($PSScriptRoot)\Blockchain\" -Name ".env" -ItemType File -Force
$envContent | Set-Content -Path "$($PSScriptRoot)\Blockchain\.env"

Write-Host "-----------------------------------------"
Write-Host "`nGenerating Frontend environment file..."

$envContent = @()

$envContent += "VITE_BACKEND_API_DOMAIN_NAME=$($backendDomainName)"

New-Item -Path "$($PSScriptRoot)\Frontend\FaceGuard_Dashboard\" -Name ".env" -ItemType File -Force
$envContent | Set-Content -Path "$($PSScriptRoot)\Frontend\FaceGuard_Dashboard\.env"