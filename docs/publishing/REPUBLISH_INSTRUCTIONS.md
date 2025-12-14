# Republish Instructions - Fixed Package

## What Was Fixed

1. ✅ **Removed `selective-salience` command** - Now only 2 commands:
   - `instinct8` - Codex-compatible CLI
   - `instinct8-agent` - Interactive agent mode

2. ✅ **Fixed package structure** - Includes `evaluation` module
   - `evaluation/token_budget.py` ✅ Included
   - `evaluation/agents/` ✅ Included
   - All required modules included

3. ✅ **Fixed imports** - Removed sys.path hacks, using proper imports

## Republish Steps

### Step 1: Update Version

Edit `pyproject.toml`:
```toml
version = "0.1.1"  # Increment from 0.1.0
```

### Step 2: Rebuild

```bash
source venv/bin/activate
rm -rf dist/ build/ *.egg-info
python -m build
```

### Step 3: Test Locally (Important!)

```bash
# Install the new build
pip install dist/instinct8_agent-0.1.1-py3-none-any.whl --force-reinstall

# Test commands
instinct8 --help
instinct8-agent --help

# Test imports
python3 -c "from selective_salience import Instinct8Agent; print('✅ Works!')"
python3 -c "from strategies.strategy_h_selective_salience import SelectiveSalienceStrategy; print('✅ Strategy works!')"
```

### Step 4: If Tests Pass, Republish

```bash
python -m twine upload \
  --username __token__ \
  --password pypi-YOUR_TOKEN \
  dist/*
```

## What Users Will Get

After republishing, users install with:
```bash
pip install instinct8-agent
```

And get **2 commands**:
- `instinct8` - Codex replacement
- `instinct8-agent` - Interactive mode

No more `selective-salience` command (it was redundant).

## Verification

After republishing, verify:
1. ✅ Package installs: `pip install instinct8-agent`
2. ✅ Commands work: `instinct8 --help` and `instinct8-agent --help`
3. ✅ Imports work: `from selective_salience import Instinct8Agent`
4. ✅ No import errors when running commands
