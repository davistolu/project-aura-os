use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum RoutingDecision {
    /// Bypasses AI inference entirely for deterministic system verbs
    Deterministic { command: String, args: Vec<String> },
    /// Local SLM for fast, offline, and private operations
    LocalSlm { model_name: String },
    /// Cloud LLM for complex coding or reasoning tasks
    CloudLlm { provider: String, model_name: String },
}

#[derive(Debug, Clone)]
pub struct ModelRouter {
    allow_cloud: bool,
    force_offline: bool,
}

impl Default for ModelRouter {
    fn default() -> Self {
        Self::new(true, false)
    }
}

impl ModelRouter {
    pub fn new(allow_cloud: bool, force_offline: bool) -> Self {
        Self {
            allow_cloud,
            force_offline,
        }
    }

    /// Evaluates input query to select the optimal execution path
    pub fn route(&self, input: &str) -> RoutingDecision {
        let trimmed = input.trim();
        let lower = trimmed.to_lowercase();

        // 1. Check for deterministic command triggers
        if lower.starts_with("open ") || lower.starts_with("launch ") {
            let app = trimmed[5..].trim().to_string();
            return RoutingDecision::Deterministic {
                command: "app_launch".to_string(),
                args: vec![app],
            };
        }

        if lower.starts_with("switch workspace ") || lower.starts_with("workspace ") {
            let parts: Vec<&str> = trimmed.split_whitespace().collect();
            let target = parts.last().unwrap_or(&"general").to_string();
            return RoutingDecision::Deterministic {
                command: "workspace_switch".to_string(),
                args: vec![target],
            };
        }

        if lower == "status" || lower == "doctor" || lower == "hardware" {
            return RoutingDecision::Deterministic {
                command: "sys_hardware_inspect".to_string(),
                args: vec![],
            };
        }

        // 2. Offline / Local fallback
        if self.force_offline || !self.allow_cloud {
            return RoutingDecision::LocalSlm {
                model_name: "llama3.2:3b".to_string(),
            };
        }

        // 3. Complex tasks route to cloud LLM if allowed
        if lower.contains("architect") || lower.contains("refactor") || lower.contains("explain") || lower.len() > 100 {
            RoutingDecision::CloudLlm {
                provider: "anthropic".to_string(),
                model_name: "claude-3-5-sonnet".to_string(),
            }
        } else {
            RoutingDecision::LocalSlm {
                model_name: "llama3.2:3b".to_string(),
            }
        }
    }
}
