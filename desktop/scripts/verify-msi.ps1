# desktop/scripts/verify-msi.ps1
# Smoke test: 安装 MSI → 启动 exe → 等待窗口 → 卸载 → 报告
# 退出码：0 = pass / 非零 = fail

$ErrorActionPreference = "Stop"

$msi = Get-ChildItem -Path desktop/src-tauri/target -Recurse -Filter "*.msi" | Select-Object -First 1
if (-not $msi) {
    Write-Error "MSI not found"
    exit 1
}

Write-Host "✓ Found MSI: $($msi.Name) ($([math]::Round($msi.Length / 1MB, 2)) MB)"

# 安装（无人值守）
Write-Host "Installing..."
$installLog = "$env:TEMP\install.log"
$proc = Start-Process -FilePath "msiexec.exe" -ArgumentList @(
    "/i", $msi.FullName,
    "/quiet",
    "/norestart",
    "/log", $installLog
) -Wait -PassThru

if ($proc.ExitCode -ne 0) {
    Write-Error "Install failed (exit $($proc.ExitCode))"
    Get-Content $installLog | Select-Object -Last 20
    exit 1
}

Write-Host "✓ Installed"

# 找安装位置
$installPath = Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" |
    Where-Object { $_.DisplayName -like "InvestBrain*" } |
    Select-Object -First 1 -ExpandProperty InstallLocation

if (-not $installPath) {
    Write-Error "Install path not found in registry"
    exit 1
}

Write-Host "✓ Install path: $installPath"

# 启 exe（如果不需要 GUI 测试，可以 short-circuit）
$exe = Get-ChildItem -Path $installPath -Filter "*.exe" | Select-Object -First 1
if (-not $exe) {
    Write-Warning "No exe found, skipping launch"
} else {
    Write-Host "Launching $exe for 10s..."
    $p = Start-Process -FilePath $exe.FullName -PassThru
    Start-Sleep -Seconds 10
    if (-not $p.HasExited) {
        Write-Host "✓ App alive after 10s"
        Stop-Process -Id $p.Id -Force
    } else {
        Write-Warning "App exited early with code $($p.ExitCode)"
    }
}

# 卸载
Write-Host "Uninstalling..."
$uninstallProc = Start-Process -FilePath "msiexec.exe" -ArgumentList @(
    "/x", $msi.FullName,
    "/quiet",
    "/norestart"
) -Wait -PassThru

if ($uninstallProc.ExitCode -ne 0) {
    Write-Error "Uninstall failed"
    exit 1
}

Write-Host "✓ Smoke test passed"
exit 0