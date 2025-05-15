import os
import subprocess
from .. import read_conf as conf

COMMAND = ":d"
exec_map = {}


# Dashboard mode: Launch configured apps
def get_opt():
    global exec_map

    options = conf.dashboard_names
    exec_map = conf.dashboard_exec_map

    return COMMAND, options


def exec_selection(selection):
    if selection not in exec_map:
        return

    path = os.environ["PATH"]
    if exec_map[selection]["env_path"] != "":
        os.environ["PATH"] = exec_map[selection]["env_path"]
    subprocess.run(exec_map[selection]["exec"], shell=True)
    os.environ["PATH"] = path
