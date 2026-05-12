# OC+ (Octane) DSL Specification

**Purpose**: A lightweight DevOps orchestration and automation language created for the Nxlebot environment. It provides clean syntax for parallel execution, error handling, and common shell operations.

---

## Syntax Overview

```oc+
# Variable declaration
set VAR = "value"

# Function definition
func name() {
    # commands
}

# Parallel execution of tasks
parallel { task1 } { task2 } { task3 }

# Error handling
try {
    # commands that may fail
} catch {
    # fallback commands
}

# Built‑in commands
run "shell command"   # Execute a shell command
echo "message"        # Print to stdout
cd /path/to/dir        # Change working directory
test -f file.txt       # Test file existence (returns exit code)
curl -X POST http://example.com/api
```

---

## Key Concepts

| Feature | Description |
|---------|-------------|
| `set` | Assign a string value to a variable. |
| `func` | Define a reusable block of commands. |
| `parallel` | Run multiple `{}` blocks concurrently. |
| `try/catch` | Simple error handling; `catch` runs on non‑zero exit. |
| `run` | Execute an arbitrary shell command. |
| `echo` | Output text. |
| `cd` | Change the current directory for subsequent commands. |
| `test` | Perform file/condition checks (similar to Bash `test`). |
| `curl` | Perform HTTP requests. |

---

## Example Script

```oc+
# Set up environment variables
set PROJECT = "myapp"
set ENV = "production"

# Define a build function
func build() {
    run "npm install"
    run "npm run build"
}

# Define a deploy function
func deploy() {
    run "scp -r ./dist user@server:/var/www/$PROJECT"
    run "ssh user@server 'systemctl restart $PROJECT'"
}

# Execute build and deploy in parallel, with error handling
parallel {
    try { build } catch { echo "Build failed!" }
} {
    try { deploy } catch { echo "Deploy failed!" }
}
```

---

## Future Extensions (Ideas)
- Loop constructs (`for`, `while`).
- Conditional statements (`if ... then ... else`).
- Import system for reusable modules.
- Native support for Docker/Kubernetes commands.

---

*This file documents the OC+ language so it won't be forgotten again.*
