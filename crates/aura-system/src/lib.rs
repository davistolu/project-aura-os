pub mod hardware;
pub mod workspaces;
pub mod power;
pub mod service;

pub use hardware::{HardwareInspector, HardwareSnapshot, CpuInfo, MemoryInfo, GpuInfo, BatteryInfo};
pub use workspaces::{WorkspaceManager, WorkspaceProfile, WorkspaceType};
pub use power::{PowerManager, PowerProfile};
pub use service::SystemDaemon;
