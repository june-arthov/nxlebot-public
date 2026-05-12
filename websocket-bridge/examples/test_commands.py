#!/usr/bin/env python3
"""
Contoh kirim command dari Agent ke Unity / Unreal via WebSocket Bridge.

Usage:
  python3 test_commands.py

Pre-req:
  1. python3 bridge.py --port 8765  (jalan di terminal lain)
  2. Unity Play mode / Unreal running dengan client-nya konek ke ws://localhost:8765
"""

import asyncio
import sys
import json

# Import server bridge
sys.path.insert(0, "..")
from bridge import get_server, send_command


async def main():
    # Ganti ini kalau mau per-command atau broadcast manual
    server = get_server()

    print("═" * 50)
    print("Hermes Engine Bridge — Test Commands")
    print("═" * 50)

    # 1. Spawn object
    print("\n[1] Spawn Cube at (10, 0, 5)")
    try:
        r = await send_command("spawn", {"prefab_name": "Cube", "x": 10, "y": 0, "z": 5}, timeout=5)
        print(f"    ← {json.dumps(r, indent=2)}")
    except TimeoutError:
        print("    ⚠️ Timeout — pastikan Unity/Unreal konek ke bridge")

    # 2. Get FPS
    print("\n[2] Query FPS")
    try:
        r = await send_command("get_fps", {}, timeout=5)
        print(f"    ← {json.dumps(r, indent=2)}")
    except TimeoutError:
        print("    ⚠️ Timeout")

    # 3. Move camera
    print("\n[3] Move camera to (20, 15, -10)")
    try:
        r = await send_command("move_camera", {"x": 20, "y": 15, "z": -10}, timeout=5)
        print(f"    ← {json.dumps(r, indent=2)}")
    except TimeoutError:
        print("    ⚠️ Timeout")

    # 4. Create light
    print("\n[4] Create red point light at (0, 10, 0)")
    try:
        r = await send_command("create_light", {
            "light_type": "Point",
            "color": "#ff0000",
            "intensity": 1.5,
            "x": 0, "y": 10, "z": 0
        }, timeout=5)
        print(f"    ← {json.dumps(r, indent=2)}")
    except TimeoutError:
        print("    ⚠️ Timeout")

    # 5. Get all objects
    print("\n[5] Get all objects")
    try:
        r = await send_command("get_objects", {}, timeout=5)
        print(f"    ← {json.dumps(r, indent=2)}")
    except TimeoutError:
        print("    ⚠️ Timeout")

    print("\n[✓] Done.")


if __name__ == "__main__":
    asyncio.run(main())
