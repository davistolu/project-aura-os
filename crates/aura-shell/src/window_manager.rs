use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use aura_core::error::{AuraError, AuraResult};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WindowInfo {
    pub id: u32,
    pub title: String,
    pub app_class: String,
    pub workspace_id: String,
    pub is_focused: bool,
    pub is_fullscreen: bool,
}

#[derive(Debug, Clone, Default)]
pub struct WindowManager {
    windows: Arc<RwLock<HashMap<u32, WindowInfo>>>,
}

impl WindowManager {
    pub fn new() -> Self {
        let mut map = HashMap::new();
        map.insert(
            101,
            WindowInfo {
                id: 101,
                title: "Alacritty - Terminal".to_string(),
                app_class: "Alacritty".to_string(),
                workspace_id: "dev".to_string(),
                is_focused: true,
                is_fullscreen: false,
            },
        );
        map.insert(
            102,
            WindowInfo {
                id: 102,
                title: "Visual Studio Code - AURA OS".to_string(),
                app_class: "Code".to_string(),
                workspace_id: "dev".to_string(),
                is_focused: false,
                is_fullscreen: false,
            },
        );

        Self {
            windows: Arc::new(RwLock::new(map)),
        }
    }

    pub fn list_windows(&self) -> Vec<WindowInfo> {
        self.windows.read().unwrap().values().cloned().collect()
    }

    pub fn focus_window(&self, id: u32) -> AuraResult<()> {
        let mut map = self.windows.write().unwrap();
        if let Some(target) = map.get_mut(&id) {
            for (_, win) in map.iter_mut() {
                win.is_focused = false;
            }
            target.is_focused = true;
            Ok(())
        } else {
            Err(AuraError::System(format!("Window ID {} not found", id)))
        }
    }
}
