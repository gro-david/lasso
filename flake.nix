{
  description = "Fuse Project";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-24.11";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in {
      packages.${system}.default = pkgs.stdenv.mkDerivation {
        pname = "fuse";
        version = "1.5.0";
        src = ./.;
        buildInputs = [ pkgs.python3 pkgs.alacritty ];
        installPhase = ''
          mkdir -p $out/bin
          mkdir -p $out/modules
          # mkdir -p ~/.config/fuse

          cp start.py fuse.py $out/
          cp -r modules/ $out/
          # cp hacks ~/.config/fuse/

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

      homeManagerModules = {
        fuse = { config, lib, pkgs, ... }: with lib; let
          cfg = config.programs.fuse;
          hacks_init = ''
                        # DO NOT MODIFY THIS FILE
                        # This file is responsible for being able to use any hacks, and for the fallback behavior of the top bar.
                        # If you do modify this, it could result in a non working installation of FUSE.
                        # For creating hacks, please check out the documentation on GitHub https://github.com/gro-david/fuse

                        import time
                        import glob
                        from os.path import dirname, basename, isfile, join

                        # define what should be imported
                        modules = glob.glob(join(dirname(__file__), "*.py"))
                        __all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')] # type: ignore

                        # import all hacks the user made
                        from . import *
                        from .modes import *

                        def get_fallback_top_bar():
                              time_now = time.strftime("%Y-%m-%d %H:%M:%S")
                              brightness = system.get_brightness() # type: ignore
                              volume = system.get_volume() # type: ignore
                              percentage, plugged, remaining = system.get_battery_state() # type: ignore
                              remaining = f"󱧥 {time.strftime("%H:%M:%S", time.gmtime(remaining))}" if not remaining == -2 else ""
                              charging = "󰚥" if plugged else "󰚦"
                              keyboard_layout = system.get_keyboard() # type: ignore

                              top_bar = f"󰥔 {time_now} | 󰃟 {brightness}% | 󰌌 {keyboard_layout} |  {volume}% | 󱐋 {percentage}% {remaining} {charging} "
                              return top_bar
                      '';
          system_py = ''
                        # DO NOT MODIFY THIS FILE
                        # This file is responsible for being able to use any hacks, and for the fallback behavior of the top bar.
                        # If you do modify this, it could result in a non working installation of FUSE.
                        # For creating hacks, please check out the documentation on GitHub https://github.com/gro-david/fuse

                        import subprocess
                        import os
                        import glob
                        import psutil

                        def get_volume():
                              result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'], stdout=subprocess.PIPE)
                              output = result.stdout.decode()
                              # Extract the volume percentage from the output
                              volume_line = [line for line in output.split('\n') if 'Volume:' in line]
                              if volume_line:
                                  volume = volume_line[0].split()[4].strip('%')
                                  return int(volume)
                              return None

                        def get_brightness():
                              # Find the correct backlight path
                              backlight_paths = glob.glob('/sys/class/backlight/*/brightness')
                              if not backlight_paths:
                                  print("No backlight path found")
                                  return None

                              brightness_path = backlight_paths[0]
                              max_brightness_path = brightness_path.replace('brightness', 'max_brightness')

                              # Read the brightness and max brightness values
                              try:
                                  with open(brightness_path, 'r') as file:
                                      brightness = int(file.read().strip())

                                  with open(max_brightness_path, 'r') as file:
                                      max_brightness = int(file.read().strip())

                                  # Calculate the brightness level as a percentage
                                  brightness_level = round((brightness / max_brightness) * 100, 2)
                                  return brightness_level
                              except FileNotFoundError:
                                  print("Brightness file not found")
                                  return None
                              except Exception as e:
                                  print(f"An error occurred: {e}")
                                  return None

                        def get_battery_state():
                              battery = psutil.sensors_battery()
                              if battery:
                                  return round(battery.percent, 2), battery.power_plugged, battery.secsleft
                              return None, None, None

                        def get_keyboard():
                              result = subprocess.run(['niri', 'msg', 'keyboard-layouts'], stdout=subprocess.PIPE)
                              output = result.stdout.decode()
                              line = [line for line in output.split('\n') if '*' in line][0]
                              line = line.translate(str.maketrans('*0123456789', ' ' * 11))
                              line = line.strip()
                              return line
                      '';
          modes_init = ''
                        # This file is responsible for being able to use any hacks, and for the fallback behavior of the top bar.
                        # If you do modify this, it could result in a non working installation of FUSE.
                        # For creating hacks, please check out the documentation on GitHub https://github.com/gro-david/fuse

                        import glob
                        from os.path import dirname, basename, isfile, join
                        import sys

                        # define what should be imported
                        modules = glob.glob(join(dirname(__file__), "*.py"))
                        __all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')] # type: ignore

                        # import all modes the user made
                        from . import *

                        class ModeExistsException(Exception):
                              def __init__(self):
                              self.message = "This mode already exists. Check your hacks."
                              super().__init__(self.message)

                        modes = {}
                        for module in __all__:
                            cmd = sys.modules[f"hacks.modes.{module}"].COMMAND
                            opt = sys.modules[f"hacks.modes.{module}"].get_opt
                            exec = sys.modules[f"hacks.modes.{module}"].exec_selection

                            if cmd in modes: raise ModeExistsException()

                            modes[cmd] = {"opt": opt, "exec": exec}
                      '';
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
              self.packages.${system}.default
              fzf
              pulseaudio
              (pkgs.python3.withPackages (ps: [ ps.psutil ps.rich ]))
            ];

            # Write launcher.json using builtins.toJSON for simplicity
            xdg.configFile."fuse/fuse.json".text = builtins.toJSON {
              dashboard = cfg.dashboard;
              apps = cfg.apps;
              app_dirs = cfg.app_dirs;
            };
            xdg.configFile."fuse/hacks/__init.py__".text = hacks_init;
            xdg.configFile."fuse/hacks/system.py".text = system_py;
            xdg.configFile."fuse/hacks/modes/__init.py__".text = modes_init;
          };
        };
      };
    };
}
