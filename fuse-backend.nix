{ stdenv, config, lib, pkgs, ... }:

with lib;
let
  fuse = pkgs.stdenv.mkDerivation {
    pname = "fuse";
    version = "1.5.0";
    src = pkgs.fetchFromGitHub {
      owner = "gro-david";
      repo = "fuse";
      rev = "master";
      hash = "sha256-kpv0nt2zqzA9U5wCuZlr3zZK2xOxN5WwCIev/ht+zKg=";
    };
    installPhase = ''
      mkdir -p $out/bin
      mkdir -p $out/modules
      mkdir -p ~/.config/fuse

      cp start.py fuse.py $out/
      cp modules/ $out/modules/
      cp hacks ~/.config/fuse/

      echo "#!/bin/sh" > $out/bin/fuse
      echo "python $out/start.py" >> $out/bin/fuse
      chmod +x $out/bin/fuse

      echo "#!/bin/sh" > $out/bin/fuse-network
      echo "python $out/modules/network.py" >> $out/bin/fuse-network
      chmod +x $out/bin/fuse-network

      echo "#!/bin/sh" > $out/bin/fuse-bluetooth
      echo "python $out/modules/bluetooth.py" >> $out/bin/fuse-bluetooth
      chmod +x $out/bin/fuse-bluetooth
    '';
  };

  cfg = config.programs.fuse;
in {
  options = {
    programs.fuse = {
      enable = mkEnableOption "Fuse";

      dashboard = mkOption {
        type = types.listOf (types.submodule {
          options = {
         	  env_path = mkOption { type = types.str; default = ""; };
            name = mkOption { type = types.str; };
            exec = mkOption { type = types.str; };
          };
        });
        default = [];
        description = "A list of programs for the dashboard launcher";
      };

      apps = mkOption {
        type = types.listOf (types.submodule {
          options = {
          	env_path = mkOption { type = types.str; default = ""; };
            name = mkOption { type = types.str; };
            exec = mkOption { type = types.str; };
          };
        });
        default = [];
        description = "List of additional applications to add.";
      };

      app_dirs = mkOption {
        type = types.listOf types.str;
        default = [
          "/usr/share/applications"
          "/var/lib/flatpak/exports/share/applications"
          "~/.local/share/applications"
          "~/.local/share/flatpak/exports/share/applications"
          "/run/current-system/sw/share/applications"
        ];
        description = "List of directories where the launcher should look for applications";
      };
    };
  };

  config = mkIf cfg.enable {
    home.packages = with pkgs; [
    	fuse
      fzf
      pulseaudio
      (python3.withPackages (ps: [ ps.psutil ps.rich ]))
    ];

    # Write launcher.json using builtins.toJSON for simplicity
    xdg.configFile."fuse.json".text = builtins.toJSON {
      dashboard = cfg.dashboard;
      apps = cfg.apps;
      app_dirs = cfg.app_dirs;
    };
  };
}
