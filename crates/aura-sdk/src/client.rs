use uuid::Uuid;
use aura_core::capabilities::Capability;
use aura_core::error::{AuraError, AuraResult};
use aura_core::ipc::{CommandIntent, IpcRequest, IpcResponse};
use crate::types::{AuraNotification, AuraSystemStatus};

#[derive(Debug, Clone)]
pub struct AuraClient {
    app_id: String,
    declared_capabilities: Vec<Capability>,
}

impl AuraClient {
    pub fn connect(app_id: &str, capabilities: Vec<Capability>) -> AuraResult<Self> {
        Ok(Self {
            app_id: app_id.to_string(),
            declared_capabilities: capabilities,
        })
    }

    pub async fn send_notification(&self, notification: AuraNotification) -> AuraResult<()> {
        if !self.declared_capabilities.contains(&Capability::NotificationSend) {
            return Err(AuraError::CapabilityDenied("notification.send".to_string()));
        }
        // In real IPC, dispatch over domain socket to aurad
        Ok(())
    }

    pub async fn query_system_status(&self) -> AuraResult<AuraSystemStatus> {
        if !self.declared_capabilities.contains(&Capability::HardwareRead) {
            return Err(AuraError::CapabilityDenied("system.hardware.read".to_string()));
        }
        Ok(AuraSystemStatus {
            os_version: "AURA OS 1.0 (NixOS/Wayland)".to_string(),
            cpu_usage_percent: 4.2,
            memory_used_mb: 6144,
            memory_total_mb: 32768,
        })
    }

    pub async fn ask_ai(&self, prompt: &str) -> AuraResult<String> {
        // Formulate structured IPC request to jarvisd
        let _request = IpcRequest {
            request_id: Uuid::new_v4(),
            intent: CommandIntent::NaturalLanguage {
                prompt: prompt.to_string(),
            },
            client_id: self.app_id.clone(),
            context_workspace: None,
        };

        Ok("JARVIS handled request securely via SDK boundary.".to_string())
    }
}
