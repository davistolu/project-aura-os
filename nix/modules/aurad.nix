{ config, pkgs, lib, ... }:

{
  systemd.services.aurad = {
    description = "AURA Platform System Daemon";
    after = [ "dbus.service" "network.target" ];
    wantedBy = [ "multi-user.target" ];

    serviceConfig = {
      ExecStart = "${pkgs.coreutils}/bin/true"; # In production: path to aurad binary
      Restart = "always";
      RestartSec = "2s";
      ProtectSystem = "strict";
      ProtectHome = "read-only";
      PrivateTmp = true;
      NoNewPrivileges = true;
      User = "root";
    };
  };
}
