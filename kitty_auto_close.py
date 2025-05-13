from typing import Any
from kitty.boss import Boss
from kitty.window import Window


def on_load(boss: Boss, data: dict[str, Any]) -> None:
    # optional: print to STDERR to confirm load
    print("auto_close watcher loaded")


def on_focus_change(boss: Boss, window: Window, data: dict[str, Any]) -> None:
    if not data.get("focused", False):
        window.close()
