import subprocess
import sys
import pathlib
import shutil

def main():
    if shutil.which("nixGL"):
        subprocess.run(
            [ 'nixGL', 'alacritty', '-T', 'fuse', '--print-events', '-e', 'python', str(pathlib.Path(__file__).parent.resolve().joinpath('fuse.py')) ],
            capture_output=True,
            text=True
        )
    else:
        subprocess.run(
                ['alacritty', '-T', 'fuse', '--print-events', '-e', 'python', str(pathlib.Path(__file__).parent.resolve().joinpath('fuse.py')) ],
                capture_output=True,
                text=True
        )



if __name__ == "__main__":
    main()
