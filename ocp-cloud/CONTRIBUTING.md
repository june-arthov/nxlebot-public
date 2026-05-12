# Contributing to OC+ Runtime Cloud

First off, thank you for considering contributing! 🎉

## Code of Conduct

Be respectful. Be constructive. Assume good intent.

## How to Contribute

### Reporting Bugs

Open an issue with:
- **What happened** (expected vs actual)
- **Steps to reproduce**
- **Environment** (OS, Python version, Docker version)
- **Relevant logs** (stdout/stderr)

### Suggesting Features

Open an issue with:
- **Problem** — what pain point does this solve?
- **Proposal** — how would it work?
- **Alternatives** — what else did you consider?

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/amazing-feature`
3. Make your changes
4. Run tests: `make test`
5. Commit using [conventional commits](#commit-conventions)
6. Push: `git push origin feat/amazing-feature`
7. Open a PR against `main`

### Commit Conventions

```
type: concise subject

Optional body with details.
```

**Types:**
- `feat` — new feature
- `fix` — bug fix
- `refactor` — code restructuring (no behavior change)
- `docs` — documentation only
- `test` — adding or updating tests
- `chore` — maintenance, dependencies, build

**Examples:**
```
feat: add cron scheduler engine
fix: prevent sandbox container leak on timeout
docs: add deployment guide for production
```

## Development Setup

### Prerequisites

- Python 3.11+
- Docker 24+ with BuildKit
- Git

### Getting Started

```bash
git clone https://github.com/june-arthov/OC-.git
cd OC-

# Install API dependencies
cd api && pip install -r requirements.txt && cd ..

# Build the sandbox
make build-sandbox

# Start development server
make run-api

# In another terminal, test
make test
```

### Running Tests

```bash
# Coming soon — currently use:
make test
```

### Project Structure

```
.
├── api/              # FastAPI server
├── sandbox/          # Docker sandbox image + interpreter
├── examples/         # Example OC+ scripts
├── docs/             # Language reference and guides
├── scripts/          # CLI tools and helper scripts
├── tests/            # Test suite
└── contrib/          # Community contributions
```

## Style Guide

### Python

- Follow PEP 8
- Type hints on function signatures
- Docstrings for public functions
- Max 120 chars per line

### OC+ Scripts

- Variables at the top
- `echo` for progress steps
- `try/catch` for network or external calls
- One pipeline per file
- Comments explain intent, not mechanics

### Documentation

- Markdown format
- Code blocks with language tags (```oc+, ```bash, ```python)
- Keep examples copy-pasteable

## Questions?

Open a [discussion](https://github.com/june-arthov/OC-/discussions) or DM on Telegram: @milkvybot
