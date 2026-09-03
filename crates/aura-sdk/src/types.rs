use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuraNotification {
    pub title: String,
    pub body: String,
    pub urgency: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuraSystemStatus {
    pub os_version: String,
    pub cpu_usage_percent: f32,
    pub memory_used_mb: u64,
    pub memory_total_mb: u64,
}
