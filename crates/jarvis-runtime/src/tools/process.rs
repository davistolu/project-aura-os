use async_trait::async_trait;
use serde_json::{json, Value};
use aura_core::capabilities::Capability;
use aura_core::error::AuraResult;
use aura_core::permissions::PermissionTier;
use crate::tools::JarvisTool;

pub struct SysProcessInspectTool;

#[async_trait]
impl JarvisTool for SysProcessInspectTool {
    fn name(&self) -> &str {
        "sys_process_inspect"
    }

    fn description(&self) -> &str {
        "Inspect running processes and their resource consumption."
    }

    fn parameters_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {
                "filter": { "type": "string", "description": "Optional name filter" }
            }
        })
    }

    fn required_capability(&self) -> Capability {
        Capability::ProcessList
    }

    fn permission_tier(&self) -> PermissionTier {
        PermissionTier::Observe
    }

    async fn execute(&self, _arguments: Value) -> AuraResult<Value> {
        Ok(json!([
            { "pid": 1, "name": "systemd", "cpu_percent": 0.0, "memory_mb": 14.2 },
            { "pid": 420, "name": "aura-shell", "cpu_percent": 0.2, "memory_mb": 42.0 },
            { "pid": 850, "name": "jarvisd", "cpu_percent": 0.1, "memory_mb": 65.5 },
            { "pid": 1204, "name": "pipewire", "cpu_percent": 0.1, "memory_mb": 12.0 }
        ]))
    }
}
