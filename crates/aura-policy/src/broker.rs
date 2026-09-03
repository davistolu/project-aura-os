use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use aura_core::error::{AuraError, AuraResult};

#[derive(Debug, Clone)]
pub struct SecretBroker {
    vault: Arc<RwLock<HashMap<String, String>>>,
}

impl Default for SecretBroker {
    fn default() -> Self {
        Self::new()
    }
}

impl SecretBroker {
    pub fn new() -> Self {
        Self {
            vault: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Register a credential handle
    pub fn store_secret(&self, key: &str, value: &str) {
        let mut map = self.vault.write().unwrap();
        map.insert(key.to_string(), value.to_string());
    }

    /// Resolve a secret for internal authorized execution
    pub fn resolve_secret(&self, key: &str) -> AuraResult<String> {
        let map = self.vault.read().unwrap();
        map.get(key)
            .cloned()
            .ok_or_else(|| AuraError::PolicyViolation(format!("Secret key '{}' not found in broker", key)))
    }

    /// Scan text (prompts, tool args) to ensure no plaintext registered secrets are leaked
    pub fn scan_for_leaks(&self, content: &str) -> AuraResult<()> {
        let map = self.vault.read().unwrap();
        for (name, secret) in map.iter() {
            if !secret.is_empty() && secret.len() >= 8 && content.contains(secret) {
                return Err(AuraError::SecretLeakDetected(format!(
                    "Plaintext credential for handle '{}' found in payload",
                    name
                )));
            }
        }
        Ok(())
    }

    /// Redact any known secrets from strings (e.g. for audit logs)
    pub fn redact(&self, mut content: String) -> String {
        let map = self.vault.read().unwrap();
        for (name, secret) in map.iter() {
            if !secret.is_empty() && secret.len() >= 8 {
                let mask = format!("[REDACTED_SECRET:{}]", name);
                content = content.replace(secret, &mask);
            }
        }
        content
    }
}
