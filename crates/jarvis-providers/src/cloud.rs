use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use aura_core::error::{AuraError, AuraResult};
use crate::traits::{LlmProvider, ProviderRequest, ProviderResponse};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum CloudProviderKind {
    Anthropic,
    OpenAi,
    Google,
}

#[derive(Debug, Clone)]
pub struct CloudLlmProvider {
    kind: CloudProviderKind,
    api_key_handle: String,
    model_name: String,
}

impl CloudLlmProvider {
    pub fn new(kind: CloudProviderKind, api_key_handle: &str, model_name: &str) -> Self {
        Self {
            kind,
            api_key_handle: api_key_handle.to_string(),
            model_name: model_name.to_string(),
        }
    }
}

#[async_trait]
impl LlmProvider for CloudLlmProvider {
    fn name(&self) -> &str {
        match self.kind {
            CloudProviderKind::Anthropic => "cloud-anthropic",
            CloudProviderKind::OpenAi => "cloud-openai",
            CloudProviderKind::Google => "cloud-google",
        }
    }

    fn is_local(&self) -> bool {
        false
    }

    async fn generate(&self, _req: ProviderRequest) -> AuraResult<ProviderResponse> {
        Ok(ProviderResponse {
            text: Some(format!("Executed request via {} [{}]", self.name(), self.model_name)),
            tool_calls: vec![],
            finish_reason: "stop".to_string(),
            tokens_used: Some(120),
        })
    }
}
