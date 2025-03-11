import os
from pathlib import Path
import json

username = os.getlogin()
config_path = f"/home/{username}/.config/lasso/lasso.json"
hacks_path = f"/home/{username}/.config/lasso/"
# config_path = f"/home/macisajt/Data/python-projects/fuse/conf/fuse.json"
# hacks_path = f"/home/macisajt/Data/python-projects/fuse/fuse/"

if not Path(config_path).exists():
    print(f"Config file not found at {config_path}")
    exit()

with open(config_path) as f:
    config = json.load(f)

dashboards = config["dashboard"]
dashboard_names = [elem["name"] for elem in dashboards]
dashboard_exec_map = {elem["name"]: {"exec": elem["exec"], "env_path": elem["env_path"]} for elem in dashboards}

apps = config["apps"]
app_names = [elem["name"] for elem in apps]
app_exec_map = {elem["name"]: {"exec": elem["exec"], "env_path": elem["env_path"]} for elem in apps}

app_dirs = config["app_dirs"]
