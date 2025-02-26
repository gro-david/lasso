import os
import subprocess
from pathlib import Path
from .. import read_conf as conf

COMMAND = ":n"

exec_map = {}
# the normal operating mode, for launching apps
def get_opt():
    global exec_map

    desktop_dirs = conf.app_dirs
    desktop_files = [
        str(file) for dir_ in desktop_dirs for file in Path(dir_).glob("*.desktop") if file.is_file()
    ]

    options = []
    exec_map = {}

    for desktop_file in desktop_files:
        with open(desktop_file) as f:
            lines = f.readlines()
        name = next((line.split("=", 1)[1].strip() for line in lines if line.startswith("Name=")), "Unknown")
        exec_cmd = next((line.split("=", 1)[1].strip() for line in lines if line.startswith("Exec=")), "")

        # Handle placeholders in the Exec command
        exec_cmd = exec_cmd.replace("%u", "").replace("%U", "").replace("%f", "").replace("%F", "").strip()
        exec_cmd = exec_cmd.replace("@@u", "").replace("@@", "").strip()

        # Handle Flatpak apps
        if "flatpak run" in exec_cmd and not exec_cmd.startswith("/usr/bin/flatpak"):
            app_id = exec_cmd.split("flatpak run", 1)[-1].strip()
            exec_cmd = f"flatpak run {app_id}"

        if name and exec_cmd:
            options.append(name)
            exec_map[name] = {"exec": exec_cmd, "env_path": ""}

    options.extend(conf.app_names)
    exec_map.update(conf.app_exec_map)

    return COMMAND, options

def exec_selection(selection):
    if not selection in exec_map: return
    try:
        path = os.environ["PATH"]
        if exec_map[selection]["env_path"] != "":
            os.environ["PATH"] = exec_map[selection]["env_path"]
        command = f"setsid {exec_map[selection]["exec"]} > /dev/null 2>&1 &"
        os.environ["PATH"] = path
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error launching {selection}:\n{result.stderr}")
        else:
            exit()
    except Exception as e:
        print(f"Failed to launch {selection}: {e}")
