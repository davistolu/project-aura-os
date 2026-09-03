use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CommandIntent {
    /// Direct, deterministic system execution bypassing LLM inference
    Deterministic { command: String, args: Vec<String> },
    /// Natural language request requiring JARVIS planning and model routing
    NaturalLanguage { prompt: String },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IpcRequest {
    pub request_id: Uuid,
    pub intent: CommandIntent,
    pub client_id: String,
    pub context_workspace: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IpcResponse {
    pub request_id: Uuid,
    pub success: bool,
    pub result: serde_json::Value,
    pub requires_approval: bool,
    pub execution_time_ms: u64,
    pub error: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", content = "payload")]
pub enum IpcMessage {
    Request(IpcRequest),
    Response(IpcResponse),
    Notification { title: String, body: String, urgency: String },
    Heartbeat { daemon_uptime_secs: u64 },
}
