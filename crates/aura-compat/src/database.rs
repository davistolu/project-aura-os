use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RuntimeTier {
    ProtonDirect,
    WineStaging,
    KvmVmFallback,
    Unsupported,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompatEntry {
    pub app_id: String,
    pub title: String,
    pub recommended_tier: RuntimeTier,
    pub required_dependencies: Vec<String>,
    pub dxvk_enabled: bool,
    pub vkd3d_enabled: bool,
    pub gamescope_args: Option<String>,
    pub tested_version: String,
}

pub struct CompatibilityDatabase {
    entries: HashMap<String, CompatEntry>,
}

impl Default for CompatibilityDatabase {
    fn default() -> Self {
        Self::new()
    }
}

impl CompatibilityDatabase {
    pub fn new() -> Self {
        let mut map = HashMap::new();
        map.insert(
            "notepadplusplus".to_string(),
            CompatEntry {
                app_id: "notepadplusplus".to_string(),
                title: "Notepad++".to_string(),
                recommended_tier: RuntimeTier::WineStaging,
                required_dependencies: vec![],
                dxvk_enabled: false,
                vkd3d_enabled: false,
                gamescope_args: None,
                tested_version: "8.6.4".to_string(),
            },
        );
        map.insert(
            "cyberpunk2077".to_string(),
            CompatEntry {
                app_id: "cyberpunk2077".to_string(),
                title: "Cyberpunk 2077".to_string(),
                recommended_tier: RuntimeTier::ProtonDirect,
                required_dependencies: vec!["vcrun2022".to_string()],
                dxvk_enabled: true,
                vkd3d_enabled: true,
                gamescope_args: Some("-W 2560 -H 1440 -r 144 --fsr".to_string()),
                tested_version: "2.12".to_string(),
            },
        );
        map.insert(
            "anticheat_proprietary_app".to_string(),
            CompatEntry {
                app_id: "anticheat_proprietary_app".to_string(),
                title: "Kernel-Level Anti-Cheat Software".to_string(),
                recommended_tier: RuntimeTier::KvmVmFallback,
                required_dependencies: vec![],
                dxvk_enabled: false,
                vkd3d_enabled: false,
                gamescope_args: None,
                tested_version: "1.0".to_string(),
            },
        );

        Self { entries: map }
    }

    pub fn lookup(&self, app_id: &str) -> Option<&CompatEntry> {
        self.entries.get(app_id)
    }
}
