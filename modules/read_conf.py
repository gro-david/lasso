import os
import json
import shutil
from pathlib import Path

try:
    import errors
except Exception:
    from modules import errors

username = os.getlogin()
config_path = f"/home/{username}/.config/lasso/lasso.json"
hacks_path = f"/home/{username}/.config/lasso/"

if not Path(config_path).exists():
    print(f"Config file not found at {config_path}")
    exit()

with open(config_path) as f:
    config = json.load(f)

dashboards = config["dashboard"]
dashboard_names = [elem["name"] for elem in dashboards]
dashboard_exec_map = {
    elem["name"]: {
        "exec": elem["exec"],
        "env_path": elem["env_path"] if "env_path" in elem else "",
    }
    for elem in dashboards
}

apps = config["apps"]
app_names = [elem["name"] for elem in apps]
app_exec_map = {
    elem["name"]: {
        "exec": elem["exec"],
        "env_path": elem["env_path"] if "env_path" in elem else "",
        "window_class": elem["window_class"] if "window_class" in elem else "",
        "single_instance": (
            elem["single_instance"] if "single_instance" in elem else False
        ),
    }
    for elem in apps
}

for elem in app_exec_map:
    if app_exec_map[elem]["single_instance"] and not app_exec_map[elem]["window_class"]:
        errors.ConfigError(
            "For single instance mode you also have to specify the class of the window"
        )

app_dirs = config["app_dirs"]

use_nixGL = config["use_nixGL"]
use_wal = config["use_wal"]
update_interval = float(config["update_interval"])

device = config["device"]
prompt = config["prompt"] if "prompt" in config else "> "

shell = config["shell"]
match shell:
    case "auto":
        if shutil.which("fish"):
            shell = "fish"
        elif shutil.which("zsh"):
            shell = "zsh"
        elif shutil.which("bash"):
            shell = "bash"
        else:
            errors.ShellError()
    case "fish":
        pass
    case "bash":
        pass
    case "zsh":
        pass
    case _:
        errors.ShellError()

default_commands = config["default_commands"] if "default_commands" in config else {}
