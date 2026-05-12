# OC+ (Octane) DSL

**Pipeline Automation Language for developers who hate YAML.**

```ocp
echo "Deploying..."
set ENV = "production"
run "docker build -t app:${ENV} ."
if $ENV == "production" {
    run "kubectl apply -f deploy.yaml"
}
```

## Install

```bash
pip install ocplus
```

## Quick Start

**CLI mode:**
```bash
ocp deploy.ocp
# or
python -m ocplus deploy.ocp
```

**Library mode:**
```python
from ocplus import execute_script

result = execute_script('''
    set NAME = "world"
    echo "Hello ${NAME}"
''')
print(result["status"])  # "success"
```

## Syntax

### Commands

| Command | Syntax | Description |
|---------|--------|-------------|
| `echo` | `echo "msg"` | Print to stdout. Supports `${VAR}` |
| `run` | `run "cmd"` | Execute shell command safely (no injection) |
| `set` | `set VAR = "val"` | Assign string variable |
| `set` | `set VAR = EXPR` | Assign math expression result |
| `cd` | `cd "path"` | Change directory |
| `if` | `if $VAR == "val" { ... }` | Conditional with optional `else` |
| `for` | `for i in [1..10] { ... }` | Range-based loop |
| `while` | `while $VAR < 5 { ... }` | Conditional loop |
| `try` | `try { ... } catch { ... }` | Error handling |
| `parallel` | `parallel { ... } { ... }` | Run blocks concurrently |

### Variables

```ocp
set NAME = "production"
set PORT = 8080
set FULL = "${NAME}:${PORT}"  # "production:8080"
```

### Math Expressions

```ocp
set COUNT = 10
set DOUBLE = COUNT * 2
set HALF = (COUNT + 10) / 2
```

### Conditionals

```ocp
if $STATUS == "ok" {
    echo "All good"
} else {
    echo "Something wrong"
}
```

**Operators:** `==`, `!=`, `<`, `>`, `<=`, `>=`

### Loops

```ocp
# Range loop
for i in [1..5] {
    echo "Attempt ${i}"
    run "curl https://api.example.com"
}

# While loop
set RETRY = 0
while $RETRY < 3 {
    try {
        run "curl https://api.example.com/health"
        set RETRY = 99
    } catch {
        set RETRY = RETRY + 1
        run "sleep 2"
    }
}
```

### Parallel Execution

```ocp
parallel {
    run "npm build -- --project=frontend"
} {
    run "cargo build --release --manifest-path backend/Cargo.toml"
}
```

### Error Handling

```ocp
try {
    run "kubectl apply -f deploy.yaml"
} catch {
    echo "Deploy failed, rolling back..."
    run "kubectl rollout undo deployment/app"
}
```

## Security

- **No shell injection** — `run` uses `subprocess.run(shell=False)` with `shlex.split()`
- Commands like `run "echo hello && rm -rf /"` are treated as literal args, not shell
- Safe by default for CI/CD pipelines and automation

## Real-World Examples

Check `examples/` directory in the repo:
- `system-report.ocp` — Hourly health check (disk, memory, load)
- `git-sync.ocp` — Pull all repos on schedule
- `docker-cleanup.ocp` — Prune unused images/containers
- `retry-deploy.ocp` — Deploy with retry logic
- `health-check.ocp` — API endpoint monitoring
- `backup-db.ocp` — Database backup pipeline

## Requirements

- Python 3.10+
- No external dependencies (stdlib only)

## License

MIT

## Links

- GitHub: [june-arthov/ocplus](https://github.com/june-arthov/ocplus)
- Issues: [Report a bug](https://github.com/june-arthov/ocplus/issues)
