import subprocess

prefix = "w"


def exec(selection):
    selection = selection.removeprefix(prefix).strip()
    if not selection.startswith("https://"):
        selection = f"https://{selection}"

    print(selection)

    subprocess.run([f"setsid xdg-open {selection}"], shell=True)
