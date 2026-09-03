use std::sync::Arc;
use async_trait::async_trait;
use serde_json::{json, Value};
use aura_core::capabilities::Capability;
use aura_core::error::AuraResult;
use aura_core::permissions::PermissionTier;
use aura_system::WorkspaceManager;
use crate::tools::JarvisTool;

pub struct WorkspaceSwitchTool {
    manager: Arc<WorkspaceManager>,
}

impl WorkspaceSwitchTool {
    pub fn new(manager: Arc<WorkspaceManager>) -> Self {
        Self { manager }
    }
}

#[async_trait]
impl JarvisTool for WorkspaceSwitchTool {
    fn name(&self) -> &str {
        "workspace_switch"
    }

    fn description(&self) -> &str {
        "Switch active desktop workspace profile (general, dev, gaming, creative, ai)."
    }

    fn parameters_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {
                "workspace_id": { "type": "string", "description": "ID of workspace (general, dev, gaming)" }
            },
            "required": ["workspace_id"]
        })
    }

    fn required_capability(&self) -> Capability {
        Capability::WorkspaceManage
    }

    fn permission_tier(&self) -> PermissionTier {
        PermissionTier::ExecuteSafe
    }

    async fn execute(&self, arguments: Value) -> AuraResult<Value> {
        let id = arguments["workspace_id"].as_str().unwrap_or("dev");
        let profile = self.manager.switch_workspace(id)?;
        Ok(serde_json::to_value(profile)?)
    }
}
