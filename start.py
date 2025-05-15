import os
import pathlib
import shutil
import argparse
import subprocess

from modules import read_conf


def main():
    parser = argparse.ArgumentParser(prog="lasso")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug. This keeps the alacritty window open, and shows errors.",
    )
    parser.add_argument(
        "-m",
        "--mode",
        help="Pass in the shorthand of a mode (eg. ':d' for dashboard mode) in which LASSO should start.",
    )
    parser.add_argument(
        "-n",
        "--network",
        action="store_true",
        help="Start the LASSO network selector instead of the launcher.",
    )
    parser.add_argument(
        "-b",
        "--bluetooth",
        action="store_true",
        help="Start the LASSO bluetooth selector instead of the launcher.",
    )
    args = parser.parse_args()

    if (args.network ^ args.bluetooth ^ (args.mode is None)) and not (
        args.network or args.bluetooth or (args.mode is None)
    ):
        print(
            'The parameters "-b/--bluetooth", "-n/--network" and "-m/--mode" are mutually exclusive!'
        )
        exit()

    init()

    exec_path = str(pathlib.Path(__file__).parent.resolve().joinpath("lasso.py"))
    if args.network and not (args.bluetooth or args.mode):
        exec_path = str(
            pathlib.Path(__file__).parent.resolve().joinpath("modules/network.py")
        )
    elif args.bluetooth and not (args.network or args.mode):
        exec_path = str(
            pathlib.Path(__file__).parent.resolve().joinpath("modules/bluetooth.py")
        )
    elif args.mode and not (args.bluetooth or args.network):
        exec_path = str(pathlib.Path(__file__).parent.resolve().joinpath("lasso.py"))

    args.mode = ":n" if args.mode is None else args.mode

    wal_command = [
        "kitty",
        "--title",
        "lasso",
        "--class",
        "lasso",
        "-c",
        f"/home/{read_conf.username}/.config/lasso/kitty.conf",
        "fish",
        "-c",
        f"wal -Rqn; python {exec_path} -m {args.mode}",
    ]
    no_wal_command = [
        "alacritty",
        "--title",
        "lasso",
        "--class",
        "lasso",
        "-c",
        f"/home/{read_conf.username}/.config/lasso/kitty.conf",
        "-e",
        "python",
        exec_path,
        "-m",
        args.mode,
    ]
    command = (
        wal_command if shutil.which("wal") and read_conf.use_wal else no_wal_command
    )

    if args.debug:
        command.insert(1, "--hold")
    if shutil.which("nixGL") and read_conf.use_nixGL:
        command.insert(0, "nixGL")

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    check_focus_lost(process)


def check_focus_lost(process):
    try:
        for line in process.stdout:
            if "Focused(false)" not in line:
                continue
            process.terminate()
            break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        process.stdout.close()
        process.stderr.close()
        process.wait()


def init():
    if os.path.isdir(f"/home/{os.getlogin()}/.config/lasso"):
        return
    shutil.copytree(
        os.path.join(os.path.dirname(__file__), "res"),
        f"/home/{os.getlogin()}/.config/lasso",
    )


if __name__ == "__main__":
    main()
