#check NodeJS requirement
$nodeJS = Get-Package | Where-Object {$_.Name -eq "Node.JS"}

if ((Measure-Object -InputObject $nodeJS).Count -lt 1)
{
    #install MSI
    & "$($PSScriptRoot)\Backend\Requirements\node-v22.14.0-x64.msi"
}

Start-Sleep -Seconds 3

#install required Node JS packages
npm install --save-dev hardhat
npm install dotenv --save
npm install --save-dev @nomiclabs/hardhat-ethers "ethers@^5.0.0"

#install required Python packages
pip install -r "$($PSScriptRoot)\Backend\Requirements\requirements.txt"