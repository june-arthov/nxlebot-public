# 🤝 Bot Coordination Skill

Shared skill for MilkV (Hermes) and Nxlebot (OpenClaw) to coordinate in the BOTS Telegram group.

## Agents

| Agent | System | Primary Model | Bot ID | Role |
|-------|--------|---------------|--------|------|
| MilkV | Hermes CLI | glm-5.1:cloud | 8636887826 (@milkvybot) | Coding, automation, creative |
| Nxlebot | OpenClaw | glm-5.1:cloud | 8055831092 (@Nxlebot) | System ops, monitoring, search |

## BOTS Group Config

- **Chat ID:** `-5179640846`
- **Nxlebot:** `requireMention: false` (ONLY for this group, so it responds to all messages)
- **MilkV:** Ignores messages from bot user `8055831092` (not in ALLOWED_USERS)
- **User (NxL, ID 8621864972):** Always highest priority

## Anti-Loop Rules

1. MilkV → Can send messages to BOTS group ✅
2. Nxlebot → Responds to ALL messages in BOTS group (requireMention:false) ✅
3. MilkV → Ignores Nxlebot's messages (8055831092 not in ALLOWED_USERS) ✅
4. **Result: 1-directional flow. No infinite loop.** ✅

## Health Check Cron (MilkV)

```
Script: ~/.hermes/scripts/bot-healthcheck.sh
Schedule: every 2h
Deliver: local (no agent, shell script only)
```

- MilkV sends random health-check message to BOTS group
- Nxlebot sees it and responds naturally
- Zero LLM tokens burned by MilkV for this (shell script + curl)
- Nxlebot only burns tokens when actually responding

## Shared Knowledge

- **Shared file:** `~/.openclaw/workspace/shared/AGENT-NETWORK.md`
  - Symlinked to `~/.hermes/shared/AGENT-NETWORK.md`
  - Both agents can read/write here
  - Date-stamp all entries

## Self-Improvement Protocol

When either bot discovers something useful:
1. Write it to `shared/AGENT-NETWORK.md` with date stamp
2. Tag the other agent in BOTS group about the update
3. Keep entries concise — reference, not diary

## Key Config Locations

| Item | MilkV (Hermes) | Nxlebot (OpenClaw) |
|------|----------------|-------------------|
| Main config | `~/.hermes/config.yaml` | `~/.openclaw/openclaw.json` |
| Skills | `~/.hermes/skills/` | `~/.openclaw/workspace/skills/` |
| Cron | `~/.hermes/cron/jobs.json` | `~/.openclaw/cron/jobs.json` |
| Memory | `~/.hermes/memory/` | `~/.openclaw/workspace/memory/` |
| Sessions | `~/.hermes/sessions/` | `~/.openclaw/agents/main/sessions/` |
| Service | Hermes gateway (systemd) | openclaw-gateway (systemd) |

## WSL Environment

- Host: DESKTOP-VHSTJM5 (WSL2)
- Both run on same machine, same user (nxelleai)
- Network: mirrored mode (may need `wsl --shutdown` to activate)
- DNS: 1.1.1.1 / 8.8.8.8, BBR congestion control