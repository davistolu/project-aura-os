use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum MemoryScope {
    Working,
    Session,
    Project { project_id: String },
    UserPreferences,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryEntry {
    pub key: String,
    pub value: serde_json::Value,
    pub timestamp_epoch_ms: u64,
}

#[derive(Debug, Clone)]
pub struct MemoryEngine {
    working: Arc<RwLock<HashMap<String, MemoryEntry>>>,
    session: Arc<RwLock<Vec<MemoryEntry>>>,
    project: Arc<RwLock<HashMap<String, HashMap<String, MemoryEntry>>>>,
    preferences: Arc<RwLock<HashMap<String, MemoryEntry>>>,
}

impl Default for MemoryEngine {
    fn default() -> Self {
        Self::new()
    }
}

impl MemoryEngine {
    pub fn new() -> Self {
        Self {
            working: Arc::new(RwLock::new(HashMap::new())),
            session: Arc::new(RwLock::new(Vec::new())),
            project: Arc::new(RwLock::new(HashMap::new())),
            preferences: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub fn set_working(&self, key: &str, value: serde_json::Value) {
        let mut map = self.working.write().unwrap();
        map.insert(key.to_string(), MemoryEntry {
            key: key.to_string(),
            value,
            timestamp_epoch_ms: current_time_ms(),
        });
    }

    pub fn clear_working(&self) {
        let mut map = self.working.write().unwrap();
        map.clear();
    }

    pub fn record_session(&self, summary: &str, data: serde_json::Value) {
        let mut vec = self.session.write().unwrap();
        vec.push(MemoryEntry {
            key: summary.to_string(),
            value: data,
            timestamp_epoch_ms: current_time_ms(),
        });
    }

    pub fn set_preference(&self, key: &str, value: serde_json::Value) {
        let mut map = self.preferences.write().unwrap();
        map.insert(key.to_string(), MemoryEntry {
            key: key.to_string(),
            value,
            timestamp_epoch_ms: current_time_ms(),
        });
    }

    pub fn get_preference(&self, key: &str) -> Option<serde_json::Value> {
        let map = self.preferences.read().unwrap();
        map.get(key).map(|e| e.value.clone())
    }

    pub fn reset_all_memories(&self) {
        self.working.write().unwrap().clear();
        self.session.write().unwrap().clear();
        self.project.write().unwrap().clear();
        self.preferences.write().unwrap().clear();
    }
}

fn current_time_ms() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}
