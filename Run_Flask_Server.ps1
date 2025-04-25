Set-Location $($PSScriptRoot)

#Remove-Item -Path "$($PSScriptRoot)\flask_session" -Force -Recurse -ErrorAction SilentlyContinue

& python.exe "$($PSScriptRoot)\Backend\LoginApp\src\app.py"