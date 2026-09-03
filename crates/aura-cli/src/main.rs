use clap::{Parser, Subcommand};
use std::sync::Arc;
use uuid::Uuid;

use aura_core::audit::AuditLogger;
use aura_core::ipc::{CommandIntent, IpcRequest};
use aura_policy::PolicyEngine;
use aura_system::{HardwareInspector, SystemDaemon};
use aura_compat::{CompatibilityDatabase, WineRunner, ProtonRunner, KvmVmRunner, RuntimeTier};
use aura_dev::{DevOrchestrator, ProjectDetector};
use jarvis_providers::mock::MockLlmProvider;
use jarvis_runtime::daemon::JarvisDaemon;
use jarvis_runtime::memory::MemoryEngine;
use jarvis_runtime::router::ModelRouter;
use jarvis_runtime::tools::{
    ToolRegistry,
    hardware::SysHardwareInspectTool,
    process::SysProcessInspectTool,
    filesystem::FsSearchTool,
    workspace::WorkspaceSwitchTool,
    dev::DevEnvironmentDoctorTool,
    notification::SystemNotificationTool,
};

#[derive(Parser)]
#[command(name = "aura")]
#[command(about = "PROJECT AURA - Unified Personal Computing Platform CLI", version = "0.1.0")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Inspect system hardware, CPU, RAM, and thermals
    Hardware,
    /// List or switch active desktop workspace profiles
    Workspace {
        #[arg(short, long)]
        switch: Option<String>,
    },
    /// Query JARVIS AI runtime with natural language
    Ai {
        /// The natural language prompt or instruction
        prompt: Vec<String>,
        /// Autonomous mode flag
        #[arg(short, long)]
        autonomous: bool,
    },
    /// Developer environment tooling and project diagnostics
    Dev {
        #[command(subcommand)]
        sub: DevSubcommands,
    },
    /// Windows application and gaming compatibility runner
    Compat {
        #[command(subcommand)]
        sub: CompatSubcommands,
    },
    /// Inspect security audit logs
    Audit,
}

#[derive(Subcommand)]
enum DevSubcommands {
    /// Check project environment health and detected tools
    Doctor,
    /// Generate reproducible Nix shell configuration for current directory
    Shell,
}

#[derive(Subcommand)]
enum CompatSubcommands {
    /// Inspect empirical compatibility tier for an application
    Info { app_id: String },
    /// Run a Windows executable using the recommended runtime
    Run { file_path: String },
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();

    let audit_logger = Arc::new(AuditLogger::fallback());
    let sys_daemon = Arc::new(SystemDaemon::new());

