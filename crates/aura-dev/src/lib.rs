pub mod detector;
pub mod orchestrator;

pub use detector::{ProjectDetector, ProjectType, DetectedEnvironment};
pub use orchestrator::DevOrchestrator;
