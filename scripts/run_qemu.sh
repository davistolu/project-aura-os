#!/usr/bin/env bash
# PROJECT AURA - QEMU VM Launcher
# Boots the compiled AURA ISO in a hardware-accelerated KVM virtual machine.

set -euo pipefail

ISO_PATH="${1:-result-iso/iso/*.iso}"

echo "=========================================================="
echo "  PROJECT AURA - QEMU Hardware-Accelerated Virtual Machine"
echo "=========================================================="

if ! command -v qemu-system-x86_64 &> /dev/null; then
    echo "Error: 'qemu-system-x86_64' not found. Please install QEMU."
    exit 1
fi

KVM_FLAG=""
if [ -e /dev/kvm ]; then
    KVM_FLAG="-enable-kvm"
fi

qemu-system-x86_64 \
    ${KVM_FLAG} \
    -m 8192 \
    -smp 4 \
    -cpu host \
    -vga virtio \
    -display gtk,gl=on \
    -device virtio-net-pci,netdev=net0 \
    -netdev user,id=net0 \
    -cdrom ${ISO_PATH} \
    -boot d
