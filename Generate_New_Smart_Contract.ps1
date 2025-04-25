Write-Host "Attempting to deploy a new smart contract..."

Set-Location "$($PSScriptRoot)\Blockchain"

& npx hardhat compile

if ($LASTEXITCODE -ne 0)
{
    Write-Host "Error occurred while compiling smart contract!" -ForegroundColor Red
    pause
    Set-Location "$($PSScriptRoot)"
    return
}
else 
{
    Write-Host "Contract compiled. Deploying to blockchain..."
    $contractAddress = & npx hardhat run ".\scripts\deploy.js" --network sepolia
    Write-Host "Smart contract deployed to: $($contractAddress)."
    Write-Host "`nApplying new address to .env file..."
    if(Test-Path -Path "$($PSScriptRoot)\Backend\LoginApp\src\.env")
    {
        $content = Get-Content -Path "$($PSScriptRoot)\Backend\LoginApp\src\.env"
        $overwrittenContent = @()

        foreach($line in $content)
        {
            $finalLine = $line
            if($line -match "CONTRACT_ADDRESS=")
            {
                $finalLine = "CONTRACT_ADDRESS=$($contractAddress)"
            }
            $overwrittenContent += $finalLine
        }
        
        $overwrittenContent | Set-Content -Path "$($PSScriptRoot)\Backend\LoginApp\src\.env"
        Write-Host "New contract address added to .env file successfully! To use the new contract, just restart the Flask app." -ForegroundColor Green
        pause
    }
}

Set-Location "$($PSScriptRoot)"