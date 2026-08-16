//! InvestBrain Tauri 主进程入口。
//! [rebuild-tag 2026-08-14 强制重编译以嵌入最新前端资源]
//!
//! Plan 1 任务 5：setup 阶段 spawn sidecar 子进程，写 SIDECAR_URL 给前端。

mod packs;

use std::process::{Command, Stdio};
use std::sync::Mutex;
use tauri::Manager;

/// sidecar 子进程句柄：dev 为 python 进程，release 为打包的 sidecar 二进制进程。
enum SidecarChild {
    Std(std::process::Child),
    Shell(tauri_plugin_shell::process::CommandChild),
}

struct SidecarHandle(Mutex<Option<SidecarChild>>);

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
            // dev 模式：从相对路径跑 python src/server.py（依赖本机 python）
            // release 模式：使用打包进 bundle 的 sidecar 二进制（见 tauri.conf.json bundle.externalBin）
            #[cfg(debug_assertions)]
            {
                let sidecar_path = std::path::Path::new("../sidecar/src/server.py");
                // dev：数据目录统一指向项目根 data（与主项目 llm_router / memory store 一致）
                let dev_data_dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
                    .join("..").join("..").join("data");
                let child = Command::new("python")
                    .arg(sidecar_path)
                    .env("SIDECAR_PORT", "8765")
                    .env("INVESTBRAIN_DATA_DIR", &dev_data_dir)
                    .stdout(Stdio::piped())
                    .stderr(Stdio::piped())
                    .spawn()
                    .expect("failed to spawn python sidecar (dev)");
                app.manage(SidecarHandle(Mutex::new(Some(SidecarChild::Std(child)))));
            }

            #[cfg(not(debug_assertions))]
            {
                use tauri_plugin_shell::ShellExt;
                // release：数据目录落 %APPDATA%\InvestBrain\data（用户可见、规范位置）
                let appdata = std::env::var("APPDATA").unwrap_or_else(|_| String::new());
                let rel_data_dir = std::path::Path::new(&appdata)
                    .join("InvestBrain").join("data");
                let (mut rx, child) = app
                    .shell()
                    .sidecar("sidecar")
                    .expect("failed to resolve packaged sidecar binary")
                    .env("SIDECAR_PORT", "8765")
                    .env("INVESTBRAIN_DATA_DIR", &rel_data_dir)
                    .spawn()
                    .expect("failed to spawn packaged sidecar (release)");
                // 后台消费 sidecar 事件，避免 Receiver 阻塞进程句柄生命周期
                tauri::async_runtime::spawn(async move {
                    while let Some(event) = rx.recv().await {
                        match event {
                            tauri_plugin_shell::process::CommandEvent::Stdout(line) => {
                                eprintln!("[sidecar] {}", String::from_utf8_lossy(&line));
                            }
                            tauri_plugin_shell::process::CommandEvent::Stderr(line) => {
                                eprintln!("[sidecar:err] {}", String::from_utf8_lossy(&line));
                            }
                            _ => {}
                        }
                    }
                });
                app.manage(SidecarHandle(Mutex::new(Some(SidecarChild::Shell(child)))));
            }

            // 写环境变量给 reqwest 调用方
            std::env::set_var("SIDECAR_URL", "http://127.0.0.1:8765");
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            health_check,
            packs::check_packs,
            packs::update_pack,
            packs::get_pack_config,
            packs::set_pack_config,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}