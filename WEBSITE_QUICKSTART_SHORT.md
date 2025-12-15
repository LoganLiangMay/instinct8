# Get Started with Instinct8

## Install & Run

```bash
# 1. Install
pip install instinct8-agent

# 2. Set API key
export OPENAI_API_KEY="your-key"

# 3. Run (file operations enabled by default)
instinct8

# 4. Enable command execution (optional)
instinct8 --allow-execution
```

## Quick Commands

**File Operations** (work immediately):
- `review my files` - Read files
- `create hello.py` - Create files
- `edit main.py` - Edit files

**Command Execution** (requires `--allow-execution`):
- `run npm install` - Execute commands
- `execute python test.py` - Run scripts

## Example

```bash
$ instinct8 --allow-execution
instinct8> create a FastAPI login endpoint
✅ Created app.py
instinct8> run pip install fastapi
✅ Installed dependencies
```

**That's it!** Instinct8 preserves your goals across long conversations.
