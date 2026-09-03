use serde::{Deserialize, Serialize};
use std::sync::{Arc, RwLock};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PowerProfile {
    PowerSaver,
    Balanced,
    Performance,
    GamingExtreme,
}

#[derive(Debug, Clone)]
pub struct PowerManager {
    current_profile: Arc<RwLock<PowerProfile>>,
}

impl Default for PowerManager {
    fn default() -> Self {
        Self::new()
    }
}

impl PowerManager {
    pub fn new() -> Self {
        Self {
            current_profile: Arc::new(RwLock::new(PowerProfile::Balanced)),
        }
    }

    pub fn get_profile(&self) -> PowerProfile {
        self.current_profile.read().unwrap().clone()
    }

    pub fn set_profile(&self, profile: PowerProfile) {
        let mut p = self.current_profile.write().unwrap();
        *p = profile;
    }
}
