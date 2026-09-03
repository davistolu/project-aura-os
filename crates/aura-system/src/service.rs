use std::sync::Arc;
use aura_core::error::AuraResult;
use crate::hardware::{HardwareInspector, HardwareSnapshot};
use crate::power::PowerManager;
use crate::workspaces::WorkspaceManager;

#[derive(Debug, Clone)]
pub struct SystemDaemon {
    pub workspace_manager: Arc<WorkspaceManager>,
    pub power_manager: Arc<PowerManager>,
}

impl Default for SystemDaemon {
    fn default() -> Self {
        Self::new()
    }
}

impl SystemDaemon {
    pub fn new() -> Self {
        Self {
            workspace_manager: Arc::new(WorkspaceManager::new()),
            power_manager: Arc::new(PowerManager::new()),
        }
    }

    pub fn inspect_hardware(&self) -> HardwareSnapshot {
        HardwareInspector::inspect_snapshot()
    }

    pub fn switch_workspace(&self, id: &str) -> AuraResult<crate::workspaces::WorkspaceProfile> {
        self.workspace_manager.switch_workspace(id)
    }
}
