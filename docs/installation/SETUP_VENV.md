# Setting Up Virtual Environment for Publishing

On macOS with Homebrew Python, you need a virtual environment to install build tools.

## Quick Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Now install build tools
pip install build twine

# Build and publish
python -m build
python -m twine upload --username __token__ --password pypi-YOUR_TOKEN dist/*
```

## Or Use pipx (Recommended for CLI Tools)

```bash
# Install pipx
brew install pipx

# Install build tools via pipx
pipx install build
pipx install twine

# Use them
python3 -m build
python3 -m twine upload --username __token__ --password pypi-YOUR_TOKEN dist/*
```

## Updated Publishing Script

The `scripts/publish.sh` script will now handle this automatically.
