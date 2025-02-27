import subprocess

def run_fzf(options):
	fzf_input = "\n".join(options)
	result = subprocess.run("fzf", input=fzf_input, shell=True, capture_output=True, text=True)
	return result.stdout.strip()

def main(options, connect_map):
	if not ":q" in options: options.append(":q")
	selection = run_fzf(options)
	if selection == ":q":
		exit()
	elif selection in connect_map:
		subprocess.run(["nmcli", "device", "wifi", "connect", connect_map[selection], "--ask"])

def parse_networks():
	result = subprocess.run(
		["nmcli", "device", "wifi", "list"],
		capture_output=True,
		text=True
	)
	lines = [" ".join(line.split()) for line in result.stdout.split("\n")]
	lines.pop(0)

	networks = {}
	for line in lines:
		active = "*" in line
		line = line.removeprefix("*")

		line = line.split()
		if len(line) <= 8: continue

		name_end_index = line.index("Infra") - 1

		bssid = line[0]
		name = " ".join([line[i] for i in range(1, name_end_index)])
		bars = line[name_end_index + 6]
		security = line[name_end_index + 7]

		if name == "--": continue
		if not name in networks or (not networks[name]["active"] and active):
			networks[name] = {"active": active, "bssid": bssid, "bars": bars, "security": security}

	return networks

def format_networks(networks):
	options = []
	connect_map = {}

	longest_ssid_length = 0
	for name in networks:
		if not len(name) > longest_ssid_length: continue
		longest_ssid_length = len(name)


	for name in networks:
		network = networks[name]

		option = ""
		option += " * " if network["active"] else "   "
		option += name + " " * (longest_ssid_length - len(name))
		option += "   "
		option += network["bars"]
		option += "   "
		option += network["security"]

		options.append(option)
		connect_map[option.strip()] = network["bssid"]

	return options, connect_map


def start():
	networks = parse_networks()
	options, connect_map = format_networks(networks)
	main(options, connect_map)

start()
