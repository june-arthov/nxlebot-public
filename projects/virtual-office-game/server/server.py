#!/usr/bin/env python3
"""Virtual Office 2D - Multiplayer WebSocket Server v3
Features: desk roles, computer workstations, IDE, email, analytics, project board"""

import asyncio, json, time, random, math, hashlib
import websockets

HOST, PORT = "0.0.0.0", 0
TICK_RATE = 1 / 20
PROXIMITY_CHAT_RANGE = 200
PROXIMITY_VOICE_RANGE = 150
MAX_AUDIO_CHUNK = 8192

players = {}
player_colors = ["#ff6b6b", "#4ecdc4", "#ffe66d", "#a29bfe", "#ff922b", "#20c997",
                 "#f06595", "#845ef7", "#339af0", "#51cf66", "#ff8787", "#74c0fc"]
color_idx = 0
chat_history = []
office_money = 0

# ─── DESK CONFIGURATION ───
# Each desk has a role, apps, and tasks
desks = {
    "Desk A": {
        "role": "Developer",
        "role_icon": "💻",
        "apps": ["IDE", "Terminal", "PR Review"],
        "tasks": ["fix_bug", "write_feature", "review_pr"],
        "color": "#3b82f6",
    },
    "Desk B": {
        "role": "Designer",
        "role_icon": "🎨",
        "apps": ["Figma", "Assets", "Prototype"],
        "tasks": ["design_mockup", "export_assets", "review_design"],
        "color": "#ec4899",
    },
    "Desk C": {
        "role": "Manager",
        "role_icon": "📊",
        "apps": ["Dashboard", "Reports", "Team Chat"],
        "tasks": ["check_metrics", "write_report", "team_standup"],
        "color": "#f59e0b",
    },
    "Desk D": {
        "role": "Support",
        "role_icon": "🎧",
        "apps": ["Tickets", "Knowledge Base", "Live Chat"],
        "tasks": ["resolve_ticket", "update_docs", "customer_call"],
        "color": "#22c55e",
    },
    "Meeting Table": {
        "role": "Meeting Room",
        "role_icon": "🏛️",
        "apps": ["Presentation", "Whiteboard", "Vote"],
        "tasks": ["daily_standup", "brainstorm", "retro"],
        "color": "#8b5cf6",
    },
}

# ─── WORK CONTENT ───
# IDE — code snippets for developer desk
code_challenges = [
    {
        "title": "Fix Null Pointer Bug",
        "lang": "python",
        "code": 'def get_user(id):\n    user = db.query(f"SELECT * FROM users WHERE id={id}")\n    return user.name.upper()\n\n# BUG: returns NoneType error when user not found\n# TASK: add null check',
        "expected": "None",
        "hint": "Check if user exists first",
        "reward": 25,
    },
    {
        "title": "Optimize Loop Performance",
        "lang": "javascript",
        "code": 'function processOrders(orders) {\n    let results = [];\n    for (let i = 0; i < orders.length; i++) {\n        for (let j = 0; j < orders.length; j++) {\n            if (orders[i].id === orders[j].ref) {\n                results.push(orders[i]);\n            }\n        }\n    }\n    return results;\n}\n\n// TASK: Refactor to O(n) using a Map',
        "hint": "Use a hash map for O(1) lookups",
        "reward": 30,
    },
    {
        "title": "Implement Rate Limiter",
        "lang": "go",
        "code": 'type RateLimiter struct {\n    // TODO: add fields\n}\n\nfunc (r *RateLimiter) Allow(clientID string) bool {\n    // TASK: Implement 10 req/sec per client\n    return false\n}',
        "hint": "Track timestamps per client in a map",
        "reward": 35,
    },
    {
        "title": "Fix Race Condition",
        "lang": "rust",
        "code": 'use std::sync::Mutex;\n\nstatic COUNTER: Mutex<i32> = Mutex::new(0);\n\nfn increment() {\n    let mut val = COUNTER.lock().unwrap();\n    *val += 1;\n    // BUG: deadlock in certain conditions\n}',
        "hint": "Check poison errors on lock",
        "reward": 40,
    },
]

