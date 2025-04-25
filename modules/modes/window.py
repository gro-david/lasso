import subprocess

COMMAND = ":w"
window_map = {}

# Window mode: Focus a window
def get_opt():
    global window_map

    window_data = subprocess.getoutput("niri msg windows")
    windows = window_data.split("\n\n")

    options = []
    window_map = {}

    for window in windows:
        lines = [line.strip() for line in window.split("\n") if line.strip()]
        window_id = next((line.split(" ", 2)[2].strip(":") for line in lines if line.startswith("Window ID")), None)
        title = next((line.split(": ", 1)[1] for line in lines if line.startswith("Title:")), None)
        title = str(title).replace('"', '')
        window_class = next((line.split(" ", 2)[2].strip(":") for line in lines if line.startswith("App ID")), None)
        window_class = str(window_class).replace('"', '').capitalize()

        if title == 'lasso': continue

        if window_id and title and window_class:
            options.append(f"{window_class} | {title}")
            window_map[f"{window_class} | {title}"] = window_id

    return COMMAND, options

def exec_selection(selection):
    if not selection in window_map: return

    window_id = window_map[selection]
    subprocess.run(f"niri msg action focus-window --id {window_id}", shell=True)
    exit()
