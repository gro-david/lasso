import os
import json
import shutil
from pathlib import Path

try:
    import errors
except Exception as e:
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
dashboard_exec_map = {elem["name"]: {"exec": elem["exec"], "env_path": elem["env_path"] if "env_path" in elem else ""} for elem in dashboards}

apps = config["apps"]
app_names = [elem["name"] for elem in apps]
app_exec_map = {elem["name"]: {"exec": elem["exec"], "env_path": elem["env_path"] if "env_path" in elem else ""} for elem in apps}

app_dirs = config["app_dirs"]

use_nixGL = config["use_nixGL"]
use_wal = config["use_wal"]
update_interval = float(config["update_interval"])

device = config["device"]

shell = config["shell"]
match shell:
    case "auto":
        if shutil.which("fish"): shell = "fish"
        elif shutil.which("zsh"): shell = "zsh"
        elif shutil.which("bash"): shell = "bash"
        else:
            errors.ShellError()
    case "fish": pass
    case "bash": pass
    case "zsh": pass
    case _:
        errors.ShellError()

execute_commands = config["execute_commands"]
