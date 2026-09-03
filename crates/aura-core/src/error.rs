use thiserror::Error;

#[derive(Error, Debug)]
pub enum AuraError {
    #[error("Capability violation: agent requires '{0}' which is not granted")]
    CapabilityDenied(String),

    #[error("Permission approval required for action '{0}' under tier {1:?}")]
    ApprovalRequired(String, crate::permissions::PermissionTier),

    #[error("Operation rejected by user")]
    UserRejected,

    #[error("Security policy violation: {0}")]
    PolicyViolation(String),

    #[error("Secret leak detected in parameters: {0}")]
    SecretLeakDetected(String),

    #[error("Tool execution failed: {0}")]
    ToolExecutionFailed(String),

    #[error("Model provider error: {0}")]
    ProviderError(String),

    #[error("IPC communication error: {0}")]
    IpcError(String),

    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    #[error("System error: {0}")]
    System(String),
}

pub type AuraResult<T> = Result<T, AuraError>;
