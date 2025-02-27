# This file is responsible for being able to use any hacks, and for the fallback behavior of the top bar.
# If you do modify this, it could result in a non working installation of FUSE.
# For creating hacks, please check out the documentation on GitHub https://github.com/gro-david/fuse

import glob
from os.path import dirname, basename, isfile, join
import sys

# define what should be imported
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')] # type: ignore

# import all modes the user made
from . import *

class ModeExistsException(Exception):
	def __init__(self):
		self.message = "This mode already exists. Check your hacks."
		super().__init__(self.message)

modes = {}
for module in __all__:
	cmd = sys.modules[f"hacks.modes.{module}"].COMMAND
	opt = sys.modules[f"hacks.modes.{module}"].get_opt
	exec = sys.modules[f"hacks.modes.{module}"].exec_selection

	if cmd in modes: raise ModeExistsException()

	modes[cmd] = {"opt": opt, "exec": exec}
