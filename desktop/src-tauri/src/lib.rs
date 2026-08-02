//! InvestBrain Tauri 主进程入口。
//!
//! Plan 1 任务 4：暴露 health_check 命令，前端调用验证 sidecar 路径。

use serde::Serialize;

#[derive(Serialize)]
pub struct HealthResponse {
    pub status: String,
    pub version: String,
    pub python_version: String,
    pub sidecar_url: String,
}

/// 调用 sidecar `/health` 端点。
///
/// Plan 1 阶段：sidecar URL 通过 `SIDECAR_URL` 环境变量传入（手动启服务）。
/// 后续 Task 改 Tauri 启动时 spawn sidecar 并写入此 env。
#[tauri::command]
async fn health_check() -> Result<HealthResponse, String> {
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

    Ok(HealthResponse {
        status: body["status"].as_str().unwrap_or("unknown").to_string(),
        version: body["version"].as_str().unwrap_or("0.0.0").to_string(),
        python_version: body["python_version"].as_str().unwrap_or("").to_string(),
        sidecar_url,
    })
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![health_check])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
