pub mod capabilities;
pub mod permissions;
pub mod audit;
pub mod ipc;
pub mod manifest;
pub mod error;

pub use capabilities::Capability;
pub use permissions::PermissionTier;
pub use audit::{AuditEvent, AuditLogger, AuditDecision};
pub use ipc::{IpcMessage, IpcRequest, IpcResponse, CommandIntent};
pub use manifest::AppManifest;
pub use error::{AuraError, AuraResult};
