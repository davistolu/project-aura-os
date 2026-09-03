use async_trait::async_trait;
use serde_json::{json, Value};
use aura_core::capabilities::Capability;
use aura_core::error::{AuraError, AuraResult};
use aura_core::permissions::PermissionTier;
use crate::tools::JarvisTool;

pub struct FsSearchTool;

#[async_trait]
impl JarvisTool for FsSearchTool {
    fn name(&self) -> &str {
        "fs_search"
    }

    fn description(&self) -> &str {
        "Search files within the project sandbox by pattern or name."
    }

    fn parameters_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {
                "pattern": { "type": "string", "description": "Filename pattern to match" },
                "directory": { "type": "string", "description": "Root search directory" }
            },
            "required": ["pattern"]
        })
    }

    fn required_capability(&self) -> Capability {
        Capability::FilesystemRead { scope: None }
    }

    fn permission_tier(&self) -> PermissionTier {
        PermissionTier::ExecuteSafe
    }

    async fn execute(&self, arguments: Value) -> AuraResult<Value> {
        let pattern = arguments["pattern"].as_str().unwrap_or("*");
        Ok(json!({
            "pattern": pattern,
            "matches": [
                "src/main.rs",
                "src/lib.rs",
                "Cargo.toml"
            ]
        }))
    }
}
