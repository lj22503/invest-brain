//! 服务包本地调度：检查 / 下载 / 写入。
//!
//! Plan 3 范围：实现 PackManager 与 3 个 Tauri 命令。

use std::path::PathBuf;
use serde::{Deserialize, Serialize};
use tauri::Manager;

const MANIFEST_URL: &str = "https://brain.mangofolio.com/api/packs/manifest.json";

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct PackVersion {
    pub pack_id: String,
    pub version: String,
    #[serde(default)]
    pub updated_at: String,
}

#[derive(Serialize, Deserialize, Debug, Clone, Default)]
pub struct RemoteManifest {
    #[serde(default)]
    pub master_views: String,
    #[serde(default)]
    pub industry_concepts: String,
}

impl RemoteManifest {
    fn zero() -> Self {
        Self {
            master_views: "0.0.0".into(),
            industry_concepts: "0.0.0".into(),
        }
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

    /// 从服务端拉 manifest。
    pub async fn fetch_remote_manifest(&self) -> Result<RemoteManifest, String> {
        let resp = reqwest::get(MANIFEST_URL)
            .await
            .map_err(|e| format!("manifest fetch fail: {}", e))?;
        let m: RemoteManifest = resp.json().await.unwrap_or_else(|_| RemoteManifest::zero());
        Ok(m)
    }

    /// 读本地 manifest (或返回零版本).
    pub fn read_local_manifest(&self) -> RemoteManifest {
        let path = self.packs_dir().join("manifest.json");
        if !path.exists() {
            return RemoteManifest::zero();
        }
        match std::fs::read_to_string(&path) {
            Ok(s) => serde_json::from_str(&s).unwrap_or_else(|_| RemoteManifest::zero()),
            Err(_) => RemoteManifest::zero(),
        }
    }

    /// 拉一个 pack 的内容并写入本地。
    pub async fn download_pack(&self, pack_id: &str, version: &str) -> Result<PathBuf, String> {
        let url = format!(
            "https://brain.mangofolio.com/api/packs/{}/{}.json",
            pack_id, version
        );
        let resp = reqwest::get(&url)
            .await
            .map_err(|e| format!("pack fetch fail: {}", e))?;
        if !resp.status().is_success() {
            return Err(format!("pack HTTP {}", resp.status()));
        }
        let bytes = resp.bytes()
            .await
            .map_err(|e| format!("pack bytes fail: {}", e))?;

        let dir = self.packs_dir().join(pack_id);
        std::fs::create_dir_all(&dir).map_err(|e| format!("mkdir fail: {}", e))?;
        let file = dir.join("content.json");
        std::fs::write(&file, &bytes).map_err(|e| format!("write fail: {}", e))?;

        // 更新本地 manifest
        self.update_local_manifest(pack_id, version)?;
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
    let remote = mgr.fetch_remote_manifest().await?;
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
    let remote = mgr.fetch_remote_manifest().await?;
    let version = match pack_id.as_str() {
        "master_views" => &remote.master_views,
        "industry_concepts" => &remote.industry_concepts,
        _ => return Err(format!("unknown pack_id {}", pack_id)),
    };

    let path = mgr.download_pack(&pack_id, version).await?;
    Ok(path.to_string_lossy().to_string())
}