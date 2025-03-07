# Step 1: Launch Chrome with debugging enabled
Start-Process "chrome.exe" "--remote-debugging-port=9222 --user-data-dir=C:\Windows\Temp\ChromeDebug --new-window http://localhost:5173"
Write-Host "Log in using Chrome. Waiting for you to finish..."
Start-Sleep -Seconds 30  # Wait for manual login

# Step 2: Retrieve cookies using Chrome DevTools Protocol (CDP)
$chromeCookies = Invoke-RestMethod -Uri "http://127.0.0.1:9222/json" -Method Get
$debuggerUrl = ($chromeCookies | Where-Object { $_.type -eq "page" }).webSocketDebuggerUrl

if (-not $debuggerUrl) {
    Write-Host "Could not retrieve Chrome debugger URL. Ensure Chrome was launched with debugging enabled."
    Exit
}

# Step 3: Connect to Chrome DevTools Protocol
$sessionCookie = ""
$socket = New-Object System.Net.Sockets.TcpClient("127.0.0.1", 9222)
$stream = $socket.GetStream()
$writer = New-Object System.IO.StreamWriter($stream)
$reader = New-Object System.IO.StreamReader($stream)

# Send CDP Command to get all cookies
$command = @{ id = 1; method = "Network.getAllCookies"; params = @{} } | ConvertTo-Json -Compress
$writer.WriteLine($command)
$writer.Flush()
Start-Sleep -Seconds 1  # Allow time for response

# Read response
$response = $reader.ReadLine() | ConvertFrom-Json
if ($response.result.cookies) {
    foreach ($cookie in $response.result.cookies) {
        if ($cookie.name -eq "session") {
            $sessionCookie = "$($cookie.name)=$($cookie.value)"
            Write-Host "Extracted Session Cookie: $sessionCookie"
            Break
        }
    }
}

# Close the connection
$writer.Close()
$reader.Close()
$stream.Close()
$socket.Close()

# Step 4: Ensure session cookie exists
if (-not $sessionCookie) {
    Write-Host "Login failed or no session cookie retrieved. Exiting..."
    Exit
}

# Step 5: Call the permissions API
$headers = @{
    "Cookie" = $sessionCookie
}
$response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/permissions/check-user-permissions" -Method Get -Headers $headers

Write-Host "Received response: $response"

# Step 6: Check for permission
if ($response -match "Notepad Access") {
    Write-Host "Permission granted! Launching Notepad..."
    Start-Process "notepad.exe"
} else {
    Write-Host "Permission denied! Notepad will not open."
}