use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum ProjectType {
    Rust,
    NodeJs,
    Python,
    Go,
    Php,
    Cpp,
    GenericNix,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DetectedEnvironment {
    pub project_type: ProjectType,
    pub manifest_file: String,
    pub recommended_toolchain: Vec<String>,
    pub required_services: Vec<String>,
}

pub struct ProjectDetector;

impl ProjectDetector {
    pub fn detect<P: AsRef<Path>>(root: P) -> DetectedEnvironment {
        let root = root.as_ref();

        if root.join("Cargo.toml").exists() {
            return DetectedEnvironment {
                project_type: ProjectType::Rust,
                manifest_file: "Cargo.toml".to_string(),
                recommended_toolchain: vec!["cargo".to_string(), "rustc".to_string(), "clippy".to_string(), "rust-analyzer".to_string()],
                required_services: vec![],
            };
        }

        if root.join("package.json").exists() {
            return DetectedEnvironment {
                project_type: ProjectType::NodeJs,
                manifest_file: "package.json".to_string(),
                recommended_toolchain: vec!["node".to_string(), "pnpm".to_string(), "typescript".to_string()],
                required_services: vec![],
            };
        }

        if root.join("pyproject.toml").exists() || root.join("requirements.txt").exists() {
            return DetectedEnvironment {
                project_type: ProjectType::Python,
                manifest_file: "pyproject.toml".to_string(),
                recommended_toolchain: vec!["python3".to_string(), "uv".to_string(), "ruff".to_string()],
                required_services: vec![],
            };
        }

        if root.join("go.mod").exists() {
            return DetectedEnvironment {
                project_type: ProjectType::Go,
                manifest_file: "go.mod".to_string(),
                recommended_toolchain: vec!["go".to_string(), "gopls".to_string()],
                required_services: vec![],
            };
        }

        DetectedEnvironment {
            project_type: ProjectType::GenericNix,
            manifest_file: "flake.nix".to_string(),
            recommended_toolchain: vec!["nix-shell".to_string()],
            required_services: vec![],
        }
    }
}
