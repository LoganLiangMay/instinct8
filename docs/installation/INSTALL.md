# Installation - Instinct8 Agent

## Quick Install (30 seconds)

```bash
# Install from PyPI
pip install instinct8-agent

# Set API key
export OPENAI_API_KEY="your-api-key"

# Test it
instinct8 "Hello!"
```

## Installation Methods

### Option 1: pip (Standard)

```bash
pip install instinct8-agent
```

### Option 2: pipx (Recommended for CLI Tools)

```bash
pipx install instinct8-agent
```

### Option 3: From Source

```bash
git clone https://github.com/jjjorgenson/instinct8.git
cd instinct8
pip install -e .
```

## Verify Installation

```bash
instinct8 --help
instinct8-agent --help
```

## Requirements

- Python 3.9+
- OpenAI API key

## Next Steps

- See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed instructions
- See [QUICKSTART.md](QUICKSTART.md) for usage examples
- See [README.md](README.md) for full documentation
