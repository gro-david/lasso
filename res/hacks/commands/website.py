import subprocess

PREFIX = ["w"]
MODE = [":n"]


def exec(selection):
    if not selection.startswith("https://"):
        selection = f"https://{selection}"

    subprocess.run([f"setsid xdg-open {selection}"], shell=True)
