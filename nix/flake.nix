{
  description = "PROJECT AURA - Declarative Operating System Flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }: {
    nixosConfigurations.aura-workstation = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix
        ./modules/aurad.nix
        ./modules/jarvisd.nix
        ./modules/wayland.nix
        ./modules/gaming.nix
      ];
    };

    # Generates bootable live installation ISO
    packages.x86_64-linux.iso = (nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        "${nixpkgs}/nixos/modules/installer/cd-dvd/installation-cd-minimal.nix"
        ./iso.nix
      ];
    }).config.system.build.isoImage;
  };
}
