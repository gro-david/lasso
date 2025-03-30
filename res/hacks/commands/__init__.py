# This file is responsible for being able to use any hacks, and for the fallback behavior of the top bar.
# If you do modify this, it could result in a non working installation of LASSO.
# For creating hacks, please check out the documentation on GitHub https://github.com/gro-david/lasso

import sys
import glob
from os.path import dirname, basename, isfile, join

# define what should be imported
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [
    basename(f)[:-3] for f in modules if isfile(f) and not f.endswith("__init__.py")
]  # type: ignore

# import all modes the user made
from . import *


class CommandExistsException(Exception):
    def __init__(self):
        self.message = "This command already exists. Check your hacks."
        super().__init__(self.message)


commands = {}
for module in __all__:
    for cmd in sys.modules[f"hacks.commands.{module}"].PREFIXES:
        for mode in sys.modules[f"hacks.commands.{module}"].MODES:
            exec = sys.modules[f"hacks.commands.{module}"].exec
            if (mode, cmd) in commands:
                raise CommandExistsException()

            commands[(mode, cmd)] = exec
