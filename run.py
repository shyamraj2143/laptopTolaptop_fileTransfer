from __future__ import annotations
import argparse
from app.agent import run_agent
from app.gui import run as run_gui

def main() -> None:
    parser = argparse.ArgumentParser(description="DirectDrop")
    parser.add_argument("--agent", action="store_true")
    parser.add_argument("--gui", action="store_true")
    args = parser.parse_args()
    if args.agent:
        run_agent()
    else:
        run_gui()

if __name__ == "__main__":
    main()
