Write-Host "Please wait - Generating website files..."

Set-Location "$($PSScriptRoot)\Frontend\FaceGuard_Dashboard"

& npm run build

Write-Host "`nGenerating web.config file (so IIS can handle React redirects and navigation)..."

# Define the web.config content
$webConfigContent = @"
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="React Routes" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/index.html" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
"@

# Create the web.config file
Set-Content -Path "$($PSScriptRoot)\Frontend\FaceGuard_Dashboard\dist\web.config" -Value $webConfigContent -Encoding UTF8 -Force

Write-Host "web.config generated at: $($PSScriptRoot)\Frontend\FaceGuard_Dashboard\dist\web.config" -ForegroundColor Green

Set-Location "$($PSScriptRoot)"

if($LASTEXITCODE -eq 0)
{
    Write-Host "`nScript complete. If successful, make sure IIS website is pointed to [$($PSScriptRoot)\Frontend\FaceGuard_Dashboard\dist] to host the website!" -ForegroundColor Green
}
else
{
    Write-Host "`nScript complete. If successful, make sure IIS website is pointed to [$($PSScriptRoot)\Frontend\FaceGuard_Dashboard\dist] to host the website!"
}