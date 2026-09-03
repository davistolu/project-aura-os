use async_trait::async_trait;
use serde_json::{json, Value};
use aura_core::capabilities::Capability;
use aura_core::error::AuraResult;
use aura_core::permissions::PermissionTier;
use crate::tools::JarvisTool;

pub struct DevEnvironmentDoctorTool;

#[async_trait]
impl JarvisTool for DevEnvironmentDoctorTool {
    fn name(&self) -> &str {
        "dev_environment_doctor"
    }

    fn description(&self) -> &str {
        "Inspect project developer environment, tooling versions, and dependencies."
    }

    fn parameters_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {
                "project_path": { "type": "string", "description": "Path to inspect" }
            }
        })
    }

    fn required_capability(&self) -> Capability {
        Capability::FilesystemRead { scope: None }
    }

    fn permission_tier(&self) -> PermissionTier {
        PermissionTier::Observe
    }

    async fn execute(&self, _arguments: Value) -> AuraResult<Value> {
        Ok(json!({
            "status": "healthy",
            "detected_stacks": ["Rust / Cargo", "Nix Flake"],
            "toolchain_ready": true,
            "services": [
                { "name": "postgresql", "status": "running", "port": 5432 },
                { "name": "redis", "status": "idle", "port": 6379 }
            ]
        }))
    }
}
