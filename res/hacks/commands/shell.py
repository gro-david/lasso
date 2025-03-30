import subprocess

PREFIX = [">"]
MODE = [":n"]


def exec(selection):
    command = f"setsid {selection} > /dev/null 2>&1 &"
    subprocess.run(command, shell=True, capture_output=True, text=True)
    return
