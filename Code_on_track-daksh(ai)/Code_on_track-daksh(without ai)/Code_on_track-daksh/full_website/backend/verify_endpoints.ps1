$urls = @(
    "http://localhost:8000/items",
    "http://localhost:8000/vendors"
)

foreach ($url in $urls) {
    Write-Host "Checking $url ..."
    try {
        $response = Invoke-WebRequest -Uri $url -Method Get -ErrorAction Stop
        Write-Host "Status: $($response.StatusCode)"
        Write-Host "Content: $($response.Content.Substring(0, [math]::Min(100, $response.Content.Length)))"
    }
    catch {
        $e = $_.Exception.Response
        if ($e) {
            Write-Host "Status: $($e.StatusCode)"
            # 401 is GOOD (means matched route but needs auth, so server is up and router is valid)
            if ($e.StatusCode -ne [System.Net.HttpStatusCode]::Unauthorized) {
                Write-Host "Error Details: $($e.StatusDescription)"
            }
        }
        else {
            Write-Host "Error: $($_.Exception.Message)"
        }
    }
    Write-Host "----------------"
}
