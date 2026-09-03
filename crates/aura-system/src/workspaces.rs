use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use aura_core::error::{AuraError, AuraResult};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum WorkspaceType {
    General,
    Development,
    Gaming,
    Creative,
    Ai,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkspaceProfile {
    pub id: String,
    pub name: String,
    pub workspace_type: WorkspaceType,
    pub active_windows: Vec<String>,
    pub layout: String,
    pub suppress_notifications: bool,
    pub power_mode: String,
}

#[derive(Debug, Clone)]
pub struct WorkspaceManager {
    workspaces: Arc<RwLock<HashMap<String, WorkspaceProfile>>>,
    active_workspace_id: Arc<RwLock<String>>,
}

impl Default for WorkspaceManager {
    fn default() -> Self {
        Self::new()
    }
}

impl WorkspaceManager {
    pub fn new() -> Self {
        let mut map = HashMap::new();
        map.insert(
            "general".to_string(),
            WorkspaceProfile {
                id: "general".to_string(),
                name: "General Work".to_string(),
                workspace_type: WorkspaceType::General,
                active_windows: vec!["browser".to_string(), "terminal".to_string()],
                layout: "tiled-balanced".to_string(),
                suppress_notifications: false,
                power_mode: "balanced".to_string(),
            },
        );
        map.insert(
            "dev".to_string(),
            WorkspaceProfile {
                id: "dev".to_string(),
                name: "Development Studio".to_string(),
                workspace_type: WorkspaceType::Development,
                active_windows: vec!["editor".to_string(), "terminal".to_string(), "monitor".to_string()],
                layout: "side-by-side-3".to_string(),
                suppress_notifications: false,
                power_mode: "performance".to_string(),
            },
        );
        map.insert(
            "gaming".to_string(),
            WorkspaceProfile {
                id: "gaming".to_string(),
                name: "Gaming Mode".to_string(),
                workspace_type: WorkspaceType::Gaming,
                active_windows: vec!["gamescope".to_string()],
                layout: "fullscreen-exclusive".to_string(),
                suppress_notifications: true,
                power_mode: "performance-extreme".to_string(),
            },
        );

        Self {
            workspaces: Arc::new(RwLock::new(map)),
            active_workspace_id: Arc::new(RwLock::new("dev".to_string())),
        }
    }

    pub fn list_workspaces(&self) -> Vec<WorkspaceProfile> {
        self.workspaces.read().unwrap().values().cloned().collect()
    }

    pub fn get_active_workspace(&self) -> WorkspaceProfile {
        let active_id = self.active_workspace_id.read().unwrap();
        let map = self.workspaces.read().unwrap();
        map.get(&*active_id).cloned().unwrap_or_else(|| WorkspaceProfile {
            id: "default".to_string(),
            name: "Default".to_string(),
            workspace_type: WorkspaceType::General,
            active_windows: vec![],
            layout: "single".to_string(),
            suppress_notifications: false,
            power_mode: "balanced".to_string(),
        })
    }

    pub fn switch_workspace(&self, id: &str) -> AuraResult<WorkspaceProfile> {
        let map = self.workspaces.read().unwrap();
        if let Some(profile) = map.get(id) {
            let mut active = self.active_workspace_id.write().unwrap();
            *active = id.to_string();
            Ok(profile.clone())
        } else {
            Err(AuraError::System(format!("Workspace '{}' not found", id)))
        }
    }
}
