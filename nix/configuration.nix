{ config, pkgs, lib, ... }:

{
  # 1. System Boot and Kernel
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  boot.kernelPackages = pkgs.linuxPackages_latest;

  networking.hostName = "aura-station";
  networking.networkmanager.enable = true;

  # 2. Hardened Base Services
  services.dbus.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    pulse.enable = true;
  };

  # 3. Memory and IO Tuning
  zramSwap.enable = true;

  # 4. Base packages for AURA developers
  environment.systemPackages = with pkgs; [
    git
    curl
    wget
    alacritty
    htop
    neovim
    podman
    vulkan-tools
    mesa-demos
  ];

  # 5. User accounts & security
  users.users.aura = {
    isNormalUser = true;
    extraGroups = [ "wheel" "networkmanager" "video" "audio" "podman" ];
  };

  system.stateVersion = "24.05";
}
