# desktop/scripts/local-smoke.ps1
# Windows 等价脚本：build sidecar → spawn → health check → kill

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot\..

Write-Host "→ Building sidecar..."
bash sidecar/build_sidecar.sh

if (-not (Test-Path "sidecar/dist/sidecar.exe")) {
    throw "sidecar binary not found at sidecar/dist/sidecar.exe"
}

$port = if ($env:PORT) { $env:PORT } else { 8765 }
$env:SIDECAR_PORT = $port
$proc = Start-Process -FilePath ".\sidecar\dist\sidecar.exe" -PassThru
Start-Sleep -Seconds 1

try {
    Write-Host "→ Health check at http://127.0.0.1:$port/health"
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:$port/health"
    if ($resp.status -eq "ok") {
        Write-Host "✓ Sidecar healthy: $($resp | ConvertTo-Json -Compress)"
        exit 0
    } else {
        throw "Unexpected response: $($resp | ConvertTo-Json)"
    }
} finally {
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}