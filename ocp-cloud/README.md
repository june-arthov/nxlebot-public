# OC+ Runtime Cloud

**Run OC+ automation scripts in the cloud. No servers. No setup. Just ship.**

OC+ Runtime Cloud is a platform for executing [OC+ (Octane)](./docs/oc-plus-language.md) pipeline scripts in secure, sandboxed Docker containers. Write automation workflows in a clean, readable DSL — deploy them with a single API call.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)

---

## Why?

| Problem | Solution |
|---------|----------|
| Bash scripts get messy fast | OC+ is a declarative pipeline language — variables, loops, conditionals, parallel blocks, error handling. Clean syntax, no YAML hell. |
| GitHub Actions overkill for simple cron | One API call. Trigger via cron, webhook, or CLI. No YAML config, no repo required. |
| Running untrusted scripts locally is dangerous | Every execution runs in an isolated Docker container. No network, limited CPU/RAM, non-root user. |

---

## Table of Contents

- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [OC+ Language](#oc-language)
- [Architecture](#architecture)
- [Security](#security)
- [Development](#development)
- [Roadmap](#roadmap)

---

## Quick Start

### Prerequisites

- **Docker** 24+ with BuildKit enabled
- **Python** 3.11+
- **Git**

### 1. Clone

```bash
git clone https://github.com/june-arthov/OC-.git
cd OC-
```

### 2. Install dependencies

```bash
cd api
pip install -r requirements.txt
```

### 3. Build the sandbox

```bash
make build-sandbox
```

This creates the `ocp-sandbox:latest` Docker image — a minimal Python container with the OC+ interpreter pre-installed and common dangerous binaries removed.

### 4. Start the API server

```bash
make run-api
```

Server starts at `http://localhost:8000`. Visit `http://localhost:8000/health` to verify.

### 5. Run your first script

```bash
make test
```

Or manually:

```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "echo \"Hello from OC+ Cloud!\"\nset NAME = \"World\"\necho \"Hi $NAME\"",
    "timeout": 30
  }'
```

**Response:**

```json
{
  "execution_id": "a1b2c3d4",
  "status": "success",
  "stdout": "Hello from OC+ Cloud!\nHi World\n",
  "stderr": "",
  "duration_ms": 1247,
  "created_at": "2026-05-07T12:00:00.000Z"
}
```

---

## API Reference

Base URL: `http://localhost:8000`

### `GET /health`

Health check endpoint.

```bash
curl http://localhost:8000/health
```

```json
{"status": "ok", "version": "0.1.0"}
```

### `POST /execute`

Execute an OC+ script in a sandboxed container.

**Headers:**
| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | `application/json` |
| `X-API-Key` | No | API key for authentication (future) |

**Request Body:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `script` | string | Yes | — | OC+ script content |
| `timeout` | integer | No | `300` | Max execution time in seconds |
| `env_vars` | object | No | `{}` | Environment variables injected into the container |

**Response:** `200 OK`

| Field | Type | Description |
|-------|------|-------------|
| `execution_id` | string | Unique 8-char execution ID |
| `status` | string | `success`, `failed`, or `error` |
| `stdout` | string | Standard output from the script |
| `stderr` | string | Standard error from the script |
| `duration_ms` | integer | Execution wall-clock time in milliseconds |
| `created_at` | string | ISO 8601 timestamp |

**Status Codes:**

| Code | Meaning |
|------|---------|
| `200` | Script executed (check `status` field for success/failure) |
| `400` | Invalid request body |
| `401` | Missing or invalid API key (future) |
| `500` | Internal server error (sandbox failure, Docker unavailable) |

**Resource Limits (per execution):**
- Memory: 512 MB
- CPU: 0.5 cores
- Network: disabled (no outbound access)
- User: `sandbox` (non-root)

---

## OC+ Language

OC+ is a declarative pipeline DSL. Write automation workflows in clean syntax instead of messy shell scripts.

> **Full language reference:** [docs/oc-plus-language.md](./docs/oc-plus-language.md)

### Quick syntax tour

```oc+
# Variables — string or integer
set PROJECT = "myapp"
set VERSION = 3
set NEXT = $VERSION + 1

# Shell commands
run "docker build -t $PROJECT:$VERSION ."

# Print output
echo "Deploying $PROJECT v$VERSION..."

# Change directory
cd "/app"

# Conditionals
if $ENV == "prod" {
    run "deploy-prod.sh"
} else {
    echo "Skipping production deploy"
}

# Parallel execution
parallel {
    run "npm install"
} {
    run "pip install -r requirements.txt"
}

# Error handling
try {
    run "risky-command.sh"
} catch {
    echo "Recovered from error"
}

# Loops
for i in [1..5] {
    echo "Iteration $i"
}

for env in ["dev", "staging", "prod"] {
    echo "Checking $env..."
}

# While loops
set RETRIES = 0
while $RETRIES < 3 {
    try {
        run "curl -f https://api.example.com/health"
        set RETRIES = 99
    } catch {
        set RETRIES = $RETRIES + 1
        echo "Retry $RETRIES/3"
    }
}
```

### Real-world examples

See [`examples/`](./examples) for complete scripts:

| Script | Description |
|--------|-------------|
| `backup-db.ocp` | Dump PostgreSQL, upload to S3, notify Telegram |
| `deploy-staging.ocp` | Build Docker image, push to registry, SSH deploy |
| `health-check.ocp` | Check 5 endpoints, send alert on failure |
| `data-sync.ocp` | Sync data between two APIs with transformation |
| `report-daily.ocp` | Aggregate logs, generate report, email to team |

---

## Architecture

```
┌─────────────────────────────────────────┐
│            Client (CLI / SDK)            │
│  curl | ocp-cli | VSCode extension       │
└──────────────────┬──────────────────────┘
                   │ REST API (JSON)
┌──────────────────▼──────────────────────┐
│          API Server (FastAPI)            │
│  • POST /execute                         │
│  • Auth middleware (future)              │
│  • Rate limiting (future)                │
│  • Execution history (future)            │
└──────────────────┬──────────────────────┘
                   │ Docker SDK
┌──────────────────▼──────────────────────┐
│         Docker Engine                    │
│  ┌────────────────────────────────────┐ │
│  │   ocp-sandbox container             │ │
│  │   • Minimal Python 3.11             │ │
│  │   • Non-root sandbox user           │ │
│  │   • Network disabled                │ │
│  │   • 512 MB RAM, 0.5 CPU             │ │
│  │   • Script mounted read-only        │ │
│  │   • Auto-removed on exit            │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Execution flow

1. Client sends `POST /execute` with OC+ script
2. API writes script to temp file
3. API spawns `ocp-sandbox` container with script mounted read-only
4. Container runs `python3 /app/ocp_interpreter.py /script/script.ocp`
5. API captures stdout, stderr, and exit code
6. Container auto-removed
7. Temp file deleted
8. Response returned to client

---

## Security

Every execution is isolated at the container level.

| Layer | Protection |
|-------|------------|
| **User** | Non-root `sandbox` user — no `sudo`, no root access |
| **Network** | `network_disabled: true` — no outbound connections |
| **Memory** | Hard limit at 512 MB — OOM killer stops abuse |
| **CPU** | `cpu_quota: 50000` — capped at 0.5 cores |
| **Filesystem** | Script mounted read-only (`:ro`) — script cannot modify itself |
| **Binaries** | `curl`, `wget`, `ssh`, `nc` removed from image |
| **Auto-cleanup** | Container destroyed immediately after execution (`remove=True`) |
| **Timeout** | Default 5-minute cap — infinite loops killed |

### Production hardening (planned)

- [ ] seccomp profiles (block `ptrace`, `mount`, `reboot`)
- [ ] AppArmor / SELinux profiles
- [ ] `read-only` root filesystem
- [ ] `no-new-privileges` flag
- [ ] gVisor / Firecracker microVM sandbox (optional)

---

## Development

### Project structure

```
.
├── api/
│   ├── main.py              # FastAPI server
│   └── requirements.txt     # Python dependencies
├── sandbox/
│   ├── Dockerfile            # Sandbox image
│   └── ocp_interpreter.py   # OC+ interpreter (lexer/parser/executor)
├── examples/                 # Example OC+ scripts (coming soon)
├── docs/                     # Documentation (coming soon)
│   └── oc-plus-language.md  # Full OC+ language reference
├── templates/                # Pre-built automation templates (coming soon)
├── tests/                    # Test suite (coming soon)
├── Makefile                  # Build/run/test commands
└── .gitignore
```

### Makefile commands

```bash
make build-sandbox   # Build Docker sandbox image
make run-api          # Start API server (dev mode with hot reload)
make test             # Run example script against API
make clean            # Remove Docker image and __pycache__
```

### Running tests

```bash
# Coming in v0.2 — currently manual testing:

# 1. Start API
make run-api

# 2. In another terminal
make test
```

---

## Roadmap

| Phase | Features | Target |
|-------|----------|--------|
| **v0.1** ✅ | MVP — Docker sandbox, `/execute` endpoint, OC+ interpreter v2.0 | May 2026 |
| **v0.2** | Cron scheduler, execution history, basic auth (API keys) | Jun 2026 |
| **v0.3** | Telegram/Email/Webhook delivery, rate limiting, per-user quotas | Jul 2026 |
| **v0.4** | Web dashboard (upload, schedule, view logs), VSCode extension | Aug 2026 |
| **v0.5** | Template library, shared workspaces, team plans | Sep 2026 |
| **v1.0** | Payment integration (Midtrans/Stripe), production hardening, SLA | Oct 2026 |

---

## Contributing

Pull requests welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md) (coming soon).

### Commit conventions

```
type: concise subject

Optional body.
```

Types: `feat`, `fix`, `refactor`, `docs`, `chore`

---

## License

MIT © 2026 June Arthov

---

## Links

- [Full OC+ Language Reference](./docs/oc-plus-language.md)
- [GitHub Repository](https://github.com/june-arthov/OC-)
