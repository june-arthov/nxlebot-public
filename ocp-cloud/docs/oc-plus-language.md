# OC+ (Octane) Language Reference v2.0

OC+ is a declarative pipeline DSL designed for automation workflows. It replaces messy shell scripts with clean, readable syntax. Variables, math expressions, conditionals, loops, parallel execution, and error handling — all in one file.

---

## Table of Contents

- [Quick Example](#quick-example)
- [Installation](#installation)
- [Syntax](#syntax)
  - [Comments](#comments)
  - [Variables](#variables)
  - [Commands](#commands)
- [Command Reference](#command-reference)
  - [`set` — Variables](#set--variables)
  - [`run` — Shell Execution](#run--shell-execution)
  - [`echo` — Output](#echo--output)
  - [`cd` — Change Directory](#cd--change-directory)
  - [`if` / `else` — Conditionals](#if--else--conditionals)
  - [`parallel` — Concurrent Execution](#parallel--concurrent-execution)
  - [`try` / `catch` — Error Handling](#try--catch--error-handling)
  - [`for` — Loops](#for--loops)
  - [`while` — While Loops](#while--while-loops)
- [Expression System](#expression-system)
- [Best Practices](#best-practices)
- [Anti-Patterns](#anti-patterns)
- [Pitfalls](#pitfalls)
- [Examples](#examples)

---

## Quick Example

```oc+
# deploy.ocp — Build and deploy a web app
set APP = "myapp"
set VERSION = 3
set ENV = "production"

echo "=== Deploying $APP v$VERSION to $ENV ==="

parallel {
    run "npm install"
    run "npm run lint"
} {
    run "pip install -r requirements.txt"
}

if $ENV == "production" {
    run "docker build -t $APP:$VERSION ."
    run "docker push registry.example.com/$APP:$VERSION"
    run "ssh deploy@server 'docker pull registry.example.com/$APP:$VERSION && docker-compose up -d'"
} else {
    echo "Skipping deploy (not production)"
}

echo "Done! ✅"
```

---

## Installation

### Via pip (coming soon)

```bash
pip install oc-plus
```

### Via Docker

```bash
docker pull ghcr.io/june-arthov/ocp-sandbox:latest
```

### Manual (standalone interpreter)

Download `ocp_interpreter.py` from the [repository](https://github.com/june-arthov/OC-):

```bash
wget https://raw.githubusercontent.com/june-arthov/OC-/main/sandbox/ocp_interpreter.py
chmod +x ocp_interpreter.py
```

---

## Syntax

### Comments

`#` to end of line. No multi-line comments.

```oc+
# This is a comment
set X = 5   # inline comment
```

### Variables

Variables are referenced with `$VAR`. Define them with `set`.

```oc+
set NAME = "Nyxelle"
set AGE = 25
echo "Hello $NAME, you are $AGE years old"
```

Variables are mutable and globally scoped within a script (except inside `parallel` blocks, which start with a copy).

---

## Command Reference

### `set` — Variables

Define or update a variable.

**String literal:**
```oc+
set GREETING = "Hello World"
set PATH = "/usr/local/bin"
```

**Integer expression:**
```oc+
set COUNTER = 0
set TOTAL = $PRICE * $QUANTITY
set NEXT = ($COUNT + 1) * 2
```

**Supported operators in expressions:** `+`, `-`, `*`, `/`, `%`, `()`. Integer math only. Correct operator precedence (Pratt parser).

**Variable expansion in strings:**
```oc+
set NAME = "Nyx"
set MSG = "Hi $NAME, welcome!"
echo $MSG   # Output: Hi Nyx, welcome!
```

---

### `run` — Shell Execution

Execute a shell command. `$VAR` references are expanded before execution.

```oc+
run "echo hello"
run "npm install"
run "git pull origin main"
run "docker build -t myapp:$VERSION ."
```

Uses `shell=True` — full shell features available (pipes, redirects, `&&`, `||`).

```oc+
run "cat data.csv | grep 'error' | wc -l > error-count.txt"
```

**⚠️ Non-zero exit codes throw an error** (caught by `try/catch` if wrapped).

---

### `echo` — Output

Print text to stdout. `$VAR` expansion enabled.

```oc+
echo "Step 1: Building..."
echo "Project: $PROJECT"
echo "Path: $HOME/.config"
```

---

### `cd` — Change Directory

Change the working directory for subsequent commands.

```oc+
cd "/home/user/project"
run "ls -la"
cd ".."
```

---

### `if` / `else` — Conditionals

Branch based on variable comparison.

**Syntax:**
```
if $VAR op "value" {
    # then block
} else {
    # else block (optional)
}
```

**Comparison operators:** `==`, `!=`, `<`, `>`, `<=`, `>=`

```oc+
set ENV = "production"

if $ENV == "production" {
    run "deploy-prod.sh"
} else {
    echo "Skipping deploy"
}

if $VERSION > 10 {
    echo "Major version detected"
}
```

Numbers are compared as integers when both sides parse as integers. Otherwise, string comparison is used.

---

### `parallel` — Concurrent Execution

Run multiple blocks simultaneously. Each block gets its own copy of the environment. Environments are merged back after all blocks complete.

```oc+
parallel {
    run "npm install"
    run "npm run build"
} {
    run "pip install -r requirements.txt"
    run "python setup.py"
} {
    run "cargo build --release"
}
```

**Rules:**
- Minimum 2 blocks
- Blocks run in separate threads (ThreadPoolExecutor)
- If one block fails, the error propagates but other blocks continue
- Environment variables set inside blocks are merged (last write wins on conflicts)

---

### `try` / `catch` — Error Handling

Wrap risky operations. If the `try` block throws any error, the `catch` block executes and the script continues.

```oc+
try {
    run "curl -f https://unreliable-api.example.com/health"
    echo "API is healthy ✅"
} catch {
    echo "API is down ❌ — alerting team"
    run "send-alert.sh 'API health check failed'"
}
```

**What triggers catch:** Any error — failed shell command, syntax error in nested blocks, division by zero.

---

### `for` — Loops

#### Range Loop

```oc+
for i in [1..5] {
    echo "Iteration $i"
}
# Output:
# Iteration 1
# Iteration 2
# Iteration 3
# Iteration 4
# Iteration 5
```

Ranges are **inclusive** on both ends. Endpoints can be integers or `$VAR` references.

```oc+
set START = 5
set END = 10
for n in [$START..$END] {
    echo "Processing batch $n"
}
```

#### List Loop (coming in v2.1)

```oc+
for env in ["dev", "staging", "prod"] {
    run "deploy.sh $env"
}
```

---

### `while` — While Loops

Repeat a block while a condition is true.

```oc+
set RETRIES = 0
while $RETRIES < 5 {
    try {
        run "curl -f https://api.example.com"
        echo "Connected!"
        set RETRIES = 99   # exit loop
    } catch {
        set RETRIES = $RETRIES + 1
        echo "Retry $RETRIES/5..."
        run "sleep 2"
    }
}
```

**Safety limit:** 100,000 maximum iterations — prevents infinite loops.

---

## Expression System

OC+ uses a Pratt precedence-climbing parser for math expressions. This means:

```oc+
set A = 2 + 3 * 4       # = 14 (not 20)
set B = (2 + 3) * 4     # = 20
set C = 10 / 3          # = 3 (integer division)
set D = 10 % 3          # = 1 (modulo)
set E = $A + $B * 2     # variables in expressions
set F = -5              # unary minus
```

**Operators (by precedence):**
| Precedence | Operators |
|------------|-----------|
| 1 (lowest) | `+`, `-` |
| 2 (highest) | `*`, `/`, `%` |

Use parentheses `()` to override precedence.

---

## Best Practices

### ✅ Do

```oc+
# Variables at the top — easy to find and change
set PROJECT = "myapp"
set VERSION = 3
set ENV = "staging"
set BACKUP_DIR = "/backups/$PROJECT"

# Use echo for progress tracking
echo "Step 1/3: Installing dependencies..."
run "npm ci"

echo "Step 2/3: Running tests..."
run "npm test"

echo "Step 3/3: Building..."
run "npm run build"

echo "Done! ✅"

# Wrap risky operations in try/catch
try {
    run "./cleanup-temp-files.sh"
} catch {
    echo "Cleanup failed, continuing anyway"
}

# Use parallel for independent tasks
parallel {
    run "npm run lint"
    run "npm run typecheck"
} {
    run "npm test"
}

# Comments explain intent, not mechanics
# Build and push the Docker image for staging
run "docker build -t $PROJECT:$VERSION ."
run "docker push registry/$PROJECT:$VERSION"
```

### ❌ Don't

```oc+
# Don't chain everything in one run — hard to debug
run "npm install && npm test && npm build && npm deploy && notify-slack.sh"

# Don't use run for simple output
run "echo hello"        # use `echo "hello"`

# Don't mix unrelated workflows in one file
# deploy + backup + report all in one .ocp — split into 3 files

# Don't comment the obvious
set VERSION = 3   # sets version to 3   ← useless comment

# Don't hardcode secrets
set API_KEY = "sk-live-abc123"   # ← BAD, use env vars instead
```

---

## Pitfalls

### ⚠️ Expression mode vs string mode in `set`

```oc+
set X = 5           # expression mode — X = "5"
set Y = "5"         # string mode — Y = "5"
set Z = $X + 1      # expression mode — Z = "6" ✅
set W = "$X + 1"    # string mode — W = "5 + 1" (literal string!) ❌
```

**Rule:** No quotes after `=` → expression. Quotes → string.

### ⚠️ Integer math only

```oc+
set X = 10 / 3      # X = "3" (not 3.333)
set Y = 10.5        # Error! No float support
```

### ⚠️ Shell errors abort the script

```oc+
run "curl https://down.example.com"   # fails → script aborts
echo "This never runs"
```

**Fix:** Wrap in `try/catch`.

### ⚠️ `parallel` blocks share parent env as snapshot

Variables set in a `parallel` block are visible to the parent after the block completes. If two blocks set the same variable, the result is undefined (depends on thread timing).

### ⚠️ `for` range endpoints must resolve to integers

```oc+
set MAX = "ten"
for i in [1..$MAX] { ... }   # Error! "ten" is not an integer
```

### ⚠️ Variable scope is global

There are no local variables. Variables defined inside loops, conditionals, or parallel blocks are visible everywhere after execution.

---

## Examples

### Database Backup

```oc+
# backup-db.ocp
set DB_NAME = "myapp_production"
set BACKUP_FILE = "backup_$DB_NAME.sql"
set S3_BUCKET = "myapp-backups"
set TIMESTAMP = 0  # will be set at runtime

run "date +%Y%m%d-%H%M%S > /tmp/timestamp"
# (timestamp handling via shell for now)

echo "Dumping database $DB_NAME..."
run "pg_dump $DB_NAME > /tmp/$BACKUP_FILE"

echo "Compressing..."
run "gzip /tmp/$BACKUP_FILE"

echo "Uploading to S3..."
run "aws s3 cp /tmp/$BACKUP_FILE.gz s3://$S3_BUCKET/daily/"

echo "Backup complete!"
```

### Multi-Environment Health Check

```oc+
# health-check.ocp
set ENDPOINTS_BASE = "https://api.example.com"
set ALERT_WEBHOOK = "https://hooks.slack.com/xxx"

echo "Running health checks..."

parallel {
    run "curl -sf $ENDPOINTS_BASE/v1/health"
    echo "v1 API: OK"
} {
    run "curl -sf $ENDPOINTS_BASE/v2/health"
    echo "v2 API: OK"
} {
    run "curl -sf $ENDPOINTS_BASE/admin/health"
    echo "Admin: OK"
}

echo "All checks passed ✅"
```

### Retry Pattern with Backoff

```oc+
# retry-deploy.ocp
set MAX_RETRIES = 3
set ATTEMPT = 0
set SUCCESS = 0

echo "Starting deploy..."

while $ATTEMPT < $MAX_RETRIES {
    set ATTEMPT = $ATTEMPT + 1
    echo "Attempt $ATTEMPT/$MAX_RETRIES..."

    try {
        run "kubectl apply -f deployment.yaml"
        run "kubectl rollout status deployment/myapp --timeout=60s"
        echo "Deploy successful!"
        set SUCCESS = 1
        set ATTEMPT = 99   # exit loop
    } catch {
        echo "Attempt $ATTEMPT failed, waiting..."
        run "sleep $((5 * $ATTEMPT))"   # exponential backoff
    }
}

if $SUCCESS == 0 {
    echo "All retries exhausted 😞"
    run "send-alert.sh 'Deploy failed after $MAX_RETRIES attempts'"
}
```

---

## Editors & Tooling

### VSCode Extension (coming soon)

Syntax highlighting, autocomplete, and `Run Script` command for `.ocp` files.

### CLI Runner

```bash
# Install
pip install oc-plus-cli

# Run a script
ocp run deploy.ocp

# Run with environment variables
ocp run deploy.ocp --env ENV=production --env VERSION=5
```

---

## Integration

OC+ Runtime Cloud enables:
- **Cron-triggered execution** (coming v0.2)
- **Telegram bot delivery** (coming v0.3)
- **Webhook triggers** (coming v0.3)
- **GitHub Action integration** (planned)

---

## See Also

- [OC+ Runtime Cloud README](../README.md)
- [API Reference](../README.md#api-reference)
- [Examples Directory](../examples/)
