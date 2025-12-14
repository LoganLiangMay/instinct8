# Fix Package Import Issues

## Problems Found

1. **Missing `evaluation` module in package** - When installed, `strategies` can't import from `evaluation`
2. **Three commands** - Should be just two: `instinct8` and `instinct8-agent`
3. **Import paths** - Need to work when installed as a package

## Solutions Applied

### 1. Updated pyproject.toml

- ✅ Included `evaluation` module in packages
- ✅ Removed `selective-salience` command
- ✅ Fixed package discovery

### 2. Fixed Imports

- ✅ Removed sys.path hacks from `compressor.py`
- ✅ Removed sys.path hacks from `codex_integration.py`
- ✅ Using proper absolute imports

### 3. Removed Redundant Command

- ✅ Removed `selective-salience` command
- ✅ Kept `instinct8` (Codex replacement)
- ✅ Kept `instinct8-agent` (Interactive mode)

## Next Steps to Fix

### Step 1: Rebuild Package

```bash
source venv/bin/activate
rm -rf dist/ build/ *.egg-info
python -m build
```

### Step 2: Test Locally Before Republishing

```bash
# Install the new build locally
pip install dist/instinct8_agent-0.1.0-py3-none-any.whl --force-reinstall

# Test commands
instinct8 --help
instinct8-agent --help

# Test imports
python3 -c "from selective_salience import Instinct8Agent; print('✅ Works!')"
```

### Step 3: If Tests Pass, Republish

```bash
# Update version in pyproject.toml to 0.1.1
# Then rebuild and upload
python -m build
python -m twine upload dist/*
```

## What Users Will See

After fix, users will have **2 commands**:
- `instinct8` - Codex-compatible CLI
- `instinct8-agent` - Interactive agent mode

The `selective-salience` command is removed (it was redundant).
