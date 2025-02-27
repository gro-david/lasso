# DO NOT MODIFY THIS FILE
# This file is responsible for being able to use any hacks, and for the fallback behavior of the top bar.
# If you do modify this, it could result in a non working installation of FUSE.
# For creating hacks, please check out the documentation on GitHub https://github.com/gro-david/fuse

import time
import glob
from os.path import dirname, basename, isfile, join

# define what should be imported
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')] # type: ignore

# import all hacks the user made
from . import *
from .modes import *

def get_fallback_top_bar():
	time_now = time.strftime("%Y-%m-%d %H:%M:%S")
	brightness = system.get_brightness() # type: ignore
	volume = system.get_volume() # type: ignore
	percentage, plugged, remaining = system.get_battery_state() # type: ignore
	remaining = f"󱧥 {time.strftime('%H:%M:%S', time.gmtime(remaining))}" if not remaining == -2 else ''
	charging = '󰚥' if plugged else '󰚦'
	keyboard_layout = system.get_keyboard() # type: ignore

	top_bar = f"󰥔 {time_now} | 󰃟 {brightness}% | 󰌌 {keyboard_layout} |  {volume}% | 󱐋 {percentage}% {remaining} {charging} "
	return top_bar
