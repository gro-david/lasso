import subprocess

PREFIX = "w"
MODE = ":n"


def exec(selection):
    selection = selection.removeprefix(PREFIX).strip()
    if not selection.startswith("https://"):
        selection = f"https://{selection}"

    print(selection)

    subprocess.run([f"setsid xdg-open {selection}"], shell=True)
