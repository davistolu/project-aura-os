use std::path::{Path, PathBuf};
use aura_core::error::AuraResult;

pub struct KvmVmRunner {
    vm_image_dir: PathBuf,
}

impl KvmVmRunner {
    pub fn new<P: AsRef<Path>>(vm_image_dir: P) -> Self {
        Self {
            vm_image_dir: vm_image_dir.as_ref().to_path_buf(),
        }
    }

    pub fn launch_fallback_vm(&self, app_name: &str) -> AuraResult<String> {
        Ok(format!(
            "qemu-system-x86_64 -enable-kvm -m 8G -smp 4 -drive file={}/win11.qcow2 -virtfs local,path=/home/user/shared,mount_tag=host_share (App: {})",
            self.vm_image_dir.display(),
            app_name
        ))
    }
}
