# Codex Replacement

How Instinct8 Agent replaces and improves upon Codex CLI.

## Overview

Instinct8 Agent is a **drop-in replacement** for Codex CLI, providing better goal preservation through Selective Salience Compression. It generates real code, creates files, and executes commands — just like Codex — but with integrated compression that preserves goal-critical information.

## Quick Setup

### Alias Codex to Instinct8

```bash
# Add to your ~/.bashrc or ~/.zshrc
alias codex=instinct8

# Now 'codex' commands use Instinct8
codex exec "create a FastAPI endpoint"
```

### Use Instinct8 Directly

```bash
instinct8 "create a FastAPI endpoint"
instinct8 exec "explain this code"
```

## What Instinct8 Does

### Real Code Generation
- Calls OpenAI API to generate actual code
- Parses code blocks from LLM responses
- Creates files automatically from generated code

### File Operations
- **Write**: Automatically creates files from code blocks
- **Read**: Can read existing files for context
- **Smart Naming**: Infers filenames from prompts

### Command Execution
- Can execute shell commands
- Safety flag: `--allow-execution` (disabled by default)
- Command history tracking

### Selective Salience Compression
- Fully integrated with the real agent
- Preserves goal-critical information verbatim
- Compresses background context automatically
- Triggers when context exceeds threshold

## Codex-Compatible Interface

```bash
# Codex syntax
codex exec "create a login endpoint"

# Instinct8 syntax (identical)
instinct8 exec "create a login endpoint"

# Shorter form
instinct8 "create a login endpoint"
```

### With Goal and Constraints

```bash
instinct8 exec \
  --goal "Build authentication system" \
  --constraints "Use JWT" "Hash passwords" \
  "create a login endpoint"
```

### JSON Output

```bash
instinct8 exec --json "explain this codebase"
```

## Invocation Comparison

### Codex (Node.js SDK)
- Uses `@openai/codex-sdk` (JavaScript SDK)
- Invoked via `npm run codex:prompt "prompt"` (wrapper script)
- Requires Node.js and npm
- Project-specific configuration

### Instinct8 (Python CLI)
- Standalone Python package installed via pip/pipx
- Invoked via `instinct8 "prompt"` (direct command)
- Works anywhere Python works
- Globally available

## Key Differences from Codex

### What's Better
- **Selective Salience Compression**: Better goal preservation
- **Explicit Constraints**: Constraints are protected during compression
- **More Efficient**: Better compression enables longer conversations

### What's Compatible
- Same CLI interface (`exec` command)
- Same prompt format
- JSON output support (`--json` flag)
- Goal/constraints support

### What's Different
- No Interactive TUI (focuses on `exec` mode)
- No Git-repo requirement (unlike Codex)
- No built-in sandbox (uses basic command execution)
- Simpler tool calling (basic file ops vs full tool system)

## Functionality Gap (Original vs Current)

The original Codex CLI provides:
1. Code generation via LLM
2. Shell command execution
3. File creation/modification
4. Iterative task execution
5. Full tool calling system (shell, file ops, patches, MCP)

Instinct8 now provides items 1-4 with Selective Salience Compression integrated. Item 5 (full tool system) is simplified but covers core use cases.

## Python API

```python
from selective_salience import Instinct8Agent

agent = Instinct8Agent()
agent.initialize(
    goal="Build a FastAPI authentication system",
    constraints=["Use JWT", "Hash passwords"]
)

# Execute a coding task
response = agent.execute("create a login endpoint")
# Generates actual Python code!
```

## Configuration

Create `~/.instinct8/config.json`:

```json
{
  "goal": "Build a FastAPI authentication system",
  "constraints": [
    "Use JWT tokens",
    "Hash passwords with bcrypt",
    "Must be production-ready"
  ],
  "model": "gpt-4o"
}
```

## Safety

- **Execution disabled by default**: Commands won't run unless `--allow-execution` is set
- **File operations**: Creates files by default (safe operation)
- **Command timeout**: 30 seconds max
- **Error handling**: Graceful failures

## Migration Guide

1. **Install**: `pip install instinct8-agent`
2. **Set API key**: `export OPENAI_API_KEY="your-key"`
3. **Alias** (optional): `alias codex=instinct8`
4. **Test**: `instinct8 exec "Hello, what can you do?"`
5. **Configure** (optional): Create `~/.instinct8/config.json`
