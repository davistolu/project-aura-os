use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum PermissionTier {
    /// Read-only observation of system state (CPU, processes, logs).
    Observe = 1,
    /// Model suggestion or plan requiring user interaction to execute.
    Suggest = 2,
    /// Automated safe operation (non-destructive, easily reversible, within project scope).
    ExecuteSafe = 3,
    /// High-risk or privileged operation (file deletion, kill process, package installation, shell exec).
    /// Requires explicit approval modal in UI unless user configured autonomous profile.
    ExecutePrivileged = 4,
    /// Continuous autonomous background task with pre-authorized boundaries.
    Autonomous = 5,
}

impl PermissionTier {
    pub fn requires_approval(&self, is_autonomous_mode: bool) -> bool {
        match self {
            PermissionTier::Observe | PermissionTier::ExecuteSafe => false,
            PermissionTier::Suggest => true,
            PermissionTier::ExecutePrivileged => !is_autonomous_mode,
            PermissionTier::Autonomous => false,
        }
    }
}
