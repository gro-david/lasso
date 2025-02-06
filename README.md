# Launcher
This is my quick and dirty fzf based keyboard application launcher, dashboard, and window switcher. It was designed to work with the niri wayland compositor.

## Features:
 - Fuzzy finding applications and launching them
 - Customization of dashboard commands, like network management, bluetooth, or a system monitor. Anything goes that has a shell or a TUI
 - Status in the launcher instead of a seperate bar, (eg: volume, battery, backlight or keyboard language)
 - Window switching in niri

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
		match title="alacritty launcher"
		open-focused true
		open-floating true
	}
	```
 - Add a binding somewhere in your niri config to start the `python start.py`
 - Customize the entries in your dashboard using ~/.config/launcher.json it should look this way:
 ```
 [
 	{
 		"name": "name of the entry",
      		"exec": "command to execute"
    	}
 ]
 ```
 - The launcher starts in normal mode. You can switch to dashboard mode by selecting the entry `:d`, using `:w` will switch you to window mode
 - In any mode you can exit the launcher `:q` or return to normal mode with `:n`.
 - Pressing Esc selecting a entry in normal or window mode or defocusing the window will close it

## How it works
 - In normal mode .desktop files will be parsed from all of the usual locations, their name will be displayed, when selected the binary defined in their Exec field will be executed
 - In window mode the launcher will get all open windows using `niri msg windows` and will switch to the selected one with `niri msg action focus-window --id <id>`
 - In dashboard mode your entries will be parsed and the `exec` field of the selected one will be executed. You should either use a TUI or a shell in your exec field.

## Installation
On most distros you will be able to use the launcher by just cloning the repo and then running the `start.py` file

On NixOS this should work too, but you can also use home-manager. You can just import the two files into home-manager. You can configure the dashboard using `launcher.nix`, a few entries will already be included by default. Then just rebuild your home. This will use the `nix` branch which already has some things set up to work with NixOS.
