import os
import math
import icons
import subprocess
from rich.console import Console

def run_fzf(options, mode):
	fzf_input = "\n".join(options)
	terminal_width = os.get_terminal_size().columns
	padding = math.floor((terminal_width - len(mode)) / 2)
	preview_text = (" " * padding) + mode

	fzf_command = (
            "fzf --header-lines=0 --no-info "
            f"--preview 'echo \"{preview_text}\"' "
            "--preview-window=up:1:follow:wrap:noinfo"
        )
	result = subprocess.run(fzf_command, input=fzf_input, shell=True, capture_output=True, text=True)
	return result.stdout.strip()


def normal_mode():
	def parse_devices():
		result = subprocess.run(
			["bluetoothctl", "devices", "Paired"],
			capture_output=True,
			text=True
		)
		macs = [line.split()[1] if not len(line.split()) <= 1 else None for line in result.stdout.split("\n")]
		devices = {}

		for mac in macs:
			if mac == None: continue
			devices[mac] = get_device_info(mac)

		return devices

	devices = parse_devices()
	options, connect_map = format_devices(devices)

	if not ":q" in options: options.extend([":q", ":s", ":d", ":r"])
	selection = run_fzf(options, '[NORMAL]')

	match selection:
		case ":q": exit()
		case ":s": scan_mode()
		case ":d": delete_mode()
		case ":r": normal_mode()
		case _:
			if not selection in connect_map: exit()
			if selection.startswith("*"): subprocess.run(["bluetoothctl", "disconnect", connect_map[selection]])
			else: subprocess.run(["bluetoothctl", "connect", connect_map[selection]])


def scan_mode():
	def parse_devices():
		# print("Scanning...")
		console = Console()
		result = None
		with console.status("Scanning..."):
			result = subprocess.run(
				["bluetoothctl", "--timeout", "5", "scan", "on"],
				capture_output=True,
				text=True
			)
		lines = [line if "NEW" in line else None for line in result.stdout.split("\n")]
		devices = {}

		for line in lines:
			if line == None: continue
			line = line.split()
			devices[line[2]] = get_device_info(line[2])

		return devices

	devices = parse_devices()
	options, connect_map = format_devices(devices)

	if not ":q" in options: options.extend([":q", ":n", ":d", ":r"])
	selection = run_fzf(options, "[SCAN]")

	match selection:
		case ":q": exit()
		case ":n": normal_mode()
		case ":d": delete_mode()
		case ":r": scan_mode()
		case _:
			if not selection in connect_map: exit()
			subprocess.Popen(["bluetoothctl", "-t", "1", "-a", "NoInputOutput", "agent", "on"])
			subprocess.run(["bluetoothctl", "pair", connect_map[selection]], stdout=subprocess.DEVNULL)
			subprocess.run(["bluetoothctl", "trust", connect_map[selection]], stdout=subprocess.DEVNULL)
			subprocess.run(["bluetoothctl", "connect", connect_map[selection]], stdout=subprocess.DEVNULL)
			normal_mode()

def delete_mode():
	def parse_devices():
			result = subprocess.run(
				["bluetoothctl", "devices", "Paired"],
				capture_output=True,
				text=True
			)
			macs = [line.split()[1] if not len(line.split()) <= 1 else None for line in result.stdout.split("\n")]
			devices = {}

			for mac in macs:
				if mac == None: continue
				devices[mac] = get_device_info(mac)

			return devices

	devices = parse_devices()
	options, remove_map = format_devices(devices)

	if not ":q" in options: options.extend([":q", ":s", ":n", ":r"])
	selection = run_fzf(options, "[DELETE]")

	match selection:
		case ":q": exit()
		case ":s": scan_mode()
		case ":n": normal_mode()
		case ":r": delete_mode()
		case _:
			if not selection in remove_map: exit()
			subprocess.run(["bluetoothctl", "remove", remove_map[selection]], stdout=subprocess.DEVNULL)
			delete_mode()

def get_device_info(mac):
	result = subprocess.run(
		["bluetoothctl", "info", mac],
		capture_output=True,
		text=True
	)
	lines = result.stdout.split("\n")

	info = {}
	for line in lines:
		line = line.split(":")

		if len(line) <= 1: continue
		if line[0].strip() == "Icon": info["icon"] = line[1].strip()
		if line[0].strip() == "Connected": info["connected"] = True if line[1].strip() == "yes" else False
		if line[0].strip() == "Name": info["name"] = line[1].strip()
		if line[0].strip() == "Battery Percentage": info["bat"] = round(int(line[1].split()[1].strip().removeprefix("(").removesuffix(")")), -1)

	if not "icon" in info: info["icon"] = "unknown"
	if not "name" in info: info["name"] = ""
	if not "bat" in info: info["bat"] = -1

	return info
def format_devices(devices):
		options = []
		connect_map = {}

		longest_name_length = 0
		for device in devices:
			if len(devices[device]["name"]) > longest_name_length: longest_name_length = len(devices[device]["name"])

		for device in devices:
			mac = device
			name = devices[device]["name"]
			connected = "*" if devices[device]["connected"] else " "
			icon = devices[device]["icon"]
			battery = devices[device]["bat"]
			battery_text = f"{(3 - (len(str(battery)) if battery >= 0 else 0)) * ' '}{battery if battery >= 0 else ''}{"%" if battery >= 0 else ' '}"

			option = f" {connected}   {icons.get_dev_icon(icon)}   {name}{(longest_name_length - len(name)) * ' '}   {icons.get_bat_icon(battery)} {battery_text}   ({mac})"

			options.append(option)
			connect_map[option.strip()] = mac

		return options, connect_map
def setup():
	subprocess.run(["bluetoothctl", "power", "on"], stdout=subprocess.DEVNULL)
	subprocess.run(["bluetoothctl", "discoverable", "on"], stdout=subprocess.DEVNULL)
	subprocess.run(["bluetoothctl", "pairable", "on"], stdout=subprocess.DEVNULL)

if __name__ == "__main__":
	setup()
	normal_mode()
