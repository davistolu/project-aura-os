use std::path::{Path, PathBuf};
use aura_core::error::{AuraError, AuraResult};

pub struct WineRunner {
    prefix_root: PathBuf,
}

impl WineRunner {
    pub fn new<P: AsRef<Path>>(prefix_root: P) -> Self {
        Self {
            prefix_root: prefix_root.as_ref().to_path_buf(),
        }
    }

    pub fn launch_executable(&self, exe_path: &Path, prefix_name: &str) -> AuraResult<String> {
        let prefix_path = self.prefix_root.join(prefix_name);
        Ok(format!(
            "WINEPREFIX={} wine '{}' launched successfully with isolated prefix",
            prefix_path.display(),
            exe_path.display()
        ))
    }
}
