use async_trait::async_trait;
use serde_json::{json, Value};
use aura_core::capabilities::Capability;
use aura_core::error::AuraResult;
use aura_core::permissions::PermissionTier;
use aura_system::HardwareInspector;
use crate::tools::JarvisTool;

pub struct SysHardwareInspectTool;

#[async_trait]
impl JarvisTool for SysHardwareInspectTool {
    fn name(&self) -> &str {
        "sys_hardware_inspect"
    }

    fn description(&self) -> &str {
        "Inspect system CPU, RAM, GPU, thermals, and battery metrics."
    }

    fn parameters_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {}
        })
    }

    fn required_capability(&self) -> Capability {
        Capability::HardwareRead
    }

    fn permission_tier(&self) -> PermissionTier {
        PermissionTier::Observe
    }

    async fn execute(&self, _arguments: Value) -> AuraResult<Value> {
        let snapshot = HardwareInspector::inspect_snapshot();
        Ok(serde_json::to_value(snapshot)?)
    }
}