# Email inbox content
emails = [
    {"from": "CEO", "subject": "Q4 Results Review", "body": "Team, great quarter! Revenue up 34%. Let's discuss in the all-hands tomorrow at 10 AM. — Jane", "urgent": True},
    {"from": "HR", "subject": "Benefits Enrollment Open", "body": "Annual benefits enrollment is now open. Please submit your elections by Friday. — HR Team", "urgent": False},
    {"from": "Client", "subject": "URGENT: Production Down", "body": "We're seeing 500s across all endpoints since the last deploy. ETA on fix? — Mike @ Acme Corp", "urgent": True},
    {"from": "DevOps", "subject": "Docker Migration Plan", "body": "Phase 2 migration starts next week. Please ensure all services have Dockerfiles ready. — SRE Team", "urgent": False},
    {"from": "Marketing", "subject": "Blog Post Draft", "body": "Hey, can someone from engineering review this technical blog post before we publish? — Sarah", "urgent": False},
    {"from": "Legal", "subject": "License Compliance Audit", "body": "Annual OSS license audit is due. Please update dependency list by EOW. — Legal Dept", "urgent": True},
]

# Analytics / Dashboard data
analytics_data = {
    "active_users": 1247,
    "revenue": 89420,
    "uptime": 99.97,
    "p95_latency": 142,
    "error_rate": 0.23,
    "deployments_week": 18,
}

# Support tickets
tickets = [
    {"id": "TKT-4201", "user": "alice@corp.com", "issue": "Can't login after password reset", "priority": "high"},
    {"id": "TKT-4202", "user": "bob@corp.com", "issue": "Export CSV returns empty file", "priority": "medium"},
    {"id": "TKT-4203", "user": "carol@corp.com", "issue": "Billing shows wrong amount", "priority": "high"},
    {"id": "TKT-4204", "user": "dave@corp.com", "issue": "Feature request: dark mode", "priority": "low"},
]

# Project board tasks
board_columns = {
    "Todo": ["Setup CI/CD", "Write unit tests", "Design system docs"],
    "In Progress": ["API v2 migration", "Auth refactor"],
    "Review": ["Landing page redesign", "Payment integration"],
    "Done": ["Bugfix: login timeout", "DB indexing optimization"],
}

# NPCs
npcs = [
    {"id": "npc1", "name": "Alice", "role": "Developer", "x": 330, "y": 170, "color": "#ff6b6b", "avatar": 1,
     "dialogues": ["Hey! Ada PR yang perlu di-review nih.", "Sprint ini lumayan hectic ya.", "Kopi dulu yuk!"]},
    {"id": "npc2", "name": "Bob", "role": "Designer", "x": 630, "y": 170, "color": "#4ecdc4", "avatar": 2,
     "dialogues": ["Mockup udah siap di Figma.", "Color palette baru udah gw push.", "Meeting jam 3 jangan lupa!"]},
    {"id": "npc3", "name": "Carol", "role": "Manager", "x": 850, "y": 430, "color": "#ffe66d", "avatar": 3,
     "dialogues": ["Deadline project H-3, gimana progress?", "Good job on the last release!", "Jangan lupa isi timesheet ya."]},
    {"id": "npc4", "name": "Dave", "role": "Support", "x": 330, "y": 440, "color": "#a29bfe", "avatar": 4,
     "dialogues": ["Mas, ini bugnya kenapa ya?", "Udah belajar Docker, keren banget!", "Bisa ajarin git rebase ga?"]},
]

# Task tracking
completed_tasks = set()

# Work session tracking per player
work_sessions = {}  # sid -> {desk, active_app, code_attempts, emails_read, tickets_resolved, ...}

def dist(a, b):
    return math.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2)

async def nearest_players(sid, max_range):
    me = players.get(sid)
    if not me: return []
    nearby = []
    for osid, op in players.items():
        if osid == sid: continue
        if dist(me, op) <= max_range:
            nearby.append(osid)
    return nearby

async def send_to(ws, msg):
    try: await ws.send(json.dumps(msg))
    except Exception: pass

async def broadcast(msg, exclude=None):
    dead = []
    for sid, p in players.items():
        if sid == exclude: continue
        try: await p["ws"].send(json.dumps(msg))
        except Exception: dead.append(sid)
    for sid in dead: await remove_player(sid)

async def broadcast_proximity(msg, sender_sid, max_range):
    nearby = await nearest_players(sender_sid, max_range)
    for sid in nearby:
        try: await players[sid]["ws"].send(json.dumps(msg))
        except Exception: pass

