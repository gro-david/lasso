{ pkgs, ... }:
{
	programs.launcher = {
		enable = true;
		dashboard = [
			{
				name = "Reboot";
				exec = "reboot";
			}
			{
				name = "Suspend";
				exec = "systemctl suspend";
			}
			{
				name = "Rebuild";
				exec = "sudo nixos-rebuild switch";
			}
			{
				name = "Collect Garbage";
				exec = "sudo nix-collect-garbage -d && nix-collect-garbage";
			}
		];
	};
}
