import os
import sys
import math
import time
import argparse
import threading
import subprocess

from modules import read_conf
from modules.modes import dashboard, normal, window

try:
    # import hacks from the just added paths
    sys.path.append(read_conf.hacks_path)
    import hacks  # type: ignore
except Exception as e:
    print(
        "Could not import hacks. Please check the following error message, and open an issue if required."
    )
    print(e)

TOP_BAR_PATH = "/tmp/lasso_top_bar"
FISH_COMMAND = f"'while true; echo \"$(cat {TOP_BAR_PATH})\"; sleep {str(read_conf.update_interval)}; end'"
BASH_ZSH_COMMAND = f"'while true; do echo \"$(cat {TOP_BAR_PATH})\"; sleep {str(read_conf.update_interval)}; done'"
FZF_STATUS_COMMAND = FISH_COMMAND if read_conf.shell == "fish" else BASH_ZSH_COMMAND


# Function to get system info
def get_system_info():
    while True:
        top_bar = ""
        try:
            top_bar = hacks.top_bar.get()  # type: ignore
        except Exception:
            top_bar = hacks.get_fallback_top_bar()  # type: ignore

        terminal_width = os.get_terminal_size().columns
        padding = math.floor((terminal_width - len(top_bar)) / 2)
        top_bar = (" " * padding) + top_bar

        with open(TOP_BAR_PATH, "w") as f:
            f.write(top_bar)

        time.sleep(read_conf.update_interval)


# runs the fzf command with the correct status and options. finally returns the selected value
def run_fzf(options):
    fzf_command = " ".join(
        [
            "fzf",
            "--header-lines=0",
            "--no-info",
            "--ignore-case",
            "--color='spinner:0'",
            "--preview",
            FZF_STATUS_COMMAND,
            "--preview-window=up:1:follow:wrap:noinfo",
            "--print-query",
            f"--prompt='{read_conf.prompt}'",
        ]
    )
    fzf_input = "\n".join(options)
    result = subprocess.run(
        fzf_command, input=fzf_input, text=True, shell=True, stdout=subprocess.PIPE
    )
    in_list = len(result.stdout.strip().split("\n")) > 1
    output = (
        result.stdout.strip().split("\n")[0]
        if len(result.stdout.strip().split("\n")) == 1
        else result.stdout.strip().split("\n")[1]
    )
    return in_list, output


def run_commands(selection):
    selection = selection.strip()
    prefix = selection.split(" ")[0]

    if not selection:
        return False

    if (mode, prefix) in commands:
        commands[(mode, prefix)](selection.removeprefix(prefix).strip())
        return True
    elif ("any", prefix) in commands:
        commands[("any", prefix)](selection.removeprefix(prefix).strip())
        return True
    elif mode in read_conf.default_commands:
        commands[(mode, read_conf.default_commands[mode])](selection)
        return True

    return False


# adds the additional options for quiting and switching modes. also change modes/quit if requested, otherwise return the selected option
def handle_modes(options):
    index = list(modes.keys()).index(mode)
    relevant_modes = list(modes.keys())
    relevant_modes.pop(index)
    if ":q" not in options:
        options.append(":q")
        options.extend(relevant_modes)

    in_list, selection = run_fzf(options)

    if selection == ":q":
        exit()
    elif selection in modes:
        modes[selection]()
        return ""
    if not in_list and run_commands(selection):
        return ""
    return selection


def run_mode(get_options, exec_selection):
    global mode

    mode, options = get_options()
    selection = handle_modes(options)
    if selection:
        exec_selection(selection)


mode = ""

# define the builtin modes and add the custom ones, a global variable for storing the current mode is also created
modes = {
    ":w": lambda: run_mode(window.get_opt, window.exec_selection),
    ":n": lambda: run_mode(normal.get_opt, normal.exec_selection),
    ":d": lambda: run_mode(dashboard.get_opt, dashboard.exec_selection),
}

# hack modes are user defined modes
hack_modes = {}
for _mode in hacks.modes.modes:  # type: ignore
    hack_modes[_mode] = lambda: run_mode(
        hacks.modes.modes[_mode]["get_opt"],  # type: ignore
        hacks.modes.modes[_mode]["exec_selection"],  # type: ignore
    )

commands = hacks.commands.commands  # type: ignore

# add the hack modes to the dict of all modes
modes.update(hack_modes)

# Start system info updater thread
threading.Thread(target=get_system_info, daemon=True).start()

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode")
args = parser.parse_args()

# start in normal mode except if the user specified something else when running
modes[":n" if args.mode not in modes else args.mode]()
