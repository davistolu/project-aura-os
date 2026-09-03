#!/usr/bin/env bash
# PROJECT AURA - Declarative ISO Build Script
# Uses Nix Flakes to build an immutable, bootable live ISO image.

set -euo pipefail

echo "=========================================================="
echo "  PROJECT AURA - Bootable ISO Generation"
echo "=========================================================="

if ! command -v nix &> /dev/null; then
    echo "Error: 'nix' command not found. Please install Nix with Flakes support."
    echo "Visit: https://nixos.org/download.html"
    exit 1
fi

echo "[1/3] Validating Nix flake definition..."
nix flake check ./nix

echo "[2/3] Building AURA OS ISO image..."
nix build ./nix#iso --out-link result-iso

echo "[3/3] ISO Generation Complete!"
ISO_PATH=$(readlink -f result-iso/iso/*.iso)
echo "Bootable ISO created at: ${ISO_PATH}"
echo "You can flash this to a USB drive using: dd if=${ISO_PATH} of=/dev/sdX bs=4M status=progress"
echo "Or run it in a VM using: ./scripts/run_qemu.sh ${ISO_PATH}"
