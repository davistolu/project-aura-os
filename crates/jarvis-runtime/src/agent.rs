use std::sync::Arc;
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use aura_core::error::{AuraError, AuraResult};
use aura_policy::PolicyEngine;
use jarvis_providers::traits::{LlmProvider, Message, ProviderRequest};
use crate::memory::MemoryEngine;
use crate::tools::ToolRegistry;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentTaskResult {
    pub task_id: Uuid,
    pub success: bool,
    pub final_response: String,
    pub steps_executed: usize,
    pub tool_executions: Vec<String>,
}

pub struct JarvisAgent {
    name: String,
    provider: Arc<dyn LlmProvider>,
    tools: ToolRegistry,
    policy: PolicyEngine,
    memory: Arc<MemoryEngine>,
    max_steps: usize,
}

impl JarvisAgent {
    pub fn new(
        name: &str,
        provider: Arc<dyn LlmProvider>,
        tools: ToolRegistry,
        policy: PolicyEngine,
        memory: Arc<MemoryEngine>,
    ) -> Self {
        Self {
            name: name.to_string(),
            provider,
            tools,
            policy,
            memory,
            max_steps: 10,
        }
    }

    /// Executes the bounded agent loop: Observe -> Plan -> Authorize -> Execute -> Verify -> Report
    pub async fn run_task(&self, prompt: &str) -> AuraResult<AgentTaskResult> {
        let task_id = Uuid::new_v4();
        let mut steps_executed = 0;
        let mut executed_tools = Vec::new();
        let mut conversation = vec![
            Message {
                role: "user".to_string(),
                content: prompt.to_string(),
            }
        ];

        let system_prompt = "You are JARVIS, an OS-native AI runtime for PROJECT AURA. \
            Assist the user safely using permissioned tools. Never attempt to bypass authorization.";

        while steps_executed < self.max_steps {
            steps_executed += 1;

            // 1. Observe & Plan: Query Model with available tools
            let req = ProviderRequest {
                system_prompt: system_prompt.to_string(),
                messages: conversation.clone(),
                tools: self.tools.list_definitions(),
                temperature: Some(0.2),
                max_tokens: Some(1024),
            };

            let response = self.provider.generate(req).await?;

            // If model returned pure text response with no tool calls, task is complete
            if response.tool_calls.is_empty() {
                let final_text = response.text.unwrap_or_else(|| "Task completed successfully.".to_string());
                self.memory.record_session(prompt, serde_json::json!({ "result": &final_text }));
                
                return Ok(AgentTaskResult {
                    task_id,
                    success: true,
                    final_response: final_text,
                    steps_executed,
                    tool_executions: executed_tools,
                });
            }

            // 2. Authorize & Execute tool calls
            for call in response.tool_calls {
                let tool = self.tools.get(&call.tool_name).ok_or_else(|| {
                    AuraError::ToolExecutionFailed(format!("Tool '{}' not registered", call.tool_name))
                })?;

                // Check policy & capabilities
                self.policy.authorize_execution(
                    task_id,
                    &self.name,
                    tool.name(),
                    &tool.required_capability(),
                    tool.permission_tier(),
                    &call.arguments,
                )?;

                // Execute authorized tool
                let tool_result = tool.execute(call.arguments.clone()).await?;
                executed_tools.push(tool.name().to_string());

                // Feed observation back into conversation loop
                conversation.push(Message {
                    role: "assistant".to_string(),
                    content: format!("Called tool {}", tool.name()),
                });
                conversation.push(Message {
                    role: "system".to_string(),
                    content: format!("Tool result: {}", tool_result),
                });
            }
        }

        Ok(AgentTaskResult {
            task_id,
            success: true,
            final_response: "Agent task finished bounded iteration limit.".to_string(),
            steps_executed,
            tool_executions: executed_tools,
        })
    }
}
