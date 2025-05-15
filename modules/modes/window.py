import json
import subprocess

COMMAND = ":w"
window_map = {}


# Window mode: Focus a window
def get_opt():
    global window_map

    window_data_raw = subprocess.getoutput("niri msg --json windows")
    window_data = json.loads(window_data_raw)
    print(window_data)

    options = []
    window_map = {}

    for window in window_data:
        window_id = window["id"]
        title = window["title"]
        window_class = window["app_id"]
        window_class = str(window_class).replace('"', "").capitalize()

        if title == "lasso":
            continue

        if window_id and title and window_class:
            options.append(f"{window_class} | {title}")
            window_map[f"{window_class} | {title}"] = window_id

    return COMMAND, options


def exec_selection(selection):
    if selection not in window_map:
        return

    window_id = window_map[selection]
    subprocess.run(f"niri msg action focus-window --id {window_id}", shell=True)
    exit()
