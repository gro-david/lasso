# DO NOT MODIFY THIS FILE
# This file is responsible for being able to use any hacks, and for the fallback behavior of the top bar.
# If you do modify this, it could result in a non working installation of FUSE.
# For creating hacks, please check out the documentation on GitHub https://github.com/gro-david/fuse

import subprocess
import os
import glob
import psutil

def get_volume():
    result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'], stdout=subprocess.PIPE)
    output = result.stdout.decode()
    # Extract the volume percentage from the output
    volume_line = [line for line in output.split('\n') if 'Volume:' in line]
    if volume_line:
        volume = volume_line[0].split()[4].strip('%')
        return int(volume)
    return None

def get_brightness():
    # Find the correct backlight path
    backlight_paths = glob.glob('/sys/class/backlight/*/brightness')
    if not backlight_paths:
        print("No backlight path found")
        return None

    brightness_path = backlight_paths[0]
    max_brightness_path = brightness_path.replace('brightness', 'max_brightness')

    # Read the brightness and max brightness values
    try:
        with open(brightness_path, 'r') as file:
            brightness = int(file.read().strip())

        with open(max_brightness_path, 'r') as file:
            max_brightness = int(file.read().strip())

        # Calculate the brightness level as a percentage
        brightness_level = round((brightness / max_brightness) * 100, 2)
        return brightness_level
    except FileNotFoundError:
        print("Brightness file not found")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_battery_state():
    battery = psutil.sensors_battery()
    if battery:
        return round(battery.percent, 2), battery.power_plugged, battery.secsleft
    return None, None, None

def get_keyboard():
    result = subprocess.run(['niri', 'msg', 'keyboard-layouts'], stdout=subprocess.PIPE)
    output = result.stdout.decode()
    line = [line for line in output.split('\n') if '*' in line][0]
    line = line.translate(str.maketrans('*0123456789', ' ' * 11))
    line = line.strip()
    return line
