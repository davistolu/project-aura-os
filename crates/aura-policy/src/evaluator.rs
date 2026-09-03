use aura_core::capabilities::Capability;
use aura_core::permissions::PermissionTier;
use std::path::Path;

#[derive(Debug, Clone)]
pub enum PolicyRule {
    AllowAll,
    SandboxFilesystem { allowed_root: String },
    DisallowCapability(Capability),
    RequireApprovalFor(Capability),
}

pub struct PolicyEvaluator;

impl PolicyEvaluator {
    /// Validates if a filesystem path is within the allowed sandbox root
    pub fn is_path_sandboxed(target_path: &Path, allowed_root: &Path) -> bool {
        if let (Ok(canon_target), Ok(canon_root)) = (target_path.canonicalize(), allowed_root.canonicalize()) {
            canon_target.starts_with(canon_root)
        } else {
            // Fallback for non-existent paths (e.g. creating new file)
            target_path.starts_with(allowed_root)
        }
    }

    /// Evaluates if an action tier needs user approval
    pub fn requires_user_approval(tier: PermissionTier, is_autonomous: bool) -> bool {
        tier.requires_approval(is_autonomous)
    }
}
