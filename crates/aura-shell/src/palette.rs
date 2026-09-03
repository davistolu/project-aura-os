use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "type", content = "payload")]
pub enum PaletteAction {
    DirectExecution { command: String, args: Vec<String> },
    NaturalLanguageQuery { prompt: String },
}

pub struct CommandPalette;

impl CommandPalette {
    /// Parses user input in under 1ms to decide whether to dispatch immediately or query AI
    pub fn parse_input(input: &str) -> PaletteAction {
        let trimmed = input.trim();
        if trimmed.starts_with('/') {
            // Explicit shell verb trigger, e.g. /workspace dev or /launch terminal
            let stripped = &trimmed[1..];
            let parts: Vec<String> = stripped.split_whitespace().map(|s| s.to_string()).collect();
            let cmd = parts.first().cloned().unwrap_or_default();
            let args = parts.into_iter().skip(1).collect();
            PaletteAction::DirectExecution { command: cmd, args }
        } else if trimmed.starts_with("open ") || trimmed.starts_with("kill ") || trimmed == "status" {
            let parts: Vec<String> = trimmed.split_whitespace().map(|s| s.to_string()).collect();
            let cmd = parts.first().cloned().unwrap_or_default();
            let args = parts.into_iter().skip(1).collect();
            PaletteAction::DirectExecution { command: cmd, args }
        } else {
            PaletteAction::NaturalLanguageQuery {
                prompt: trimmed.to_string(),
            }
        }
    }
}
