# LASSO - LASSO Actively Simplifies System Operations
LASSO was designed to make my workflow with the [Niri](https://github.com/yalter/niri) WM more streamlined and efficient. It was inspired by a multi modal workflow, uniting an application launcher, a dashboard, and a window switcher. Additionally it includes a system bar. The main goal was simplicity and minimalism, which is accomplished by only relying on a terminal emulator to work.

## Features:
 - Fuzzy finding applications and launching them
 - Customization of dashboard commands, like network management, bluetooth, or a system monitor. Anything goes that has a shell or a TUI
 - Status in the launcher instead of a seperate bar, (eg: volume, battery, backlight or keyboard language)
 - Window switching in niri
 - Custom tools for managing Bluetooth and WiFi connections is included. The fit the theme and style of FUSE. The can be started by starting the respective files in the modules directory.

### Normal mode:
![image](https://github.com/user-attachments/assets/e6cb6053-d83e-4861-a44b-1a7244e94dec)

### Dashboard mode:
![image](https://github.com/user-attachments/assets/ff06e4b8-7934-4751-a369-c6e6b1e7b8fa)

### Window mode:
![image](https://github.com/user-attachments/assets/7f59e193-4eb1-40f6-922b-1adbe0f84d8e)


## Requirements:
 - niri, window switching and keyboard language display depend on the niri compositor and use `niri msg`
 - alacritty, alacritty is used as the terminal emulator and is started by `start.py` with the launcher running (you _could_ use another terminal emulator, but you will need to change `start.py`)
 - pactl, for displaying the volume
 - python-psutil, for showing battery information in the header bar
 - fzf, for the whole program to even work
 - nerdfont, to display the icons in the status bar correctly
 - fish, this is the shell for which this was written. it is probably possible to port to other shells, but I did not have the time up until now.

## How to use:
 -  Add the following rule to your niri config file:
	```
	window-rule {
		match title="lasso" app-id="lasso"
		open-focused true
		open-floating true
	}
	```
 - Add a binding somewhere in your niri config to start the `python start.py`
 - The launcher starts in normal mode. You can switch to dashboard mode by selecting the entry `:d`, using `:w` will switch you to window mode
 - In any mode you can exit the launcher `:q` or return to normal mode with `:n`.
 - Pressing Esc selecting a entry in normal or window mode or defocusing the window will close it

## How it works
 - In normal mode .desktop files will be parsed from all of the usual locations, their name will be displayed, when selected the binary defined in their Exec field will be executed
 - In window mode the launcher will get all open windows using `niri msg windows` and will switch to the selected one with `niri msg action focus-window --id <id>`
 - In dashboard mode your entries will be parsed and the `exec` field of the selected one will be executed. You should either use a TUI or a shell in your exec field.

## Installation
On most distros you will be able to use the launcher by just cloning the repo and then running the `start.py` file

For Arch Linux, just install the lasso-launcher package from the AUR.

## Documentation
After installing you should be able to start the program by executing the `start.py` file or on Nix/Arch by executing the `lasso` command.
The configuration is written in plain json and can is usually found under `~.config/lasso/lasso.json`. The following options are available:
  - `"use_nixGL": boolean`, whether to execute processes with nixGL. (deprecated, will be removed soon)
  - `"use_wal": boolean`, whether to execute wal after starting alacritty. Required to have your terminal correctly colored.
  - `"update_interval": float`, how often to update the system bar (secs)
  - `"device": string`, which device to use for wireless network configuration.
  - `"shell": (auto|fish|bash|zsh)`, set the shell to use, must be exactly one of the four options.
  - `"app_dirs": []`, This list of the directories that LASSO will look for applications. If this options is omitted the usual locations will be crawled. If this option is present _only_ the listed directories will be crawled. To disable automatically loading .desktop files, include this option but leave the list empty.
  - `"apps": []`, This should contain all applications that you want to manually add to LASSO. They should have the following format:
    - `{ "env_path": "", "exec": "", "name": "" }`:
      - `"env_path"` is a string representing the PATH environment variable.
      - `"exec"` is the command which will be executed.
      - `"name"` is the display name that will be shown.
  - `"dashboard": []`, This is a list containing anything that should be included in your dashboard. It uses the same format as the applications.

LASSO is designed to be hackable. You can customize a few things up to now, with more coming in the future. If there is anything you would like to customize but is not customizable, please open an issue.

These user provided modifications are called hacks and should be placed under `~/.config/lasso/hacks`. For now there are two types of hacks: modes and top_bar. If you would like to customize the status bar shown in LASSO create a file called `top_bar.py` and place it in the root of the hacks directory. Please do _NOT_ remove or modify the `__init__.py` and `system.py` files. These are required for the basic functionality of LASSO.

Your `top_bar.py` only needs to include a method `get()` which should return your desired system bar. This function will be called automatically multiple times by LASSO, so you do not need to do anything else.

Creating modes is also relatively simple and done in python. These will be loaded from `~/.config/lasso/hacks/modes`. Please do _NOT_ remove or modify the `__init__.py` file located in this directory, as this will break the loading of these hacks.

Each mode should include a constant variable called `COMMAND` which will be the command used to switch to this mode. It usually starts with a colon (:) and is only a single letter, but there is nothing stopping you of naming it something else.

There are two methods required by LASSO. `get_opt()` should return `COMMAND` and a list of options that should be selectable. `exec_selection(selection)` will be called by FUSE when the user selects an entry. This should only handle your custom options, you do not need to include handling of mode switching commands.

In LASSO there is support for custom commands. These are expressions written in the input field of one of the modes. These can be created under `~/.config/lasso/hacks/commands/`. There are three things that must be defined. These are the constants `PREFIX` and `MODE`, which define in which mode the command can be used and what needs to be prepended to the command that one wants to execute. `MODE` can be defined as `"any"`, which will make the command available in all modes. 

A function called `exec(selection)` is also required which will receive the command (stripped and without the prefix) from `lasso.py`, which will have to execute your desired program. It is recommended to execute the program with `setsid` as otherwise it will terminate as soon as LASSO is closed. 

Example top bar:
```python
def get():
  return "This is my system bar"
```

Example mode:
```python
COMMAND = ":e"

def get_opt():
  return COMMAND, [1, 2, 3]

def exec_selection(selection):
  match selection:
    3: print("You selected the number 3")
    _: print(selection)
```
Example command:
```python
PREFIX = ">"
MODE = "any"

def exec(selection):
  print(selection)
```
```
```
```
