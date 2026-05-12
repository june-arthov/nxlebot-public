"""CLI entry point: `python -m ocplus` or `ocp` command"""

import sys
from .interpreter import run_file


def main():
    if len(sys.argv) < 2:
        print("Usage: ocp <script.ocp>", file=sys.stderr)
        print("       python -m ocplus <script.ocp>", file=sys.stderr)
        sys.exit(1)

    run_file(sys.argv[1])


if __name__ == "__main__":
    main()
