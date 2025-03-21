import os
import sys
import json
import time
import argparse
import threading
import subprocess
from pathlib import Path

from modules import read_conf, system
from modules.modes import dashboard, normal, window

try:
    # import hacks from the just added paths
    sys.path.append(read_conf.hacks_path)
    import hacks # type: ignore
except Exception as e:
    print("Could not import hacks. Please check the following error message, and open an issue if required.")
    print(e)

TOP_BAR_PATH = "/tmp/lasso_top_bar"
FISH_COMMAND = f"--preview 'while true; echo \"$(cat {TOP_BAR_PATH})\"; sleep {str(read_conf.update_interval)}; end' "
BASH_ZSH_COMMAND = f"--preview 'while true; do echo \"$(cat {TOP_BAR_PATH})\"; sleep {str(read_conf.update_interval)}; done' "
FZF_STATUS_COMMAND = FISH_COMMAND if read_conf.shell == "fish" else BASH_ZSH_COMMAND

# Function to get system info
def get_system_info():
    while True:
        top_bar = ""
        try:
            top_bar = hacks.top_bar.get() # type: ignore
        except Exception as e:
            top_bar = hacks.get_fallback_top_bar() # type: ignore

        with open(TOP_BAR_PATH, "w") as f:
            f.write(top_bar)

        time.sleep(read_conf.update_interval)

# runs the fzf command with the correct status and options. finally returns the selected value
def run_fzf(options):
    fzf_command = (
        "fzf --header-lines=0 --no-info "
        f"{FZF_STATUS_COMMAND}"
        "--preview-window=up:1:follow:wrap:noinfo"
    )
    fzf_input = "\n".join(options)
    result = subprocess.run(fzf_command, input=fzf_input, text=True, shell=True, stdout=subprocess.PIPE)
    return result.stdout.strip()

# adds the additional options for quiting and switching modes. also change modes/quit if requested, otherwise return the selected option
def handle_modes(options):
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

def run_mode(get_options, exec_selection):
    global mode

    mode, options = get_options()
    selection = handle_modes(options)
    exec_selection(selection)

mode = ''

# define the builtin modes and add the custom ones, a global variable for storing the current mode is also created
modes = {
    ":w": lambda: run_mode(window.get_opt, window.exec_selection),
    ":n": lambda: run_mode(normal.get_opt, normal.exec_selection),
    ":d": lambda: run_mode(dashboard.get_opt, dashboard.exec_selection)
}

# hack modes are user defined modes
hack_modes = {}
for _mode in hacks.modes.modes: # type: ignore
    hack_modes[_mode] = lambda: run_mode(hacks.modes.modes[_mode]["get_opt"], hacks.modes.modes[_mode]["exec_selection"]) # type: ignore

# add the hack modes to the dict of all modes
modes.update(hack_modes)

# Start system info updater thread
threading.Thread(target=get_system_info, daemon=True).start()

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode")
args = parser.parse_args()

# start in normal mode
modes[":n" if args.mode not in modes else args.mode]()
