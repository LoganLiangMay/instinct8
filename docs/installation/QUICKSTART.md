# Instinct8 Agent - Quick Start Guide

Get started with Instinct8 Agent in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/jjjorgenson/instinct8.git
cd instinct8

# Install the package
pip install -e .

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

## Quick Test

### Option 0: Replace Codex (Drop-in Replacement)

```bash
# Use Instinct8 as a Codex replacement
instinct8 "create a FastAPI endpoint"

# Or alias it
alias codex=instinct8
codex exec "create a login endpoint"
```

### Option 1: Interactive Mode (Recommended)

```bash
instinct8-agent interactive \
  --goal "Build a FastAPI authentication system" \
  --constraints "Use JWT" "Hash passwords"
```

Then try these commands:
- `ask What is the current task?`
- `say Create a login endpoint`
- `ask What are we building?`
- `salience` - See preserved information
- `stats` - See agent statistics
- `quit` - Exit

### Option 2: Test Mode

```bash
instinct8-agent test \
  --goal "Research async Python frameworks" \
  --constraints "Budget $10K" "Timeline 2 weeks" \
  --questions "What is the goal?" "What constraints exist?"
```

### Option 3: Python API

```python
from selective_salience import Instinct8Agent

# Create agent
agent = Instinct8Agent()
agent.initialize(
    goal="Build a FastAPI auth system",
    constraints=["Use JWT", "Hash passwords"]
)

# Use it
agent.ingest_turn({"role": "user", "content": "Create login endpoint"})
response = agent.answer_question("What are we building?")
print(response)
```

## What Makes Instinct8 Different?

**Traditional compression** loses goal-critical information when summarizing.

**Instinct8 Agent** preserves goal-critical information **verbatim** by:
1. Using GPT-4o to identify what's important
2. Keeping important info verbatim (not summarized)
3. Only compressing background context

**Result**: Your agent remembers its goal and constraints even after many compressions!

## Next Steps

- Read the full [README](selective_salience/README.md)
- Try the [example script](examples/instinct8_agent_example.py)
- Check out [installation guide](INSTALL.md)

## Troubleshooting

**"OPENAI_API_KEY not set"**
```bash
export OPENAI_API_KEY="your-key"
```

**"Command not found"**
```bash
pip install -e .
```

**Import errors**
```bash
# Make sure you're in the project root
cd instinct8
pip install -e .
```

## Need Help?

- Check the [README](selective_salience/README.md) for full documentation
- See [examples](examples/) for more usage patterns
- Open an issue on GitHub
