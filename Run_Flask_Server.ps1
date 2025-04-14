Set-Location $($PSScriptRoot)

Remove-Item -Path "$($PSScriptRoot)\flask_session" -Force -Recurse

& python3.exe "$($PSScriptRoot)\Backend\LoginApp\src\app.py"