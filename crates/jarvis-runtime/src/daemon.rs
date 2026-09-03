use std::sync::Arc;
use serde_json::json;
use uuid::Uuid;
use chrono::Utc;

use aura_core::error::{AuraError, AuraResult};
use aura_core::ipc::{CommandIntent, IpcRequest, IpcResponse};
use aura_policy::PolicyEngine;
use jarvis_providers::traits::LlmProvider;

use crate::agent::JarvisAgent;
use crate::memory::MemoryEngine;
use crate::router::{ModelRouter, RoutingDecision};
use crate::tools::ToolRegistry;

#[derive(Clone)]
pub struct JarvisDaemon {
    router: Arc<ModelRouter>,
    memory: Arc<MemoryEngine>,
    tools: ToolRegistry,
    policy: PolicyEngine,
    provider: Arc<dyn LlmProvider>,
}

impl JarvisDaemon {
    pub fn new(
        router: Arc<ModelRouter>,
        memory: Arc<MemoryEngine>,
        tools: ToolRegistry,
        policy: PolicyEngine,
        provider: Arc<dyn LlmProvider>,
    ) -> Self {
        Self {
            router,
            memory,
            tools,
            policy,
            provider,
        }
    }

    /// Primary dispatch handling both deterministic fast-path and AI agent execution
    pub async fn handle_request(&self, request: IpcRequest) -> IpcResponse {
        let start_time = std::time::Instant::now();

        match &request.intent {
            CommandIntent::Deterministic { command, args } => {
                let res = self.execute_deterministic(command, args).await;
                let elapsed = start_time.elapsed().as_millis() as u64;

                match res {
                    Ok(val) => IpcResponse {
                        request_id: request.request_id,
                        success: true,
                        result: val,
                        requires_approval: false,
                        execution_time_ms: elapsed,
                        error: None,
                    },
                    Err(e) => IpcResponse {
                        request_id: request.request_id,
                        success: false,
                        result: json!(null),
                        requires_approval: matches!(e, AuraError::ApprovalRequired(_, _)),
                        execution_time_ms: elapsed,
                        error: Some(e.to_string()),
                    },
                }
            }
            CommandIntent::NaturalLanguage { prompt } => {
                let routing = self.router.route(prompt);
                
                // Fast-path bypass if router recognized deterministic verb
                if let RoutingDecision::Deterministic { command, args } = routing {
                    let res = self.execute_deterministic(&command, &args).await;
                    let elapsed = start_time.elapsed().as_millis() as u64;
                    return match res {
                        Ok(val) => IpcResponse {
                            request_id: request.request_id,
                            success: true,
                            result: val,
                            requires_approval: false,
                            execution_time_ms: elapsed,
                            error: None,
                        },
                        Err(e) => IpcResponse {
                            request_id: request.request_id,
                            success: false,
                            result: json!(null),
                            requires_approval: matches!(e, AuraError::ApprovalRequired(_, _)),
                            execution_time_ms: elapsed,
                            error: Some(e.to_string()),
                        },
                    };
                }

                // AI Agent Path
                let agent = JarvisAgent::new(
                    "jarvis-main",
                    self.provider.clone(),
                    self.tools.clone(),
                    self.policy.clone(),
                    self.memory.clone(),
                );

                let result = agent.run_task(prompt).await;
                let elapsed = start_time.elapsed().as_millis() as u64;

                match result {
                    Ok(task_res) => IpcResponse {
                        request_id: request.request_id,
                        success: task_res.success,
                        result: json!({
                            "response": task_res.final_response,
                            "steps": task_res.steps_executed,
                            "tools_called": task_res.tool_executions
                        }),
                        requires_approval: false,
                        execution_time_ms: elapsed,
                        error: None,
                    },
                    Err(e) => IpcResponse {
                        request_id: request.request_id,
                        success: false,
                        result: json!(null),
                        requires_approval: matches!(e, AuraError::ApprovalRequired(_, _)),
                        execution_time_ms: elapsed,
                        error: Some(e.to_string()),
                    },
                }
            }
        }
    }

    async fn execute_deterministic(&self, command: &str, args: &[String]) -> AuraResult<serde_json::Value> {
        let tool = self.tools.get(command).ok_or_else(|| {
            AuraError::System(format!("Command '{}' not found", command))
        })?;

        let args_val = if args.is_empty() {
            json!({})
        } else {
            json!({ "arg": args[0] })
        };

        self.policy.authorize_execution(
            Uuid::new_v4(),
            "deterministic-shell",
            tool.name(),
            &tool.required_capability(),
            tool.permission_tier(),
            &args_val,
        )?;

        tool.execute(args_val).await
    }
}
