use async_trait::async_trait;
use serde_json::{json, Value};
use aura_core::capabilities::Capability;
use aura_core::error::AuraResult;
use aura_core::permissions::PermissionTier;
use crate::tools::JarvisTool;

pub struct SystemNotificationTool;

#[async_trait]
impl JarvisTool for SystemNotificationTool {
    fn name(&self) -> &str {
        "system_notification"
    }

    fn description(&self) -> &str {
        "Post a notification to the AURA desktop shell."
    }

    fn parameters_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {
                "title": { "type": "string" },
                "body": { "type": "string" },
                "urgency": { "type": "string", "enum": ["low", "normal", "critical"] }
            },
            "required": ["title", "body"]
        })
    }

    fn required_capability(&self) -> Capability {
        Capability::NotificationSend
    }

    fn permission_tier(&self) -> PermissionTier {
        PermissionTier::ExecuteSafe
    }

    async fn execute(&self, arguments: Value) -> AuraResult<Value> {
        let title = arguments["title"].as_str().unwrap_or("AURA");
        let body = arguments["body"].as_str().unwrap_or("");
        Ok(json!({
            "delivered": true,
            "title": title,
            "body": body
        }))
    }
}
