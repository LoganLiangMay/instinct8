# Instinct8 Agent - Installation Guide

Complete guide to install and use Instinct8 Agent as a Codex replacement.

## Prerequisites

- Python 3.9 or higher
- OpenAI API key
- Git (for cloning the repository)

## Installation Methods

### Method 1: pip (Recommended)

**Install from PyPI:**
```bash
pip install instinct8-agent
```

**Verify installation:**
```bash
instinct8 --help
instinct8-agent --help
```

### Method 2: pipx (Recommended for CLI Tools)

**Install with pipx (isolated environment):**
```bash
# Install pipx if you don't have it
brew install pipx  # macOS
# or: pip install pipx  # Linux/Windows

# Install Instinct8 Agent
pipx install instinct8-agent

# Verify
instinct8 --help
```

### Method 3: From Source (Development)

**For development or latest features:**
```bash
git clone https://github.com/jjjorgenson/instinct8.git
cd instinct8
pip install -e .
```

This installs Instinct8 Agent and makes the `instinct8` and `instinct8-agent` commands available.

### Step 3: Set Your OpenAI API Key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

**To make this permanent**, add it to your shell configuration file:

```bash
# For bash
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# For zsh
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### Step 4: Verify Installation

```bash
# Check that commands are available
instinct8 --help
instinct8-agent --help

# Test basic functionality
instinct8 "Hello, what can you do?"
```

If you see help text and a response, installation is successful! ✅

## Quick Start

### Option 1: Use as Codex Replacement

```bash
# Alias Instinct8 to replace Codex
alias codex=instinct8

# Now use Codex commands - they'll use Instinct8!
codex exec "create a FastAPI endpoint"
```

### Option 2: Use Instinct8 Directly

```bash
# Basic usage
instinct8 "create a FastAPI endpoint"

# With exec command (Codex-compatible)
instinct8 exec "explain this codebase"
```

### Option 3: Interactive Agent Mode

```bash
instinct8-agent interactive \
  --goal "Build a FastAPI authentication system" \
  --constraints "Use JWT" "Hash passwords"
```

## Configuration (Optional)

Create a config file to set default goal and constraints:

```bash
mkdir -p ~/.instinct8
```

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

Now Instinct8 will use these defaults for all commands.

## Usage Examples

### Basic Task Execution

```bash
# Simple prompt
instinct8 "create a login endpoint"

# With exec (Codex-compatible)
instinct8 exec "refactor this code to use async/await"

# JSON output
instinct8 exec --json "explain this codebase"
```

### With Goal and Constraints

```bash
instinct8 exec \
  --goal "Build authentication system" \
  --constraints "Use JWT" "Hash passwords" "Support refresh tokens" \
  "create a login endpoint"
```

### Interactive Mode

```bash
instinct8-agent interactive \
  --goal "Research async Python frameworks" \
  --constraints "Budget $10K" "Timeline 2 weeks"
```

Then use these commands:
- `ask <question>` - Ask the agent a question
- `say <message>` - Add a user message
- `compress` - Manually trigger compression
- `salience` - Show preserved salience set
- `stats` - Show agent statistics
- `quit` - Exit

### Test Mode

```bash
instinct8-agent test \
  --goal "Build FastAPI app" \
  --constraints "Use JWT" \
  --questions "What is the goal?" "What constraints exist?"
```

## Python API Usage

You can also use Instinct8 in your Python code:

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

## Troubleshooting

### "Command not found: instinct8"

**Solution:**
```bash
# Make sure you're in the project directory
cd instinct8

# Reinstall
pip install -e .

# Verify installation
which instinct8
```

### "OPENAI_API_KEY environment variable not set"

**Solution:**
```bash
export OPENAI_API_KEY="your-api-key-here"

# Verify it's set
echo $OPENAI_API_KEY
```

### "ModuleNotFoundError: No module named 'selective_salience'"

**Solution:**
```bash
# Make sure you're in the project root
cd instinct8

# Reinstall in development mode
pip install -e .

# Or install dependencies
pip install -r requirements.txt
pip install -e .
```

### Import Errors

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Reinstall package
pip install -e .
```

## Updating

If you already have Instinct8 Agent installed:

```bash
# Upgrade to latest version
pip install --upgrade instinct8-agent

# Or with pipx
pipx upgrade instinct8-agent

# Verify version
pip show instinct8-agent
```

## Uninstallation

```bash
# Remove the package
pip uninstall instinct8-agent

# Remove config (optional)
rm -rf ~/.instinct8
```

## Next Steps

- Read the [Quick Start Guide](QUICKSTART.md)
- See [Codex Replacement Guide](docs/CODEX_REPLACEMENT.md) for migration details
- Check [Examples](examples/) for more usage patterns
- Read the [Full Documentation](selective_salience/README.md)

## Getting Help

- Check the [README](README.md) for project overview
- See [Troubleshooting](#troubleshooting) section above
- Open an issue on GitHub: https://github.com/jjjorgenson/instinct8/issues

## What Makes Instinct8 Different?

**Codex's compression** uses simple summarization - it may lose goal-critical information.

**Instinct8's compression** preserves goal-critical information **verbatim** by:
1. Using GPT-4o to identify what's important
2. Keeping important info verbatim (not summarized)
3. Only compressing background context

**Result**: Better goal coherence and constraint retention in long conversations!

---

**Ready to get started?** Run `instinct8 "Hello!"` to test your installation! 🚀
