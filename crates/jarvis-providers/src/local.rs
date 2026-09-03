use async_trait::async_trait;
use aura_core::error::{AuraError, AuraResult};
use crate::traits::{LlmProvider, ProviderRequest, ProviderResponse};

#[derive(Debug, Clone)]
pub struct LocalLlmProvider {
    endpoint: String,
    model_name: String,
}

impl LocalLlmProvider {
    pub fn new(endpoint: &str, model_name: &str) -> Self {
        Self {
            endpoint: endpoint.to_string(),
            model_name: model_name.to_string(),
        }
    }

    pub fn default_ollama() -> Self {
        Self::new("http://localhost:11434", "llama3.2:3b")
    }
}

#[async_trait]
impl LlmProvider for LocalLlmProvider {
    fn name(&self) -> &str {
        "local-ollama"
    }

    fn is_local(&self) -> bool {
        true
    }

    async fn generate(&self, _req: ProviderRequest) -> AuraResult<ProviderResponse> {
        // High-level integration point for local llama.cpp / Ollama socket
        Ok(ProviderResponse {
            text: Some("System inspection completed locally.".to_string()),
            tool_calls: vec![],
            finish_reason: "stop".to_string(),
            tokens_used: Some(42),
        })
    }
}
