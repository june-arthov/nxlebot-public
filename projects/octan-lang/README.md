# OCTAN - OC+ Language

**IN → OUT Philosophy**

---

## Quick Start

```bash
cd /home/nxelleai/.openclaw/workspace/octan-lang

# REPL mode
python interpreter.py

# Execute file
python interpreter.py script.oct

# Execute code directly
python interpreter.py -c 'target = "example.com"'
```

---

## Syntax

### Assignment
```octan
target = "example.com"
ports = [80, 443, 8080]
```

### Pipeline (IN → OUT)
```octan
"example.com" -> scan -> ports
ports -> probe -> live
live -> sqli -> vulns
```

### Conditional
```octan
vulns -> yes -> exploit -> shell
vulns -> no -> skip
```

### Loop
```octan
hosts -> each -> scan -> result
result -> save
```

---

## Example Script

```octan
# Bug bounty automation
target = "example.com"

target 
  -> scan 
  -> [80, 443, 8080]
  -> probe 
  -> ["http://target", "https://target"]
  -> sqli "id"
  -> vulns?

vulns?
  -> yes
  -> exploit
  -> shell
  -> "whoami"
  -> "root"
  -> print "PWNED!"

vulns?
  -> no
  -> print "No vulns found"

# Generate report
vulns -> report -> "report.md"
```

---

## Built-in Functions

| Function | Input | Output | Description |
|----------|-------|--------|-------------|
| `scan` | target string | ports list | Port scan |
| `probe` | ports list | urls list | Service probe |
| `sqli` | urls list, param string | vulns list | SQL injection test |
| `exploit` | vulns list | shells list | Exploit vulnerabilities |
| `shell` | shells list, cmd string | output string | Execute command |
| `report` | data any | filename string | Generate report |
| `print` | data any | data any | Print output |
| `yes` | data any | bool | Check truthy |
| `no` | data any | bool | Check falsy |
| `each` | items list | items list | Iterate |
| `save` | data any | status string | Save data |

---

## Architecture

```
octan-lang/
├── interpreter.py    # Lexer + Parser + Runtime
├── README.md        # Documentation
└── examples/        # Example scripts (future)
```

**Components:**
1. **Lexer** - Tokenize source code
2. **Parser** - Build AST
3. **Runtime** - Execute with built-in functions

---

## Status

✅ Lexer - DONE  
✅ Parser - DONE  
✅ Runtime - DONE  
✅ REPL - DONE  
✅ CLI - DONE  

**OCTAN IS READY!** 🔥👑💀
