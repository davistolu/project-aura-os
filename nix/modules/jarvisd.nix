{ config, pkgs, lib, ... }:

{
  systemd.user.services.jarvisd = {
    description = "JARVIS OS-Native AI Runtime Daemon";
    after = [ "graphical-session.target" ];
    wantedBy = [ "default.target" ];

    serviceConfig = {
      ExecStart = "${pkgs.coreutils}/bin/true"; # In production: path to jarvisd binary
      Restart = "always";
      RestartSec = "3s";
      ProtectSystem = "strict";
      PrivateTmp = true;
      NoNewPrivileges = true;
      MemoryMax = "2G";
      CPUQuota = "50%";
    };
  };
}
