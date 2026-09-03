use async_trait::async_trait;
use aura_core::error::AuraResult;
use crate::traits::{LlmProvider, ProviderRequest, ProviderResponse, ToolCallRequest};

#[derive(Debug, Clone, Default)]
pub struct MockLlmProvider {
    pub scripted_responses: Vec<ProviderResponse>,
}

impl MockLlmProvider {
    pub fn new() -> Self {
        Self {
            scripted_responses: Vec::new(),
        }
    }

    pub fn with_tool_call(tool_name: &str, args: serde_json::Value) -> Self {
        Self {
            scripted_responses: vec![ProviderResponse {
                text: None,
                tool_calls: vec![ToolCallRequest {
                    id: "call_001".to_string(),
                    tool_name: tool_name.to_string(),
                    arguments: args,
                }],
                finish_reason: "tool_calls".to_string(),
                tokens_used: Some(30),
            }],
        }
    }
}

#[async_trait]
impl LlmProvider for MockLlmProvider {
    fn name(&self) -> &str {
        "mock-provider"
    }

    fn is_local(&self) -> bool {
        true
    }

    async fn generate(&self, _req: ProviderRequest) -> AuraResult<ProviderResponse> {
        if let Some(resp) = self.scripted_responses.first() {
            Ok(resp.clone())
        } else {
            Ok(ProviderResponse {
                text: Some("Mock deterministic response".to_string()),
                tool_calls: vec![],
                finish_reason: "stop".to_string(),
                tokens_used: Some(10),
            })
        }
    }
}
