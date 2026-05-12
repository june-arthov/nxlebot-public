#!/usr/bin/env python3
"""
Hermes WebSocket Bridge — Agent ↔ Engine Real-time Link

Jalanin server ini dari agent:
  python3 bridge.py --port 8765

Unity / Unreal konek ke ws://localhost:8765
Protocol: JSON message {type, ...}

Supported message types:
  engine → agent
    { type: "register", engine: "unity|unreal", version: "2023.1" }
    { type: "status",   data: {...} }           # telemetry
    { type: "event",    name: "player_death", data: {...} }
    { type: "response", id: "uuid", result: {...} }

  agent → engine
    { type: "command", id: "uuid", action: "spawn", params: {...} }
    { type: "query",   id: "uuid", action: "get_objects", params: {...} }
    { type: "config",  set: {"skybox_color": "#ff0000"} }

Usage from agent:
  1. Start server:  python3 bridge.py
  2. Send command:   curl or websocket client to ws://localhost:8765

Or import:
  from bridge import BridgeServer, send_command
"""

import asyncio
import json
import uuid
import logging
import argparse
from typing import Callable, Any
from collections.abc import Awaitable

logger = logging.getLogger("hermes-ws-bridge")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")

Handler = Callable[[str, dict, Any], Awaitable[None]]


class BridgeServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: set[Any] = set()
        self.handlers: dict[str, list[Handler]] = {}
        self.pending: dict[str, asyncio.Future] = {}

    def on(self, msg_type: str, handler: Handler):
        """Register a handler for incoming message types.
        handler(engine: str, payload: dict, client_ws) -> None
        """
        self.handlers.setdefault(msg_type, []).append(handler)
        return handler

    async def _dispatch(self, engine: str, payload: dict, ws):
        msg_type = payload.get("type", "unknown")
        for handler in self.handlers.get(msg_type, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(engine, payload, ws)
                else:
                    handler(engine, payload, ws)
            except Exception as e:
                logger.exception("Handler error for %s: %s", msg_type, e)

    async def _handle_client(self, websocket, path):
        engine_name = "unknown"
        self.clients.add(websocket)
        logger.info("Client connected (total %d)", len(self.clients))
        try:
            async for message in websocket:
                try:
                    payload = json.loads(message)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON from %s", engine_name)
                    continue

                # Capture engine name from register
                if payload.get("type") == "register":
                    engine_name = payload.get("engine", "unknown")
                    logger.info("Engine registered: %s", engine_name)

                # Fulfill pending futures for responses
                if payload.get("type") == "response" and "id" in payload:
                    fut = self.pending.pop(payload["id"], None)
                    if fut and not fut.done():
                        fut.set_result(payload.get("result"))

                await self._dispatch(engine_name, payload, websocket)
        except Exception as e:
            logger.info("Client %s disconnected: %s", engine_name, e)
        finally:
            self.clients.discard(websocket)
            logger.info("Client gone (total %d)", len(self.clients))

    async def broadcast(self, message: dict):
        """Send JSON to all connected engine clients."""
        if not self.clients:
            logger.warning("No clients connected")
            return
        text = json.dumps(message)
        dead = set()
        for ws in self.clients:
            try:
                await ws.send(text)
            except Exception:
                dead.add(ws)
        self.clients -= dead

    async def command(self, action: str, params: dict | None = None, timeout: float = 10.0) -> Any:
        """Send a command and wait for the engine response."""
        cmd_id = str(uuid.uuid4())
        message = {
            "type": "command",
            "id": cmd_id,
            "action": action,
            "params": params or {},
        }
        future = asyncio.get_event_loop().create_future()
        self.pending[cmd_id] = future
        await self.broadcast(message)
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self.pending.pop(cmd_id, None)
            raise TimeoutError(f"Engine did not respond to '{action}' within {timeout}s")

    async def query(self, action: str, params: dict | None = None, timeout: float = 10.0) -> Any:
        """Same as command(), semantics only differ in protocol."""
        return await self.command(action, params, timeout)

    async def run(self):
        try:
            import websockets
        except ImportError:
            logger.error("websockets library not installed. Run: pip install websockets")
            raise SystemExit(1)

        srv = await websockets.serve(self._handle_client, self.host, self.port)
        logger.info("🚀 Bridge server running on ws://%s:%d", self.host, self.port)
        await srv.wait_closed()


# ── convenience singleton ──────────────────────────────────────────
_server: BridgeServer | None = None


def get_server() -> BridgeServer:
    global _server
    if _server is None:
        _server = BridgeServer()
    return _server


async def send_command(action: str, params: dict | None = None, timeout: float = 10.0) -> Any:
    return await get_server().command(action, params, timeout)


# ── example handlers ───────────────────────────────────────────────
async def _status_handler(engine: str, payload: dict, ws):
    data = payload.get("data", {})
    fps = data.get("fps", "?")
    logger.info("[%s] FPS: %s", engine, fps)


async def _event_handler(engine: str, payload: dict, ws):
    name = payload.get("name", "?")
    logger.info("[%s] Event: %s | data: %s", engine, name, payload.get("data"))


# ── main ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hermes WebSocket Bridge Server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    server = BridgeServer(host=args.host, port=args.port)
    server.on("status", _status_handler)
    server.on("event", _event_handler)

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Shutdown by Ctrl+C")
