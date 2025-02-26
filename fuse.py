import os
import sys
import json
import time
import threading
import subprocess
from pathlib import Path

from modules import system
from modules import read_conf as conf

try:
    # import hacks from the just added paths
    sys.path.append(conf.hacks_path)
    import hacks # type: ignore
except Exception as e:
    print("Could not import hacks. Please check the following error message, and open an issue if required.")
    print(e)

# Function to get system info
def get_system_info():
    while True:
        top_bar = ""
        try:
            top_bar = hacks.top_bar.get() # type: ignore
        except Exception as e:
            top_bar = hacks.get_fallback_top_bar() # type: ignore

        with open("/tmp/launcher_top_bar", "w") as f:
            f.write(top_bar)

        time.sleep(0.5)

# runs the fzf command with the correct status and options. finally returns the selected value
def run_fzf(options):
    fzf_command = (
        "fzf --header-lines=0 --no-info "
        "--preview 'while true; echo \"$(cat /tmp/launcher_top_bar)\"; sleep 0.5; end' "
        "--preview-window=up:1:follow:wrap:noinfo"
    )
    fzf_input = "\n".join(options)
    result = subprocess.run(fzf_command, input=fzf_input, text=True, shell=True, stdout=subprocess.PIPE)
    return result.stdout.strip()

# adds the additional options for quiting and switching modes. also change modes/quit if requested, otherwise return the selected option
def create_options(options):
    index = list(modes.keys()).index(mode)
    relevant_modes = list(modes.keys())
    relevant_modes.pop(index)
    if not ":q" in options:
        options.append(":q")
        options.extend(relevant_modes)


    selection = run_fzf(options)

    if selection == ":q": exit()
    elif selection in modes:
        modes[selection]()
        return ""
    return selection

# the normal operating mode, for launching apps
def normal_mode():
    global mode
    mode = ':n'
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

    selection = create_options(options)

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

# Window mode: Focus a window
def window_mode():
    global mode
    mode = ":w"
    window_data = subprocess.getoutput("niri msg windows")
    windows = window_data.split("\n\n")

    options = []
    window_map = {}

    for window in windows:
        lines = [line.strip() for line in window.split("\n") if line.strip()]
        window_id = next((line.split(" ", 2)[2].strip(":") for line in lines if line.startswith("Window ID")), None)
        title = next((line.split(": ", 1)[1] for line in lines if line.startswith("Title:")), None)
        title = str(title).replace('"', '')

        if title == 'alacritty launcher': continue

        if window_id and title:
            options.append(title)
            window_map[title] = window_id

    selection = create_options(options)
    if not selection in window_map: return

    window_id = window_map[selection]
    subprocess.run(f"niri msg action focus-window --id {window_id}", shell=True)
    exit()

# Dashboard mode: Launch configured apps
def dashboard_mode():
    global mode
    mode = ":d"
    options = conf.dashboard_names
    exec_map = conf.dashboard_exec_map

    selection = create_options(options)
    if not selection in exec_map: return
    path = os.environ["PATH"]
    if exec_map[selection]["env_path"] != "":
        os.environ["PATH"] = exec_map[selection]["env_path"]
    subprocess.run(exec_map[selection]["exec"], shell=True)
    os.environ["PATH"] = path
    dashboard_mode()

# define the builtin modes and add the custom ones, a global variable for storing the current mode is also created
modes = {
    ":w": window_mode,
    ":n": normal_mode,
    ":d": dashboard_mode
}
modes.update(hacks.modes.modes) # type: ignore
mode = ''

# Start system info updater thread
threading.Thread(target=get_system_info, daemon=True).start()

# Start in normal mode
normal_mode()
