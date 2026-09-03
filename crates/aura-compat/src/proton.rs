use std::path::{Path, PathBuf};
use aura_core::error::AuraResult;
use crate::database::CompatEntry;

pub struct ProtonRunner {
    proton_binary: PathBuf,
}

impl ProtonRunner {
    pub fn new<P: AsRef<Path>>(proton_binary: P) -> Self {
        Self {
            proton_binary: proton_binary.as_ref().to_path_buf(),
        }
    }

    pub fn launch_game(&self, game_path: &Path, entry: &CompatEntry) -> AuraResult<String> {
        let gamescope_prefix = entry.gamescope_args.as_deref().unwrap_or("");
        Ok(format!(
            "gamescope {} -- proton run '{}' (DXVK={}, VKD3D={})",
            gamescope_prefix,
            game_path.display(),
            entry.dxvk_enabled,
            entry.vkd3d_enabled
        ))
    }
}
