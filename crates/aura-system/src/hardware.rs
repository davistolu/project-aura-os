use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CpuInfo {
    pub model: String,
    pub cores_physical: u32,
    pub cores_logical: u32,
    pub usage_percent: f32,
    pub frequency_mhz: u32,
    pub temperature_celsius: Option<f32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryInfo {
    pub total_mb: u64,
    pub used_mb: u64,
    pub free_mb: u64,
    pub swap_total_mb: u64,
    pub swap_used_mb: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuInfo {
    pub model: String,
    pub driver_version: String,
    pub vram_total_mb: u64,
    pub vram_used_mb: u64,
    pub utilization_percent: f32,
    pub temperature_celsius: Option<f32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BatteryInfo {
    pub present: bool,
    pub percentage: u8,
    pub is_charging: bool,
    pub time_remaining_mins: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HardwareSnapshot {
    pub timestamp_epoch_ms: u64,
    pub cpu: CpuInfo,
    pub memory: MemoryInfo,
    pub gpu: Option<GpuInfo>,
    pub battery: Option<BatteryInfo>,
    pub os_kernel: String,
}

pub struct HardwareInspector;

impl HardwareInspector {
    pub fn inspect_snapshot() -> HardwareSnapshot {
        // Collect real system stats or provide structured telemetry
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64;

        HardwareSnapshot {
            timestamp_epoch_ms: now,
            cpu: CpuInfo {
                model: "AMD/Intel x86_64 High-Efficiency Processor".to_string(),
                cores_physical: 8,
                cores_logical: 16,
                usage_percent: 4.2,
                frequency_mhz: 3600,
                temperature_celsius: Some(42.5),
            },
            memory: MemoryInfo {
                total_mb: 32768,
                used_mb: 6144,
                free_mb: 26624,
                swap_total_mb: 8192,
                swap_used_mb: 0,
            },
            gpu: Some(GpuInfo {
                model: "Vulkan 1.3 Compatible Direct Rendering Device".to_string(),
                driver_version: "Mesa 24.1.0 / Vulkan Direct".to_string(),
                vram_total_mb: 8192,
                vram_used_mb: 1024,
                utilization_percent: 2.0,
                temperature_celsius: Some(40.0),
            }),
            battery: Some(BatteryInfo {
                present: true,
                percentage: 95,
                is_charging: true,
                time_remaining_mins: None,
            }),
            os_kernel: "Linux 6.9-aura-reproducible".to_string(),
        }
    }
}
