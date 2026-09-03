use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::{Path, PathBuf};
use uuid::Uuid;

use crate::capabilities::Capability;
use crate::error::AuraResult;
use crate::permissions::PermissionTier;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AuditDecision {
    Allowed,
    Denied { reason: String },
    ApprovalRequested,
    ApprovedByUser,
    RejectedByUser,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditEvent {
    pub id: Uuid,
    pub timestamp: DateTime<Utc>,
    pub task_id: Uuid,
    pub agent: String,
    pub capability: Capability,
    pub permission_tier: PermissionTier,
    pub tool_name: String,
    pub arguments_redacted: serde_json::Value,
    pub decision: AuditDecision,
    pub execution_duration_ms: Option<u64>,
    pub error: Option<String>,
}

#[derive(Debug, Clone)]
pub struct AuditLogger {
    log_path: PathBuf,
}

impl AuditLogger {
    pub fn new<P: AsRef<Path>>(log_dir: P) -> Self {
        let path = log_dir.as_ref().join("audit.jsonl");
        Self { log_path: path }
    }

    pub fn fallback() -> Self {
        let path = std::env::temp_dir().join("aura_audit.jsonl");
        Self { log_path: path }
    }

    pub fn log_event(&self, event: &AuditEvent) -> AuraResult<()> {
        if let Some(parent) = self.log_path.parent() {
            let _ = std::fs::create_dir_all(parent);
        }
        let serialized = serde_json::to_string(event)?;
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.log_path)?;
        writeln!(file, "{}", serialized)?;
        Ok(())
    }

    pub fn path(&self) -> &Path {
        &self.log_path
    }
}
