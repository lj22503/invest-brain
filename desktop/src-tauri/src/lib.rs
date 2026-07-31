//! InvestBrain Tauri 主进程入口。
//!
//! Plan 1 任务 3 范围：仅 boot Tauri，无 sidecar，无命令。

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|_app| Ok(()))
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
