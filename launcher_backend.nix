{ stdenv, config, lib, pkgs, ... }:

with lib;
let 
launcher = pkgs.stdenv.mkDerivation {
    pname = "launcher";
    version = "1.0.0";
    src = pkgs.fetchFromGitHub {
    owner = "gro-david";
    repo = "launcher";
    rev = "nix";
    hash = "sha256-Kt1BObb78SyzbJOUjU3zEaLTsxww/Dcl3B6L1HU02vQ=";
  };
    installPhase = ''
      mkdir -p $out
      mkdir -p $out/bin
      touch $out/bin/start-launcher
      chmod +x $out/bin/start-launcher
      cp start.py $out/
      cp launcher.py $out/
      cp system.py $out/
      echo "#!/bin/sh" > $out/bin/start-launcher
      echo "python $out/start.py" >> $out/bin/start-launcher
    '';
  };
  # Define the configuration for the launcher
  cfg = config.programs.launcher;

  # Function to create the launcher JSON content
createLauncherJson = dashboard: ''
[
  ${lib.concatStringsSep ",\n" (map (program: ''
    {
      "name": "${program.name}",
      "exec": "${program.exec}"
    }
  '') dashboard)}
]
'';
in {

  options = {
    programs.launcher = {
      enable = mkEnableOption "Launcher";

      # Define the list of dashboard programs (with `name` and `exec` for each program)
      dashboard = mkOption {
        type = types.listOf (types.submodule {
          options = {
            name = mkOption { type = types.str; };
            exec = mkOption { type = types.str; };
          };
        });
        default = [];
        description = "A list of programs for the dashboard launcher";
      };
    };
  };

  config = mkIf cfg.enable {
    # Install the dependencies for the launcher
    home.packages = with pkgs; [
      launcher
      fzf
      pulseaudio
      (python3.withPackages (ps: [ ps.psutil ]))
    ];

    # Create the launcher.json file with the necessary content
    xdg.configFile."launcher.json" = lib.mkIf (cfg.dashboard != []) {
      # Use writeTextFile to generate the launcher.json content
      source = pkgs.writeTextFile {
        name = "launcher.json";  # The name of the file
        text = createLauncherJson cfg.dashboard;  # The generated JSON content
      };
    };
    programs.bash.initExtra = ''
      alias launcher="python3 ${dlRepo}/start.py"
    '';
  };
}

