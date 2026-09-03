pub mod hardware;
pub mod process;
pub mod filesystem;
pub mod workspace;
pub mod dev;
pub mod notification;

use std::collections::HashMap;
use std::sync::Arc;
use async_trait::async_trait;
use serde_json::Value;

use aura_core::capabilities::Capability;
use aura_core::error::AuraResult;
use aura_core::permissions::PermissionTier;
use jarvis_providers::traits::ToolDefinition;

#[async_trait]
pub trait JarvisTool: Send + Sync {
    fn name(&self) -> &str;
    fn description(&self) -> &str;
    fn parameters_schema(&self) -> Value;
    fn required_capability(&self) -> Capability;
    fn permission_tier(&self) -> PermissionTier;
    async fn execute(&self, arguments: Value) -> AuraResult<Value>;

    fn definition(&self) -> ToolDefinition {
        ToolDefinition {
            name: self.name().to_string(),
            description: self.description().to_string(),
            parameters_schema: self.parameters_schema(),
        }
    }
}

#[derive(Default, Clone)]
pub struct ToolRegistry {
    tools: HashMap<String, Arc<dyn JarvisTool>>,
}

impl ToolRegistry {
    pub fn new() -> Self {
        Self {
            tools: HashMap::new(),
        }
    }

    pub fn register(&mut self, tool: Arc<dyn JarvisTool>) {
        self.tools.insert(tool.name().to_string(), tool);
    }

    pub fn get(&self, name: &str) -> Option<Arc<dyn JarvisTool>> {
        self.tools.get(name).cloned()
    }

    pub fn list_definitions(&self) -> Vec<ToolDefinition> {
        self.tools.values().map(|t| t.definition()).collect()
    }
}
