# ━━━ Hermes WebSocket Bridge ━━━
## Agent ↔ Unity / Unreal Real-time Link

### Struktur
```
websocket-bridge/
├── server/
│   └── bridge.py              ── Server bridge (Python)
├── unity/
│   └── HermesWebSocketClient.cs ── Unity MonoBehaviour
├── unreal/
│   ├── HermesWebSocket.*       ── Unreal C++ module
│   └── README_Unreal.md        ── Panduan setup C++
└── examples/
    └── test_commands.py        ── Contoh kirim command dari agent
```

### 1️⃣ Jalankan Server
```bash
cd server
pip install websockets   # kalau belum
python3 bridge.py --port 8765
```
→ Output: `🚀 Bridge server running on ws://0.0.0.0:8765`

### 2️⃣ Unity Setup
1. Install `WebSocket-Sharp` via NuGet / Unity Package Manager:
   - Git URL: `https://github.com/sta/websocket-sharp.git`
2. Taruh `HermesWebSocketClient.cs` di folder `Assets/Scripts/`
3. Buat GameObject kosong → nama "HermesBridge"
4. Attach script `HermesWebSocketClient.cs`
5. Play → liat Console "[Hermes] Connected"

### 3️⃣ Kirim Command dari Agent
```bash
python3 examples/test_commands.py
```
Atau dari Python REPL:
```python
import asyncio
from bridge import get_server, send_command

async def demo():
    server = get_server()
    # Kirim command ke semua engine yang konek
    result = await send_command("spawn", {"prefab_name": "Enemy", "x": 10, "y": 0, "z": 5})
    print(result)   # {'status': 'spawned', 'name': 'Enemy'}

    result = await send_command("get_fps")
    print(result)   # {'fps': 144.0}

asyncio.run(demo())
```

### 4️⃣ Protocol Message Format

**Agent → Engine:**
```json
{ "type": "command", "id": "uuid", "action": "spawn",
  "params": {"prefab_name": "Cube", "x": 0, "y": 5, "z": 0} }
```

```json
{ "type": "query", "id": "uuid", "action": "get_objects", "params": {} }
```

**Engine → Agent:**
```json
{ "type": "register", "engine": "unity", "version": "2022.3" }
```

```json
{ "type": "response", "id": "uuid", "result": {"status": "ok"} }
```

### 5️⃣ Commands Supported

| Command | Params | Unity Action |
|-----------|--------|-------------|
| `spawn` | `prefab_name`, `x`, `y`, `z` | Instantiate prefab |
| `move_camera` | `x`, `y`, `z` | Set Camera.main.position |
| `destroy_all` | — | Destroy all objects tagged "AgentSpawned" |
| `set_material_color` | `object_name`, `color` (hex) | Set renderer.material.color |
| `create_light` | `light_type`, `color`, `intensity`, `x`, `y`, `z` | Add Light component |
| `get_objects` | — | Return all GameObject names |
| `get_fps` | — | Return current FPS |

### 6️⃣ Extend

Tambah command baru di Unity: edit method `HandleCommand()` di `HermesWebSocketClient.cs`.
Tambah handler baru di Python: `server.on("event_name", callback)`.

### Port Default
- Server: **8765**
- Ganti di `--port` flag server dan di Unity Inspector `serverUrl`.
