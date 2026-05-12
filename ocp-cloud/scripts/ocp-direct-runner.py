#!/usr/bin/env python3
"""
OC+ Direct Runner — jalanin script OC+ langsung di host (tanpa Docker).
Khusus internal automation. Fast, no overhead.

Usage: python3 ocp-direct-runner.py <script_name>
"""

import sys, os, subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: ocp-direct-runner.py <script_name>")
        sys.exit(1)

    script_name = sys.argv[1]
    if not script_name.endswith('.ocp'):
        script_name += '.ocp'

    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'examples')
    script_path = os.path.join(script_dir, script_name)

    if not os.path.exists(script_path):
        print(f"Script '{script_name}' gak ditemukan di {script_dir}")
        sys.exit(1)

    interpreter = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sandbox', 'ocp_interpreter.py')

    result = subprocess.run(
        ['python3', interpreter, script_path],
        capture_output=True, text=True, timeout=60,
        cwd=os.path.expanduser('~')
    )

    exit_ok = result.returncode == 0
    status = "success" if exit_ok else "failed"

    output = result.stdout.strip() or "(empty)"
    errors = result.stderr.strip()

    print(f"*OC+ {script_name}*\n")
    print(f"Status: `{status}` (exit: {result.returncode})")
    print("```")
    print(output)
    if errors:
        print("\n--- stderr ---")
        print(errors)
    print("```")

if __name__ == '__main__':
    main()