async def send_state(ws, sid):
    state = {
        "type": "init",
        "you": {k: v for k, v in players.get(sid, {}).items() if k not in ("ws", "last_seen")},
        "you_sid": sid,
        "players": {s: {k: v for k, v in p.items() if k != "ws"} for s, p in players.items() if s != sid},
        "npcs": npcs,
        "desks": desks,
        "chat_history": chat_history[-30:],
        "completed_tasks": list(completed_tasks),
        "office_money": office_money,
    }
    await ws.send(json.dumps(state))

async def remove_player(sid):
    if sid in players:
        p = players[sid]
        name = p.get("name", "?")
        del players[sid]
        if sid in work_sessions: del work_sessions[sid]
        await broadcast({"type": "player_left", "sid": sid, "name": name})

async def handler(ws):
    global color_idx
    color = player_colors[color_idx % len(player_colors)]
    color_idx += 1
    sid = str(id(ws))

    players[sid] = {
        "ws": ws, "name": f"Player{len(players)+1}", "x": 250, "y": 250,
        "dir": 0, "color": color, "last_seen": time.time(),
        "energy": 100, "morale": 75, "money": 0,
        "avatar": 0, "sitting": False, "current_desk": None,
    }
    work_sessions[sid] = {
        "active_app": None,
        "code_attempts": 0,
        "emails_read": [],
        "tickets_resolved": [],
        "board_moved": [],
    }

    await send_state(ws, sid)
    await broadcast({
        "type": "player_joined",
        "sid": sid,
        "player": {k: v for k, v in players[sid].items() if k != "ws"}
    }, exclude=sid)
    print(f"[+] {players[sid]['name']} joined ({len(players)} online)")

    try:
        async for raw in ws:
            try:
                msg = json.loads(raw)
                p = players.get(sid)
                if not p: continue
                p["last_seen"] = time.time()
                wsess = work_sessions.get(sid, {})

                if msg["type"] == "pos":
                    p["x"], p["y"] = msg["x"], msg["y"]
                    p["dir"] = msg.get("dir", 0)
                    # Don't broadcast every move — position_broadcaster handles batching

                elif msg["type"] == "name":
                    p["name"] = msg["name"][:20]

                elif msg["type"] == "set_avatar":
                    p["avatar"] = msg["avatar"]
                    await broadcast({"type": "player_avatar", "sid": sid, "avatar": p["avatar"]})

                elif msg["type"] == "chat":
                    entry = {"name": p["name"], "color": p["color"], "text": msg["text"][:200]}
                    chat_history.append(entry)
                    if len(chat_history) > 50: chat_history.pop(0)
                    await broadcast_proximity({"type": "chat", "entry": entry, "proximity": True}, sid, PROXIMITY_CHAT_RANGE)
                    await send_to(ws, {"type": "chat", "entry": entry, "proximity": False})

                elif msg["type"] == "voice_chunk":
                    chunk = msg.get("data", "")[:MAX_AUDIO_CHUNK]
                    await broadcast_proximity(
                        {"type": "voice_chunk", "sid": sid, "name": p["name"], "data": chunk},
                        sid, PROXIMITY_VOICE_RANGE)

                elif msg["type"] == "emote":
                    emote = msg["emote"]
                    await broadcast({"type": "player_emote", "sid": sid, "emote": emote})

                elif msg["type"] == "sit":
                    sitting = msg.get("sitting", True)
                    desk_label = msg.get("desk")
                    p["sitting"] = sitting
                    p["current_desk"] = desk_label if sitting else None
                    await broadcast({"type": "player_sit", "sid": sid, "sitting": sitting, "desk": desk_label})

                    # Send desk context when sitting
                    if sitting and desk_label and desk_label in desks:
                        desk = desks[desk_label]
                        await send_to(ws, {
                            "type": "desk_context",
                            "desk": desk_label,
                            "role": desk["role"],
                            "role_icon": desk["role_icon"],
                            "apps": desk["apps"],
                            "color": desk["color"],
                        })
                    elif not sitting:
                        wsess["active_app"] = None
                        await send_to(ws, {"type": "desk_close"})

                # ─── COMPUTER / WORK ACTIONS ───
                elif msg["type"] == "open_app":
                    app = msg["app"]
                    wsess["active_app"] = app

                    if app == "IDE":
                        challenge = code_challenges[hash(sid + str(len(wsess.get("code_attempts", 0)))) % len(code_challenges)]
                        await send_to(ws, {"type": "app_content", "app": "IDE", "content": challenge})

                    elif app == "Email" or app == "Tickets":
                        items = emails if app == "Email" else tickets
                        await send_to(ws, {
                            "type": "app_content", "app": app,
                            "content": {"messages": items, "type": "inbox"}
                        })

                    elif app == "Dashboard" or app == "Reports":
                        await send_to(ws, {
                            "type": "app_content", "app": app,
                            "content": {"metrics": analytics_data, "type": "dashboard"}
                        })

                    elif app == "Knowledge Base":
                        docs = [
                            {"title": "Getting Started Guide", "category": "onboarding"},
                            {"title": "API Reference v2.4", "category": "technical"},
                            {"title": "Troubleshooting Common Issues", "category": "support"},
                            {"title": "Deployment Checklist", "category": "devops"},
                            {"title": "Security Best Practices", "category": "security"},
                        ]
                        await send_to(ws, {"type": "app_content", "app": app, "content": {"docs": docs, "type": "docs"}})

                    elif app == "Live Chat":
                        await send_to(ws, {
                            "type": "app_content", "app": app,
                            "content": {"type": "chat_app", "messages": [
                                {"from": "user", "text": "Hi, my dashboard is showing blank"},
                                {"from": "agent", "text": "Let me check that for you. Can you try clearing cache?"},
                            ]}
                        })

                    elif app == "PR Review":
                        await send_to(ws, {
                            "type": "app_content", "app": app,
                            "content": {"type": "pr_list", "prs": [
                                {"id": 142, "title": "Refactor auth middleware", "author": "alice", "files": 12, "status": "open"},
                                {"id": 143, "title": "Add rate limiting to API", "author": "bob", "files": 4, "status": "open"},
                                {"id": 144, "title": "Fix memory leak in worker pool", "author": "carol", "files": 2, "status": "open"},
                            ]}
                        })

                    elif app == "Figma":
                        await send_to(ws, {
                            "type": "app_content", "app": app,
                            "content": {"type": "designs", "designs": [
                                {"name": "Landing Page v3", "status": "in_progress"},
                                {"name": "Mobile Nav Redesign", "status": "review"},
                                {"name": "Icon Set — Dark Mode", "status": "done"},
                            ]}
                        })

                    elif app == "Assets":
                        await send_to(ws, {
                            "type": "app_content", "app": app,
                            "content": {"type": "files", "files": [
                                "logo.svg", "hero-bg.png", "icons-sprite.svg",
                                "banner-2026.psd", "brand-guide.pdf", "avatars-pack.zip",
                            ]}
                        })

                    elif app == "Prototype":
                        await send_to(ws, {
                            "type": "app_content", "app": app,
                            "content": {"type": "proto", "prototypes": [
                                {"name": "Checkout Flow v2", "frames": 8, "shared": True},
                                {"name": "Onboarding Wizard", "frames": 12, "shared": False},
                            ]}
                        })

                    elif app == "Presentation":
                        await send_to(ws, {
                            "type": "app_content", "app": app,
                            "content": {"type": "slides", "slides": [
                                {"title": "Q4 Roadmap", "presenter": "Manager"},
                                {"title": "Sprint Retrospective", "presenter": "Scrum Master"},
                                {"title": "Architecture Overview", "presenter": "Tech Lead"},
                            ]}
                        })

                    elif app == "Whiteboard":
                        await send_to(ws, {"type": "app_content", "app": app, "content": {"type": "canvas", "elements": []}})

                    elif app == "Vote":
                        await send_to(ws, {
                            "type": "app_content", "app": app,
                            "content": {"type": "polls", "polls": [
                                {"question": "Sprint length?", "options": ["1 week", "2 weeks", "3 weeks"], "results": [2, 5, 1]},
                            ]}
                        })

                    elif app == "Terminal":
                        await send_to(ws, {
                            "type": "app_content", "app": app,
                            "content": {"type": "terminal", "history": [
                                "$ docker ps", "CONTAINER ID   IMAGE          STATUS",
                                "a1b2c3d4e5f6   api-gateway    Up 3 days",
                                "$ npm run build", "Build complete. 450 modules, 0 errors.",
                                "$ █",
                            ]}
                        })

                    elif app == "Team Chat":
                        await send_to(ws, {
                            "type": "app_content", "app": app,
                            "content": {"type": "slack", "channels": [
                                "#general", "#engineering", "#design", "#random", "#announcements"
                            ], "messages": {
                                "#general": [
                                    {"user": "Alice", "text": "Prod deploy going out in 5"},
                                    {"user": "Bob", "text": "PR #142 ready for review 👀"},
                                ]
                            }}
                        })

                # ─── SUBMIT WORK ───
                elif msg["type"] == "submit_work":
                    app = msg["app"]
                    desk = p.get("current_desk", "")
                    desk_cfg = desks.get(desk, {})

                    if app == "IDE":
                        # Player "solved" the coding challenge
                        wsess["code_attempts"] = wsess.get("code_attempts", 0) + 1
                        challenge = code_challenges[hash(sid + str(wsess["code_attempts"])) % len(code_challenges)]
                        reward = challenge["reward"]
                        p["money"] = p.get("money", 0) + reward
                        global office_money
                        office_money += reward

                        await send_to(ws, {"type": "work_result", "app": "IDE", "success": True,
                                           "message": f"✅ Bug fixed! +${reward}", "reward": reward})
                        await broadcast({
                            "type": "task_done", "task": "fix_bug",
                            "by": p["name"], "reward": reward,
                            "office_money": office_money,
                            "desc": f"{p['name']} fixed a bug in {desk}"
                        })
                        completed_tasks.add(f"fix_bug_{sid}_{wsess['code_attempts']}")

                    elif app == "Email":
                        # Reading email = small reward
                        wsess["emails_read"] = wsess.get("emails_read", [])
                        if len(wsess["emails_read"]) < len(emails):
                            wsess["emails_read"].append(time.time())
                            reward = 5
                            p["money"] = p.get("money", 0) + reward
                            office_money += reward
                            await send_to(ws, {"type": "work_result", "app": "Email", "success": True,
                                               "message": f"📧 Email processed! +${reward}", "reward": reward})

                    elif app == "Tickets":
                        wsess["tickets_resolved"] = wsess.get("tickets_resolved", [])
                        if len(wsess["tickets_resolved"]) < len(tickets):
                            ticket = tickets[len(wsess["tickets_resolved"])]
                            wsess["tickets_resolved"].append(ticket["id"])
                            reward = 20 if ticket["priority"] == "high" else 10
                            p["money"] = p.get("money", 0) + reward
                            office_money += reward
                            await send_to(ws, {"type": "work_result", "app": "Tickets", "success": True,
                                               "message": f"🎫 Ticket {ticket['id']} resolved! +${reward}", "reward": reward})

                    elif app == "PR Review":
                        reward = 15
                        p["money"] = p.get("money", 0) + reward
                        office_money += reward
                        await send_to(ws, {"type": "work_result", "app": "PR Review", "success": True,
                                           "message": f"✅ PR reviewed & approved! +${reward}", "reward": reward})

                    else:
                        reward = 10
                        p["money"] = p.get("money", 0) + reward
                        office_money += reward
                        await send_to(ws, {"type": "work_result", "app": app, "success": True,
                                           "message": f"✅ {app} work done! +${reward}", "reward": reward})

            except json.JSONDecodeError:
                pass

    except Exception as e:
        print(f"[-] {players[sid].get('name','?')} error: {e}")
    finally:
        await remove_player(sid)
        print(f"[-] removed, now {len(players)} online")


