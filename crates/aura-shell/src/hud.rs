use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HudState {
    pub active_workspace: String,
    pub cpu_load: f32,
    pub ram_used_percent: f32,
    pub battery_percent: Option<u8>,
    pub jarvis_status: String,
    pub notifications_unread: usize,
}

impl HudState {
    pub fn current() -> Self {
        Self {
            active_workspace: "dev".to_string(),
            cpu_load: 3.8,
            ram_used_percent: 18.7,
            battery_percent: Some(95),
            jarvis_status: "ready".to_string(),
            notifications_unread: 0,
        }
    }
}
