# InvestBrain Release 流程

## 触发发布

```bash
git tag v0.1.0
git push origin v0.1.0
```

## GitHub Actions 自动跑

`.github/workflows/release.yml` 在推送 `v*.*.*` tag 后自动触发：

1. 装 Python + Rust + Node
2. `pip install -r src/mcp_server/requirements.txt pyinstaller`
3. `bash desktop/sidecar/build_sidecar.sh` — 编译 Python sidecar 单文件
4. `cd app && npm ci && npm run build:app` — Next.js 静态导出
5. `cargo tauri build --target x86_64-pc-windows-msvc --bundles msi` — 打包 MSI
6. `desktop/scripts/verify-msi.ps1` — 装 + 启 + 卸 冒烟
7. 上传 `.msi` 产物 + Create Draft Release

## 手动收尾

1. 打开 GitHub Releases 页面
2. 选刚生成的 draft release
3. **关键步骤**：把 `app/public/.well-known/releases.json` 的 URL 改成 GitHub Release 实际产物的文件名（Tauri 命名规则通常是 `InvestBrain_X.Y.Z_x64_en-US.msi`）
4. 把更新后的 `releases.json` commit 推上去，让 Vercel 重部署
5. publish release
6. 用户从 brain.mangofolio.com 看到新版本

## 不签名的代价

- 用户在 Windows 上装时看到 SmartScreen「未知发布者」警告
- 多点一次「更多信息 → 仍要运行」即可
- 详见 `~/.claude/projects/C--Users-lj225/memory/investbrain-code-signing-checklist.md`

## 已知限制（v0.x）

- 仅 Windows .msi（macOS / Linux 留 v1.2+）
- 不代码签名（Apple / Windows EV 证书留 v1.1）
- 无自动更新（手动下载新版，Tauri updater 留 v1.1）
- 单 tag 单产物（不发 beta / rc 等预发布）

## 故障排查

| 现象 | 排查 |
|---|---|
| CI cargo build 失败 | 检查 `desktop/src-tauri/Cargo.toml` 依赖版本 |
| verify-msi 找不到 exe | Tauri `bundle.targets` 是不是 `msi`，且 wix toolset 是否装 |
| /chat 加载失败 | `npm run build:app` 是否成功，`desktop/ui/chat/index.html` 是否存在 |
| Tauri 启动后窗口空白 | 检查 `desktop/ui/index.html` 是否存在（被 `frontendDist: ../ui` 指向） |
| Sidecar 没起 | `python` 在 PATH 中；`desktop/sidecar/dist/sidecar.exe` 是否生成 |