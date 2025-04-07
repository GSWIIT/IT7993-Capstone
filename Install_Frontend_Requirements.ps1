Write-Host "Checking to see if Node.JS is installed..."
#check NodeJS requirement
$nodeJS = Get-Package | Where-Object {$_.Name -eq "Node.JS"}
if ((Measure-Object -InputObject $nodeJS).Count -lt 1)
{
    #install MSI
    Write-Host "Please wait while Node.JS is installed..."
    $nodeInstallerProcess = Start-Process -FilePath "msiexec" -ArgumentList "/i", "$($PSScriptRoot)\Backend\Requirements\node-v22.14.0-x64.msi", "/qb" -Wait -PassThru
    if($nodeInstallerProcess.ExitCode -eq 0)
    {
        Write-Host "`nNode.JS installed! Please close this window and restart the script to continue."
        Write-Host "If running from VS Code, exit all open terminals and VS Code completely. Then, restart VS Code and run again." -ForegroundColor Yellow
        pause
        exit
    }
    if($nodeInstallerProcess.ExitCode -eq 3010)
    {
        Write-Host "`nNode.JS installed! However, a computer restart is required to finish the installation."
        Write-Host "Please restart your computer, then run this script again." -ForegroundColor Yellow
        pause
        exit
    }
}
else 
{
    Write-Host "NodeJS detected." -ForegroundColor Green
}

Start-Sleep -Seconds 3

try 
{
    $nodeVersion = & node -v
    if($null -ne $nodeVersion)
    {
        Write-Host "Node.JS detected! Version: $($nodeVersion)"
    }
}
catch 
{
    Write-Host "Error: Node.JS version check failed. Please make sure Node.JS is installed and added to the PATH variable." -ForegroundColor Red
    Write-Host "Caught Exception: $($_)"
    pause
    exit
}

try 
{
    $npmVersion = & npm -v
    if($null -ne $npmVersion)
    {
        Write-Host "NPM detected! Version: $($npmVersion)"
    }
}
catch 
{
    Write-Host "Error: NPM version check failed. Please make sure Node.JS is installed and added to the PATH variable." -ForegroundColor Red
    Write-Host "Caught Exception: $($_)"
    pause
    exit
}

Write-Host "`nInstalling required NPM packages...`n"

Set-Location "$($PSScriptRoot)\Frontend\FaceGuard_Dashboard"

npm install vite
npm install @vitejs/plugin-react
npm install react @types/react
npm install react-router-dom
npm install @tailwindcss/vite
npm install react-scroll

Write-Host "Script complete!"