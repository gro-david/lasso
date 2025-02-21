{ stdenv, config, lib, pkgs, ... }:

with lib;
let
  launcher = pkgs.stdenv.mkDerivation {
    pname = "launcher";
    version = "1.2.3";
    src = pkgs.fetchFromGitHub {
      owner = "gro-david";
      repo = "launcher";
      rev = "nix";
      hash = "sha256-kpv0nt2zqzA9U5wCuZlr3zZK2xOxN5WwCIev/ht+zKg=";
    };
    installPhase = ''
      mkdir -p $out/bin
      mkdir -p $out/modules
      echo "#!/bin/sh" > $out/bin/start-launcher
      echo "python $out/start.py" >> $out/bin/start-launcher
      chmod +x $out/bin/start-launcher
      cp start.py launcher.py $out/
      cp modules/system.py modules/read_conf.py $out/modules/
    '';
  };

  cfg = config.programs.launcher;
in {
  options = {
    programs.launcher = {
      enable = mkEnableOption "Launcher";

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
      launcher
      fzf
      pulseaudio
      (python3.withPackages (ps: [ ps.psutil ]))
    ];

    # Write launcher.json using builtins.toJSON for simplicity
    xdg.configFile."launcher.json".text = builtins.toJSON {
      dashboard = cfg.dashboard;
      apps = cfg.apps;
      app_dirs = cfg.app_dirs;
    };
  };
}
