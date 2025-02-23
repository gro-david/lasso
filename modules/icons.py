dev_icons = {
	"audio-card": "󱡬",
	"audio-headphones": "󰋋",
	"audio-headset": "󰋎",
	"camera-photo": "",
	"camera-video": "",
	"computer": "󰇅",
	"input-gaming": "󰖺",
	"input-keyboard": "",
	"input-mouse": "󰍽",
	"input-tablet": "󰓷",
	"modem": "󱂇",
	"multimedia-player": "󰤽",
	"network-wireless": "󰑩",
	"phone": "",
	"printer": "󰐪",
	"scanner": "󰚫",
	"unknown": "",
	"video-display": "󰍹"
}
bat_icons = {
	0: "󰂃",
	10: "󰁺",
	20: "󰁻",
	30: "󰁼",
	40: "󰁽",
	50: "󰁾",
	60: "󰁿",
	70: "󰂀",
	80: "󰂁",
	90: "󰂂",
	100: "󰁹",
	-1: "󰂑"
}

def get_dev_icon(icon):
	return dev_icons[icon] if icon in dev_icons else bat_icons[-1]
	pass

def get_bat_icon(percentage):
	return bat_icons[percentage] if percentage in bat_icons else bat_icons[-1]
