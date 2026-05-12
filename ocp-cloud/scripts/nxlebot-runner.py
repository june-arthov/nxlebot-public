#!/usr/bin/env python3
"""
OC+ Runner — dipanggil Hermes cronjob atau langsung.
Usage: python3 nxlebot-runner.py <script_name>
Script dicari di ../examples/ relatif dari runner.
"""

import sys, json, subprocess, os

def main():
    if len(sys.argv) < 2:
        print("Usage: nxlebot-runner.py <script_name>")
        sys.exit(1)

    script_name = sys.argv[1]
    if not script_name.endswith('.ocp'):
        script_name += '.ocp'

    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'examples')
    script_path = os.path.join(script_dir, script_name)

    if not os.path.exists(script_path):
        print(f"Script '{script_name}' gak ditemukan di {script_dir}")
        sys.exit(1)

    with open(script_path) as f:
        script_content = f.read()

    payload = json.dumps({"script": script_content})
    result = subprocess.run(
        ['curl', '-s', '-X', 'POST', 'http://localhost:8000/execute',
         '-H', 'Content-Type: application/json',
         '-d', payload],
        capture_output=True, text=True, timeout=30
    )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Gagal parse response: {result.stdout[:200]}")
        sys.exit(1)

    status = data.get('status', 'error')
    output = data.get('output', 'no output')
    exit_code = data.get('exit_code', -1)

    print(f"*OC+ {script_name}*\n")
    print(f"Status: `{status}` (exit: {exit_code})")
    print(f"```\n{output[:3000]}\n```")

if __name__ == '__main__':
    main()
