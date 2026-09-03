use serde::{Deserialize, Serialize};
use crate::capabilities::Capability;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum RuntimeType {
    Native,
    Wine,
    Proton,
    Container,
    Vm,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppManifest {
    pub id: String,
    pub name: String,
    pub version: String,
    pub description: Option<String>,
    pub publisher: String,
    pub executable: String,
    pub runtime: RuntimeType,
    pub required_capabilities: Vec<Capability>,
    pub environment_variables: Option<std::collections::HashMap<String, String>>,
    pub sandbox_isolated: bool,
}
