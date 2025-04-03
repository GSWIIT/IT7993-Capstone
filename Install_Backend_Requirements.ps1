Write-Host "Checking to see if CMake is installed..."
#check CMake requirement
$cmake = Get-Package | Where-Object {$_.Name -eq "CMake"}
if ((Measure-Object -InputObject $cmake).Count -lt 1)
{
    #install MSI
    Write-Host "Please wait while CMake is installed..."
    $cmakeInstallerProcess = Start-Process -FilePath "msiexec" -ArgumentList "/i", "$($PSScriptRoot)\Backend\Requirements\cmake-4.0.0-rc2-windows-x86_64.msi", "/qb" -Wait -PassThru
    if($cmakeInstallerProcess.ExitCode -eq 0)
    {
        Write-Host "`nCMake installed successfully!" -ForegroundColor Green
    }
    if($cmakeInstallerProcess.ExitCode -eq 3010)
    {
        Write-Host "`nCMake installed! However, a computer restart is required to finish the installation."
        Write-Host "Please restart your computer, then run this script again." -ForegroundColor Yellow
        pause
        exit
    }
}
else 
{
    Write-Host "CMake detected." -ForegroundColor Green
}

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
        Write-Host "Node.JS detected! Version: $($npmVersion)"
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

#install required Node JS packages
npm install --save-dev hardhat
npm install dotenv --save
npm install --save-dev @nomiclabs/hardhat-ethers "ethers@^5.0.0"

Write-Host "`nNPM packages installed.`n"

Write-Host "Verifying that VS C++ Build Tools are installed... (This may take a minute...)"
$buildToolsProcess = Start-Process -FilePath "$($PSScriptRoot)\Backend\Requirements\vs_BuildTools.exe" -ArgumentList "--passive", "--installWhileDownloading", "--add Microsoft.VisualStudio.Workload.VCTools;includeRecommended" -Wait -PassThru
if($buildToolsProcess.ExitCode -eq 0)
{
    Write-Host "VS C++ Build Tools installed successfully!" -ForegroundColor Green
}

#update PIP if necessary
& python.exe -m pip install --upgrade pip

Start-Sleep -Seconds 10

#install dlib wheel for Python 3.11, needed for face_recognition module
pip install "$($PSScriptRoot)\Backend\Requirements\dlib-19.24.1-cp311-cp311-win_amd64.whl"

#install required Python packages
pip install -r "$($PSScriptRoot)\Backend\Requirements\python_requirements.txt"