# Replacing Codex with Instinct8

Instinct8 Agent can be used as a **drop-in replacement** for Codex CLI, providing better goal preservation through Selective Salience Compression.

## Quick Setup

### Option 1: Alias Codex to Instinct8

```bash
# Add to your ~/.bashrc or ~/.zshrc
alias codex=instinct8

# Now 'codex' commands use Instinct8!
codex exec "create a FastAPI endpoint"
```

### Option 2: Use Instinct8 Directly

```bash
# Just use instinct8 instead of codex
instinct8 "create a FastAPI endpoint"
instinct8 exec "explain this code"
```

## Installation

```bash
# Install Instinct8
pip install -e .

# Set API key
export OPENAI_API_KEY="your-key"
```

## Codex-Compatible Interface

Instinct8 mimics Codex's `exec` command:

```bash
# Codex syntax
codex exec "create a login endpoint"

# Instinct8 syntax (identical!)
instinct8 exec "create a login endpoint"

# Or shorter
instinct8 "create a login endpoint"
```

## Configuration

Create `~/.instinct8/config.json` to set default goal and constraints:

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

## Key Differences

### What's Better

✅ **Goal Preservation**: Instinct8 preserves goal-critical information verbatim  
✅ **Constraint Retention**: Constraints are explicitly protected  
✅ **Better Compression**: Selective salience extraction vs simple summarization  

### What's Compatible

✅ Same CLI interface (`exec` command)  
✅ Same prompt format  
✅ JSON output support (`--json` flag)  

### What's Different

⚠️ **No Interactive TUI**: Instinct8 focuses on non-interactive `exec` mode  
⚠️ **No Git Integration**: Instinct8 doesn't require git repo (unlike Codex)  
⚠️ **No Sandbox**: Instinct8 doesn't include Codex's sandbox features  

## Usage Examples

### Basic Task

```bash
# Codex
codex exec "create a FastAPI endpoint for user registration"

# Instinct8 (same!)
instinct8 exec "create a FastAPI endpoint for user registration"
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

## Migration Guide

### Step 1: Install Instinct8

```bash
git clone https://github.com/jjjorgenson/instinct8.git
cd instinct8
pip install -e .
```

### Step 2: Set Up Alias (Optional)

```bash
echo 'alias codex=instinct8' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Test

```bash
# Test that it works
instinct8 exec "Hello, what can you do?"

# If aliased, test Codex compatibility
codex exec "Hello, what can you do?"
```

### Step 4: Configure (Optional)

```bash
mkdir -p ~/.instinct8
cat > ~/.instinct8/config.json << EOF
{
  "goal": "Your default project goal",
  "constraints": ["Constraint 1", "Constraint 2"],
  "model": "gpt-4o"
}
EOF
```

## Why Replace Codex?

**Codex's compression** uses simple summarization - it may lose goal-critical information.

**Instinct8's compression** preserves goal-critical information verbatim:
- Extracts salient information using GPT-4o
- Keeps it verbatim (not summarized)
- Only compresses background context

**Result**: Better goal coherence and constraint retention in long conversations.

## Troubleshooting

**"Command not found"**
```bash
pip install -e .
```

**"OPENAI_API_KEY not set"**
```bash
export OPENAI_API_KEY="your-key"
```

**Want to keep both?**
Don't use the alias - use `instinct8` directly and keep `codex` as-is.

## Advanced Usage

See the [Instinct8 Agent README](../selective_salience/README.md) for:
- Python API usage
- Interactive mode
- Advanced configuration
- Integration examples
