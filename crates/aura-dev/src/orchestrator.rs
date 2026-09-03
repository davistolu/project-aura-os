use std::path::{Path, PathBuf};
use aura_core::error::AuraResult;
use crate::detector::{DetectedEnvironment, ProjectDetector};

pub struct DevOrchestrator {
    workspace_root: PathBuf,
}

impl DevOrchestrator {
    pub fn new<P: AsRef<Path>>(workspace_root: P) -> Self {
        Self {
            workspace_root: workspace_root.as_ref().to_path_buf(),
        }
    }

    pub fn inspect_environment(&self) -> DetectedEnvironment {
        ProjectDetector::detect(&self.workspace_root)
    }

    pub fn generate_nix_shell(&self) -> AuraResult<String> {
        let env = self.inspect_environment();
        let packages_str = env.recommended_toolchain.join(" ");
        Ok(format!(
            "# Auto-generated AURA Nix Developer Shell\n\
            {{\n  \
              description = \"AURA Dev Shell for {:?}\";\n  \
              inputs.nixpkgs.url = \"github:NixOS/nixpkgs/nixos-unstable\";\n  \
              outputs = {{ self, nixpkgs }}: let\n    \
                pkgs = nixpkgs.legacyPackages.x86_64-linux;\n  \
              in {{\n    \
                devShells.x86_64-linux.default = pkgs.mkShell {{\n      \
                  buildInputs = with pkgs; [ {} ];\n    \
                }};\n  \
              }};\n\
            }}",
            env.project_type,
            packages_str
        ))
    }
}
