# instinct8-mcp

Context compression with goal drift prevention for LLM agents — as an MCP server.

## Install

```bash
pip install instinct8-mcp
```

## Quick Start

Add to your Claude Code MCP config (`~/.claude/claude_code_config.json`):

```json
{
  "mcpServers": {
    "instinct8": {
      "command": "instinct8-mcp"
    }
  }
}
```

## How It Works

instinct8-mcp uses **MCP sampling** — the server constructs compression prompts and asks *your* client's model to run them. This means:

- **No API keys needed** in instinct8
- **No heavy dependencies** (~50KB install, no torch/transformers)
- **All data stays local** on your machine
- Works with whatever model your client already uses

## Tools

| Tool | Purpose | Sampling Calls |
|------|---------|---------------|
| `initialize_session` | Set goal + constraints for the session | 0 |
| `compress_context` | Compress conversation preserving goals | 2 |
| `measure_drift` | Quantify goal coherence after compression | 1-3 |

## Resources

| Resource | Purpose |
|----------|---------|
| `session://current` | Current session state |
| `strategies://list` | Available strategies with descriptions |

## Prompt Templates

For clients that don't support MCP sampling, two prompt templates are available:

| Prompt | Purpose |
|--------|---------|
| `selective_salience_extract` | Extract goal-critical info from context |
| `protected_core_compress` | Compress with Protected Core pattern |

## Architecture

```
Agent hits context limit
  → calls compress_context(conversation, goal, constraints)
    → instinct8 constructs salience extraction prompt
      → MCP sampling: client's LLM extracts salient quotes
    → instinct8 constructs background compression prompt
      → MCP sampling: client's LLM compresses background
    → instinct8 assembles: PROTECTED CORE + SALIENT ITEMS + COMPRESSED BACKGROUND
  → returns compressed context to agent
```

## License

BSL 1.1 — see LICENSE-BSL for details. Converts to Apache-2.0 after 3 years.

The core instinct8-agent library remains Apache-2.0.
