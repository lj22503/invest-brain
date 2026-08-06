//! InvestBrain Tauri 主进程入口。
//!
//! Plan 1 任务 5：setup 阶段 spawn sidecar 子进程，写 SIDECAR_URL 给前端。

mod packs;

use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use tauri::Manager;

struct SidecarHandle(Mutex<Option<Child>>);

#[tauri::command]
async fn health_check() -> Result<serde_json::Value, String> {
    let sidecar_url = std::env::var("SIDECAR_URL")
        .unwrap_or_else(|_| "http://127.0.0.1:8765".to_string());
    let url = format!("{}/health", sidecar_url);

    let resp = reqwest::Client::new()
        .get(&url)
        .timeout(std::time::Duration::from_secs(3))
        .send()
        .await
        .map_err(|e| format!("sidecar unreachable: {}", e))?;

    if !resp.status().is_success() {
        return Err(format!("sidecar returned {}", resp.status()));
    }

    let body: serde_json::Value = resp.json().await
        .map_err(|e| format!("invalid JSON: {}", e))?;

    Ok(body)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // Plan 1 dev 模式：从相对路径跑 python src/server.py
            // release 时切到 packaged 二进制（Task 5+ 后续 Plan）
            let sidecar_path = std::path::Path::new("../sidecar/src/server.py");

            let child = Command::new("python")
                .arg(sidecar_path)
                .env("SIDECAR_PORT", "8765")
                .stdout(Stdio::piped())
                .stderr(Stdio::piped())
                .spawn()
                .expect("failed to spawn sidecar");

            // 保存子进程 handle 到 State（release 用 app.shell().sidecar()）
            app.manage(SidecarHandle(Mutex::new(Some(child))));

            // 写环境变量给 reqwest 调用方
            std::env::set_var("SIDECAR_URL", "http://127.0.0.1:8765");
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            health_check,
            packs::check_packs,
            packs::update_pack,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}