<#
.SYNOPSIS
    一键配置 Invest-Brain 的 PushPlus 微信推送渠道（交互式引导，无需阅读文档）。

.DESCRIPTION
    本脚本会：
      1) 显示 PushPlus 获取 token 的步骤
      2) 提示你粘贴 token
      3) 校验 token 格式（非空、长度 >= 8）
      4) 写入 data/config/webhook.json 并启用 pushplus 渠道
      5) 调用 send_notification 发送一条测试消息验证链路
      6) 打印成功或失败原因

    使用方法（在 invest-brain 仓库根目录或任意位置运行均可）：
      powershell -ExecutionPolicy Bypass -File scripts/configure_pushplus.ps1

    注意：本脚本仅配置 pushplus 渠道，不会改动飞书/钉钉/Bark 等其他渠道，
    也不会提交 git、不会上传任何密钥。
#>

[CmdletBinding()]
param(
    [string]$Token = ""
)

$ErrorActionPreference = "Stop"
# 确保中文正常显示
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

# ---- 定位项目根目录（scripts/ 的上一级） ----
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$configPath = Join-Path $projectRoot "data\config\webhook.json"

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Invest-Brain 一键配置 PushPlus 微信推送" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "【PushPlus 是什么】" -ForegroundColor Yellow
Write-Host "  PushPlus 可以把消息推送到你的微信，无需安装额外 App，适合接收投资提醒。"
Write-Host ""
Write-Host "【如何获取 PushPlus token（约 2 分钟）】" -ForegroundColor Yellow
Write-Host "  1. 手机微信扫码关注公众号：https://www.pushplus.plus（也可直接访问该网址）"
Write-Host "  2. 登录后点击右上角『个人中心』"
Write-Host "  3. 页面上会显示你的 token（一长串字符），点击复制"
Write-Host "  4. 粘贴到下方提示符，回车即可"
Write-Host ""

# ---- 读取或初始化 token ----
if ([string]::IsNullOrWhiteSpace($Token)) {
    $Token = Read-Host "请粘贴你的 PushPlus token（不会显示在屏幕上以外的任何地方）"
}

$Token = $Token.Trim()
if ([string]::IsNullOrWhiteSpace($Token)) {
    Write-Host ""
    Write-Host "[失败] token 为空，无法配置。请重新运行本脚本并粘贴 token。" -ForegroundColor Red
    exit 1
}
if ($Token.Length -lt 8) {
    Write-Host ""
    Write-Host "[失败] token 长度不足（至少 8 位），请检查是否复制完整。" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host ("已收到 token（长度 {0} 位，前 4 位：{1}****）" -f $Token.Length, $Token.Substring(0, 4)) -ForegroundColor Green

# ---- 写入 webhook.json ----
Write-Host ""
Write-Host "正在写入配置 data/config/webhook.json ..." -ForegroundColor Yellow

# 读取现有配置，保留其他渠道；不存在则创建
$config = @{ channels = @{} }
if (Test-Path $configPath) {
    try {
        $raw = Get-Content -Path $configPath -Raw -Encoding UTF8
        if (-not [string]::IsNullOrWhiteSpace($raw)) {
            $existing = $raw | ConvertFrom-Json
            if ($null -ne $existing -and $null -ne $existing.channels) {
                # 转成 hashtable，避免 PSCustomObject 与哈希混用问题
                $config = @{ channels = @{} }
                foreach ($prop in $existing.channels.PSObject.Properties) {
                    $config.channels[$prop.Name] = $prop.Value
                }
            }
        }
    } catch {
        Write-Host "[警告] 读取现有 webhook.json 失败，将新建配置：$_" -ForegroundColor Yellow
    }
}

# 设置 pushplus 渠道
$config.channels["pushplus"] = [ordered]@{
    token    = $Token
    template = "html"
    enabled  = $true
}

# 使用 UTF-8 无 BOM 写回（Python json 读取兼容）
$jsonText = $config | ConvertTo-Json -Depth 10
$dir = Split-Path -Parent $configPath
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
[System.IO.File]::WriteAllText($configPath, $jsonText, (New-Object System.Text.UTF8Encoding($false)))

Write-Host "配置已写入：" -ForegroundColor Green
Write-Host "  - channel: pushplus" 
Write-Host "  - enabled: true"
Write-Host "  - token: $($Token.Substring(0,4))****（已隐藏）"
Write-Host "  - template: html"
Write-Host "  - 其他渠道保持不变"

# ---- 发送测试消息 ----
Write-Host ""
Write-Host "正在发送测试消息（需要联网，请稍候）..." -ForegroundColor Yellow

$python = "python"
$env:PYTHONIOENCODING = "utf-8"
$testCode = @"
import sys, os
sys.path.insert(0, os.path.join(r'$projectRoot', 'src', 'mcp_server'))
from notifier import send_notification
res = send_notification('Invest-Brain 配置成功！这是一条测试消息，你已经可以收到提醒推送了。', channel='pushplus')
print('RESULT_OK' if res.get('results', {}).get('pushplus') else 'RESULT_FAIL')
print('DETAIL: ' + str(res))
"@

$out = $null
$err = $null
try {
    $out = & $python -c $testCode 2>&1
} catch {
    $err = $_
}

$resultOk = ($out -join "`n") -match "RESULT_OK"
if ($resultOk) {
    Write-Host ""
    Write-Host "[成功] 测试消息已通过 PushPlus 发送！" -ForegroundColor Green
    Write-Host "  请打开微信查看是否收到『Invest-Brain 配置成功』的推送。"
    Write-Host "  之后你设置的价格/时间/PE 提醒触发时，都会推送到这个微信。"
    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host "  配置完成！你的 Invest-Brain 推送已生效。" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[失败] 测试消息未发送成功。" -ForegroundColor Red
    Write-Host "可能原因与解决办法：" -ForegroundColor Yellow
    Write-Host "  1. 网络不通 → 请检查网络后重试"
    Write-Host "  2. token 错误/被平台风控 → 请重新登录 https://www.pushplus.plus 复制最新 token"
    Write-Host "  3. 未关注 PushPlus 公众号 → 微信扫码关注后重试"
    Write-Host ""
    if ($err) { Write-Host "错误详情：$err" -ForegroundColor DarkYellow }
    Write-Host "输出详情：$($out -join "`n")" -ForegroundColor DarkYellow
    Write-Host ""
    Write-Host "[提示] 配置已写入 webhook.json，token 校验格式通过；若想换回飞书等渠道，" -ForegroundColor Yellow
    Write-Host "  请把 webhook.json 中对应渠道的 enabled 改为 true，或重新运行本脚本配置其他渠道。"
    exit 2
}
