//! 服务包本地调度：检查 / 下载 / 写入。
//!
//! Plan 3 范围：实现 PackManager 与 3 个 Tauri 命令。
//!
//! Plan 4 修正：直连 Vercel Blob（每 pack 一个 env var），不再走 Vercel Function proxy。

use std::path::PathBuf;
use serde::{Deserialize, Serialize};
use tauri::Manager;

const PACK_IDS: &[&str] = &["master_views", "industry_concepts"];

#[derive(Serialize, Deserialize, Debug, Clone, Default)]
pub struct RemoteVersions {
    #[serde(default)]
    pub master_views: String,
    #[serde(default)]
    pub industry_concepts: String,
}

impl RemoteVersions {
    fn zero() -> Self {
        Self {
            master_views: "0.0.0".into(),
            industry_concepts: "0.0.0".into(),
        }
    }
}

fn manifest_blob_url(pack_id: &str) -> Option<String> {
    match pack_id {
        "master_views" => std::env::var("PACK_MASTER_VIEWS_BLOB_URL").ok(),
        "industry_concepts" => std::env::var("PACK_INDUSTRY_CONCEPTS_BLOB_URL").ok(),
        _ => None,
    }
}

pub struct PackManager {
    user_data_dir: PathBuf,
}

impl PackManager {
    pub fn new(user_data_dir: PathBuf) -> Self {
        Self { user_data_dir }
    }

    fn packs_dir(&self) -> PathBuf {
        self.user_data_dir.join("data").join("packs")
    }

    /// 从每 pack 的 Vercel Blob manifest 直拉版本号。
    pub async fn fetch_remote_versions(&self) -> RemoteVersions {
        let mut out = RemoteVersions::zero();
        for id in PACK_IDS {
            let Some(url) = manifest_blob_url(id) else { continue };
            match reqwest::get(&url).await {
                Ok(resp) if resp.status().is_success() => {
                    if let Ok(m) = resp.json::<serde_json::Value>().await {
                        if let Some(v) = m.get("version").and_then(|x| x.as_str()) {
                            match *id {
                                "master_views" => out.master_views = v.to_string(),
                                "industry_concepts" => out.industry_concepts = v.to_string(),
                                _ => {}
                            }
                        }
                    }
                }
                _ => {}
            }
        }
        out
    }

    /// 读本地 manifest (或返回零版本).
    pub fn read_local_manifest(&self) -> RemoteVersions {
        let path = self.packs_dir().join("manifest.json");
        if !path.exists() {
            return RemoteVersions::zero();
        }
        match std::fs::read_to_string(&path) {
            Ok(s) => serde_json::from_str(&s).unwrap_or_else(|_| RemoteVersions::zero()),
            Err(_) => RemoteVersions::zero(),
        }
    }

    /// 拉一个 pack 的内容并写入本地。
    pub async fn download_pack(&self, pack_id: &str) -> Result<PathBuf, String> {
        let url = manifest_blob_url(pack_id)
            .ok_or_else(|| format!("pack {} has no blob URL env var", pack_id))?;
        let resp = reqwest::get(&url)
            .await
            .map_err(|e| format!("pack fetch fail: {}", e))?;
        if !resp.status().is_success() {
            return Err(format!("pack HTTP {}", resp.status()));
        }

        // 先读 JSON 拿 version，再写文件
        let body: serde_json::Value = resp.json().await
            .map_err(|e| format!("pack parse fail: {}", e))?;
        let version = body.get("version")
            .and_then(|x| x.as_str())
            .ok_or_else(|| "pack missing version field".to_string())?
            .to_string();

        let dir = self.packs_dir().join(pack_id);
        std::fs::create_dir_all(&dir).map_err(|e| format!("mkdir fail: {}", e))?;
        let file = dir.join("content.json");
        std::fs::write(&file, serde_json::to_string_pretty(&body).unwrap())
            .map_err(|e| format!("write fail: {}", e))?;

        // 更新本地 manifest
        self.update_local_manifest(pack_id, &version)?;
        Ok(file)
    }

    fn update_local_manifest(&self, pack_id: &str, version: &str) -> Result<(), String> {
        let path = self.packs_dir().join("manifest.json");
        let mut m = self.read_local_manifest();
        match pack_id {
            "master_views" => m.master_views = version.to_string(),
            "industry_concepts" => m.industry_concepts = version.to_string(),
            _ => return Err(format!("unknown pack_id {}", pack_id)),
        }
        std::fs::write(&path, serde_json::to_string_pretty(&m).unwrap())
            .map_err(|e| format!("manifest write fail: {}", e))?;
        Ok(())
    }
}

fn data_dir(app: &tauri::AppHandle) -> PathBuf {
    app.path()
        .app_data_dir()
        .unwrap_or_else(|_| PathBuf::from("."))
}

// ============ Tauri 命令 ============

#[tauri::command]
pub async fn check_packs(app: tauri::AppHandle) -> Result<serde_json::Value, String> {
    let mgr = PackManager::new(data_dir(&app));
    let remote = mgr.fetch_remote_versions().await;
    let local = mgr.read_local_manifest();

    let mut updates: Vec<serde_json::Value> = vec![];
    if remote.master_views != local.master_views && remote.master_views != "0.0.0" {
        updates.push(serde_json::json!({
            "pack_id": "master_views",
            "from": local.master_views,
            "to": remote.master_views,
        }));
    }
    if remote.industry_concepts != local.industry_concepts && remote.industry_concepts != "0.0.0" {
        updates.push(serde_json::json!({
            "pack_id": "industry_concepts",
            "from": local.industry_concepts,
            "to": remote.industry_concepts,
        }));
    }

    Ok(serde_json::json!({
        "remote": remote,
        "local": local,
        "updates_available": updates,
    }))
}

#[tauri::command]
pub async fn update_pack(
    app: tauri::AppHandle,
    pack_id: String,
) -> Result<String, String> {
    let mgr = PackManager::new(data_dir(&app));
    let path = mgr.download_pack(&pack_id).await?;
    Ok(path.to_string_lossy().to_string())
}