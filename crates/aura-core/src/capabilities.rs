use serde::{Deserialize, Serialize};
use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Capability {
    /// Read hardware state (CPU, GPU, RAM, storage, battery, thermals, fans)
    HardwareRead,
    /// List active system and user processes
    ProcessList,
    /// Terminate or manage user processes
    ProcessKill,
    /// Read files within declared project scopes
    FilesystemRead { scope: Option<String> },
    /// Write or modify files within declared project scopes
    FilesystemWrite { scope: Option<String> },
    /// Delete files or directories
    FilesystemDelete { scope: Option<String> },
    /// Execute commands in isolated developer/user terminals
    TerminalExecute,
    /// Make outbound network HTTP/TCP requests
    NetworkRequest { host: Option<String> },
    /// Install or remove system packages via package manager
    PackageManage,
    /// Manage window positions, workspaces, and display layouts
    WorkspaceManage,
    /// Post desktop notifications to user shell
    NotificationSend,
    /// Manage Windows compatibility runtime and KVM virtual machines
    VmManage,
    /// Manage persistent user automations and event hooks
    AutomationManage,
}

impl fmt::Display for Capability {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Capability::HardwareRead => write!(f, "system.hardware.read"),
            Capability::ProcessList => write!(f, "system.process.list"),
            Capability::ProcessKill => write!(f, "system.process.kill"),
            Capability::FilesystemRead { scope } => write!(f, "filesystem.read[{}]", scope.as_deref().unwrap_or("*")),
            Capability::FilesystemWrite { scope } => write!(f, "filesystem.write[{}]", scope.as_deref().unwrap_or("*")),
            Capability::FilesystemDelete { scope } => write!(f, "filesystem.delete[{}]", scope.as_deref().unwrap_or("*")),
            Capability::TerminalExecute => write!(f, "terminal.execute"),
            Capability::NetworkRequest { host } => write!(f, "network.request[{}]", host.as_deref().unwrap_or("*")),
            Capability::PackageManage => write!(f, "package.manage"),
            Capability::WorkspaceManage => write!(f, "workspace.manage"),
            Capability::NotificationSend => write!(f, "notification.send"),
            Capability::VmManage => write!(f, "vm.manage"),
            Capability::AutomationManage => write!(f, "automation.manage"),
        }
    }
}