async def position_broadcaster():
    while True:
        await asyncio.sleep(TICK_RATE)
        if len(players) <= 1: continue
        all_pos = {"type": "positions", "players": {
            sid: {"x": p["x"], "y": p["y"], "dir": p.get("dir", 0),
                  "sitting": p.get("sitting", False), "avatar": p.get("avatar", 0),
                  "current_desk": p.get("current_desk")}
            for sid, p in players.items()}}
        dead = []
        for sid, p in players.items():
            try: await p["ws"].send(json.dumps(all_pos))
            except Exception: dead.append(sid)
        for sid in dead: await remove_player(sid)


async def timeout_cleaner():
    while True:
        await asyncio.sleep(15)
        now = time.time()
        dead = [sid for sid, p in players.items() if now - p["last_seen"] > 60]
        for sid in dead:
            print(f"[!] Timeout {players[sid]['name']}")
            await remove_player(sid)


async def main():
    print(f"🏢 Virtual Office 2D Server v3 on ws://{HOST}:{PORT}")
    print(f"   Desks: {', '.join(desks.keys())}")
    server = await websockets.serve(handler, HOST, PORT)
    print("Server listening...")
    await asyncio.gather(position_broadcaster(), timeout_cleaner())


if __name__ == "__main__":
    asyncio.run(main())
