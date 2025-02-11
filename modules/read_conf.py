import os
from pathlib import Path
import json

username = os.getlogin()
config_path = f"/home/{username}/.config/launcher.json"
#config_path = f"/home/macisajt/launcher/launcher.json"

if not Path(config_path).exists():
    print(f"Config file not found at {config_path}")
    exit()

with open(config_path) as f:
    config = json.load(f)

dashboards = config["dashboard"]
dashboard_names = [elem["name"] for elem in dashboards]
dashboard_exec_map = {elem["name"]: elem["exec"] for elem in dashboards}

apps = config["apps"]
app_names = [elem["name"] for elem in apps]
app_exec_map = {elem["name"]: elem["exec"] for elem in apps}

app_dirs = config["app_dirs"]
