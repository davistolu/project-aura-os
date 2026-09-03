{ config, pkgs, ... }:

{
  isoImage.isoBaseName = "aura-os-installer";
  isoImage.volumeID = "AURA_LIVE";

  # Auto-login for live trial environment
  services.getty.autologinUser = "nixos";

  environment.systemPackages = with pkgs; [
    parted
    efibootmgr
    nix-prefetch-git
  ];
}