    match cli.command {
        Commands::Hardware => {
            let snapshot = HardwareInspector::inspect_snapshot();
            println!("{}", serde_json::to_string_pretty(&snapshot)?);
        }
        Commands::Workspace { switch } => {
            if let Some(target) = switch {
                match sys_daemon.switch_workspace(&target) {
                    Ok(profile) => println!("Switched to workspace: {} [{:?}]", profile.name, profile.workspace_type),
                    Err(e) => eprintln!("Error: {}", e),
                }
            } else {
                let workspaces = sys_daemon.workspace_manager.list_workspaces();
                let active = sys_daemon.workspace_manager.get_active_workspace();
                println!("Active Workspace: {}\nAvailable Workspaces:", active.name);
                for ws in workspaces {
                    println!(" - {} (ID: {}, Type: {:?})", ws.name, ws.id, ws.workspace_type);
                }
            }
        }
        Commands::Ai { prompt, autonomous } => {
            let prompt_text = prompt.join(" ");
            if prompt_text.is_empty() {
                eprintln!("Error: Please provide a prompt for JARVIS.");
                return Ok(());
            }

            let policy = PolicyEngine::with_defaults(audit_logger.clone());
            let memory = Arc::new(MemoryEngine::new());
            let router = Arc::new(ModelRouter::new(true, false));

            let mut tools = ToolRegistry::new();
            tools.register(Arc::new(SysHardwareInspectTool));
            tools.register(Arc::new(SysProcessInspectTool));
            tools.register(Arc::new(FsSearchTool));
            tools.register(Arc::new(WorkspaceSwitchTool::new(sys_daemon.workspace_manager.clone())));
            tools.register(Arc::new(DevEnvironmentDoctorTool));
            tools.register(Arc::new(SystemNotificationTool));

            let provider = Arc::new(MockLlmProvider::new());
            let daemon = JarvisDaemon::new(router, memory, tools, policy, provider);

            let req = IpcRequest {
                request_id: Uuid::new_v4(),
                intent: CommandIntent::NaturalLanguage { prompt: prompt_text },
                client_id: "aura-cli".to_string(),
                context_workspace: Some("dev".to_string()),
            };

            let resp = daemon.handle_request(req).await;
            if resp.success {
                println!("JARVIS Result ({} ms):\n{}", resp.execution_time_ms, serde_json::to_string_pretty(&resp.result)?);
            } else {
                eprintln!("JARVIS Error: {:?}", resp.error);
            }
        }
        Commands::Dev { sub } => {
            let orchestrator = DevOrchestrator::new(".");
            match sub {
                DevSubcommands::Doctor => {
                    let detected = orchestrator.inspect_environment();
                    println!("AURA Dev Doctor - Project Diagnostics:");
                    println!(" - Project Type: {:?}", detected.project_type);
                    println!(" - Manifest: {}", detected.manifest_file);
                    println!(" - Toolchain: {:?}", detected.recommended_toolchain);
                }
                DevSubcommands::Shell => {
                    let shell_flake = orchestrator.generate_nix_shell()?;
                    println!("{}", shell_flake);
                }
            }
        }
        Commands::Compat { sub } => {
            let db = CompatibilityDatabase::new();
            match sub {
                CompatSubcommands::Info { app_id } => {
                    if let Some(entry) = db.lookup(&app_id) {
                        println!("Compatibility Entry for '{}':", entry.title);
                        println!(" - Recommended Tier: {:?}", entry.recommended_tier);
                        println!(" - DXVK Enabled: {}", entry.dxvk_enabled);
                        println!(" - VKD3D Enabled: {}", entry.vkd3d_enabled);
                        println!(" - Dependencies: {:?}", entry.required_dependencies);
                    } else {
                        println!("No entry found for '{}'. Defaulting to Wine isolated prefix.", app_id);
                    }
                }
                CompatSubcommands::Run { file_path } => {
                    let path = std::path::Path::new(&file_path);
                    let file_stem = path.file_stem().and_then(|s| s.to_str()).unwrap_or("app");
                    let entry = db.lookup(file_stem);

                    let tier = entry.map(|e| &e.recommended_tier).unwrap_or(&RuntimeTier::WineStaging);
                    match tier {
                        RuntimeTier::ProtonDirect => {
                            let runner = ProtonRunner::new("/usr/bin/proton");
                            let cmd = runner.launch_game(path, entry.unwrap())?;
                            println!("[Proton Execution]: {}", cmd);
                        }
                        RuntimeTier::WineStaging => {
                            let runner = WineRunner::new("/var/lib/aura/wine_prefixes");
                            let cmd = runner.launch_executable(path, file_stem)?;
                            println!("[Wine Execution]: {}", cmd);
                        }
                        RuntimeTier::KvmVmFallback => {
                            let runner = KvmVmRunner::new("/var/lib/aura/vms");
                            let cmd = runner.launch_fallback_vm(file_stem)?;
                            println!("[KVM Fallback]: {}", cmd);
                        }
                        RuntimeTier::Unsupported => {
                            eprintln!("This software is unsupported on current hardware.");
                        }
                    }
                }
            }
        }
        Commands::Audit => {
            println!("Audit Log location: {}", audit_logger.path().display());
            if let Ok(content) = std::fs::read_to_string(audit_logger.path()) {
                println!("--- Structured Tamper-Evident Audit Log ---");
                println!("{}", content);
            } else {
                println!("(No audit events logged yet in current session)");
            }
        }
    }

    Ok(())
}
