use std::collections::HashSet;
use std::sync::Arc;
use uuid::Uuid;
use chrono::Utc;

use aura_core::audit::{AuditDecision, AuditEvent, AuditLogger};
use aura_core::capabilities::Capability;
use aura_core::error::{AuraError, AuraResult};
use aura_core::permissions::PermissionTier;

use crate::broker::SecretBroker;

#[derive(Debug, Clone)]
pub struct PolicyEngine {
    granted_capabilities: HashSet<Capability>,
    autonomous_mode: bool,
    secret_broker: SecretBroker,
    audit_logger: Arc<AuditLogger>,
}

impl PolicyEngine {
    pub fn new(
        initial_capabilities: HashSet<Capability>,
        autonomous_mode: bool,
        secret_broker: SecretBroker,
        audit_logger: Arc<AuditLogger>,
    ) -> Self {
        Self {
            granted_capabilities: initial_capabilities,
            autonomous_mode,
            secret_broker,
            audit_logger,
        }
    }

    pub fn with_defaults(audit_logger: Arc<AuditLogger>) -> Self {
        let mut caps = HashSet::new();
        caps.insert(Capability::HardwareRead);
        caps.insert(Capability::ProcessList);
        caps.insert(Capability::FilesystemRead { scope: None });
        caps.insert(Capability::WorkspaceManage);
        caps.insert(Capability::NotificationSend);

        Self {
            granted_capabilities: caps,
            autonomous_mode: false,
            secret_broker: SecretBroker::new(),
            audit_logger,
        }
    }

    pub fn grant_capability(&mut self, capability: Capability) {
        self.granted_capabilities.insert(capability);
    }

    pub fn revoke_capability(&mut self, capability: &Capability) {
        self.granted_capabilities.remove(capability);
    }

    pub fn secret_broker(&self) -> &SecretBroker {
        &self.secret_broker
    }

    /// Evaluates whether a tool request is authorized, requires user approval, or is denied.
    pub fn authorize_execution(
        &self,
        task_id: Uuid,
        agent_name: &str,
        tool_name: &str,
        required_capability: &Capability,
        tier: PermissionTier,
        arguments_json: &serde_json::Value,
    ) -> AuraResult<()> {
        // 1. Scan for leaked plaintext secrets in tool arguments
        let args_str = arguments_json.to_string();
        self.secret_broker.scan_for_leaks(&args_str)?;

        // 2. Check if required capability is held
        let holds_capability = self.granted_capabilities.contains(required_capability)
            || self.has_compatible_capability(required_capability);

        if !holds_capability {
            let event = AuditEvent {
                id: Uuid::new_v4(),
                timestamp: Utc::now(),
                task_id,
                agent: agent_name.to_string(),
                capability: required_capability.clone(),
                permission_tier: tier,
                tool_name: tool_name.to_string(),
                arguments_redacted: serde_json::from_str(&self.secret_broker.redact(args_str)).unwrap_or_default(),
                decision: AuditDecision::Denied {
                    reason: format!("Capability '{}' not granted", required_capability),
                },
                execution_duration_ms: None,
                error: Some(format!("Capability '{}' not granted", required_capability)),
            };
            let _ = self.audit_logger.log_event(&event);

            return Err(AuraError::CapabilityDenied(required_capability.to_string()));
        }

        // 3. Check permission tier & approval requirement
        if tier.requires_approval(self.autonomous_mode) {
            let event = AuditEvent {
                id: Uuid::new_v4(),
                timestamp: Utc::now(),
                task_id,
                agent: agent_name.to_string(),
                capability: required_capability.clone(),
                permission_tier: tier,
                tool_name: tool_name.to_string(),
                arguments_redacted: serde_json::from_str(&self.secret_broker.redact(args_str)).unwrap_or_default(),
                decision: AuditDecision::ApprovalRequested,
                execution_duration_ms: None,
                error: None,
            };
            let _ = self.audit_logger.log_event(&event);

            return Err(AuraError::ApprovalRequired(tool_name.to_string(), tier));
        }

        // 4. Authorized execution - log approval event
        let event = AuditEvent {
            id: Uuid::new_v4(),
            timestamp: Utc::now(),
            task_id,
            agent: agent_name.to_string(),
            capability: required_capability.clone(),
            permission_tier: tier,
            tool_name: tool_name.to_string(),
            arguments_redacted: serde_json::from_str(&self.secret_broker.redact(args_str)).unwrap_or_default(),
            decision: AuditDecision::Allowed,
            execution_duration_ms: None,
            error: None,
        };
        let _ = self.audit_logger.log_event(&event);

        Ok(())
    }

    fn has_compatible_capability(&self, target: &Capability) -> bool {
        match target {
            Capability::FilesystemRead { scope: _ } => {
                self.granted_capabilities.iter().any(|c| matches!(c, Capability::FilesystemRead { scope: None }))
            }
            Capability::FilesystemWrite { scope: _ } => {
                self.granted_capabilities.iter().any(|c| matches!(c, Capability::FilesystemWrite { scope: None }))
            }
            Capability::FilesystemDelete { scope: _ } => {
                self.granted_capabilities.iter().any(|c| matches!(c, Capability::FilesystemDelete { scope: None }))
            }
            Capability::NetworkRequest { host: _ } => {
                self.granted_capabilities.iter().any(|c| matches!(c, Capability::NetworkRequest { host: None }))
            }
            _ => false,
        }
    }
}
