import argparse
import subprocess
from pathlib import Path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Follow a logfile and filter output")
    parser.add_argument("logfile", help="Path to the logfile to follow")
    parser.add_argument("--filter", help="Optional filter string", default=None)

    args = parser.parse_args()

    logfile = Path(args.logfile)

    # If relative → make it relative to the working directory
    if not logfile.is_absolute():
        logfile = Path.cwd() / logfile
    logfile = logfile.resolve()

    if not logfile.exists():
        raise AttributeError(f"Logfile does not exist: {logfile}")

    process = subprocess.Popen(
        ["tail", "-f", args.logfile],
        stdout=subprocess.PIPE,
        text=True
    )

    for line in process.stdout:
        if args.filter is None or args.filter in line:
            print(line, end="")
