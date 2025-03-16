import re
import subprocess

import read_conf

def run_fzf(options):
    fzf_input = "\n".join(options)
    result = subprocess.run("fzf", input=fzf_input, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def main(options, connect_map, networks):
    if not ":q" in options: options.extend([":q", ":r", ":c"])
    selection = run_fzf(options)
    if selection == ":q": exit()
    elif selection == ":r": normal_mode()
    elif selection == ":c":
        subprocess.run(["iwctl"])
        normal_mode()
    elif selection in connect_map:
        if networks[connect_map[selection]]["active"]:
            subprocess.run(["iwctl", "station", read_conf.device, "disconnect", connect_map[selection]])
        else:
            subprocess.run(["iwctl", "station", read_conf.device, "connect", connect_map[selection]])

def parse_networks():
    result = subprocess.run(
        ["iwctl", "station", read_conf.device, "get-networks"],
        capture_output=True,
        text=True
    )

    lines = [re.sub(r'\x1b\[[0-9;]*m', '', re.sub(r'\x1b\[[0-9;]*m(\*+)\x1b\[0m', lambda m: '-' * len(m.group(1)), line)).strip().split() for line in result.stdout.splitlines()]
    while [] in lines: lines.remove([])
    for i in range(4): lines.pop(0)

    networks = {}
    for line in lines:
        active = line[0] == ">"
        if active: line.pop(0)
        signal = line.pop(-1)
        security = line.pop(-1)
        name = " ".join(line)
        networks[name] = {"active": active, "signal": signal, "security": security}

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
        option += network["signal"]
        option += "   "
        option += network["security"]

        options.append(option)
        connect_map[option.strip()] = name

    return options, connect_map

def setup():
    subprocess.run(["iwctl", "device", read_conf.device, "set-property", "Powered", "on"])
    subprocess.run(["iwctl", "station", read_conf.device, "scan"])

def normal_mode():
    networks = parse_networks()
    options, connect_map = format_networks(networks)
    main(options, connect_map, networks)

setup()
normal_mode()
