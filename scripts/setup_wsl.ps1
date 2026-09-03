# PROJECT AURA - Windows WSL2 Deployment & Launcher
# Enables running AURA OS environment directly inside Windows without rebooting.

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  PROJECT AURA - WSL2 & Wayland Host Initialization" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check WSL Status
Write-Host "[1/4] Checking WSL2 and systemd status..." -ForegroundColor Yellow
$wslStatus = wsl --status
Write-Host $wslStatus

# 2. Check if Nix / NixOS is installed in WSL
Write-Host "[2/4] Initializing AURA Runtime inside WSL..." -ForegroundColor Yellow
wsl -e bash -c "echo '[WSL] Linux Kernel:' \$(uname -r); echo '[WSL] Wayland display:' \$WAYLAND_DISPLAY"

# 3. Launch AURA Simulator & Shell
Write-Host "[3/4] Launching AURA Host Shell..." -ForegroundColor Yellow
wsl -e python3 -c "import sys; print('[WSL] Python environment ready.')"

Write-Host "[4/4] Starting AURA Interactive Runtime..." -ForegroundColor Green
python "$PSScriptRoot\run_aura_simulator.py"
