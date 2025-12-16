# User Installation Guide

**How to install Instinct8 Agent (for end users)**

## Installation

### Step 1: Install the Package

```bash
pip install instinct8-agent
```

**On macOS/Linux**, you might need:
```bash
pip3 install instinct8-agent
```

**Or use pipx (recommended):**
```bash
pipx install instinct8-agent
```

### Step 2: Set Your API Key

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Get your API key from: https://platform.openai.com/api-keys

### Step 3: Test Installation

```bash
instinct8 --help
```

You should see help text. If so, installation is successful! ✅

## Usage

### Basic Usage

```bash
instinct8 "create a FastAPI endpoint"
```

### Interactive Mode

```bash
instinct8-agent interactive \
  --goal "Build a FastAPI app" \
  --constraints "Use JWT" "Hash passwords"
```

### As Codex Replacement

```bash
# Alias to replace Codex
alias codex=instinct8

# Now use Codex commands
codex exec "create a login endpoint"
```

## Updating

If you already have Instinct8 Agent installed:

```bash
# Upgrade to latest version
pip install --upgrade instinct8-agent

# Or with pipx
pipx upgrade instinct8-agent
```

## Troubleshooting

**"Command not found: instinct8"**
- Make sure pip install completed successfully
- Try: `pip3 install instinct8-agent`
- Or use: `pipx install instinct8-agent`

**"Import errors" (if you have 0.1.0)**
```bash
# Upgrade to 0.1.1 or later
pip install --upgrade instinct8-agent
```

**"OPENAI_API_KEY not set"**
```bash
export OPENAI_API_KEY="your-key"
```

**"Permission denied"**
- Use virtual environment: `python3 -m venv venv && source venv/bin/activate`
- Or use pipx: `pipx install instinct8-agent`

## Need Help?

- Full guide: [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- Quick start: [QUICKSTART.md](QUICKSTART.md)
- Documentation: [README.md](README.md)
