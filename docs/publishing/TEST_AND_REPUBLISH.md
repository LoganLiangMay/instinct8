# Test and Republish - Version 0.1.1

## ✅ Version Updated and Built

Version has been updated to **0.1.1** and package has been rebuilt with fixes:
- ✅ Removed `selective-salience` command
- ✅ Fixed package structure (includes evaluation module)
- ✅ Fixed imports

## Step 1: Test Locally

```bash
# Install the new build locally
pip install dist/instinct8_agent-0.1.1-py3-none-any.whl --force-reinstall

# Test commands
instinct8 --help
instinct8-agent --help

# Test imports
python3 -c "from selective_salience import Instinct8Agent; print('✅ Import works!')"
python3 -c "from strategies.strategy_h_selective_salience import SelectiveSalienceStrategy; print('✅ Strategy import works!')"
```

## Step 2: If Tests Pass, Republish

```bash
source venv/bin/activate
python -m twine upload \
  --username __token__ \
  --password pypi-YOUR_TOKEN \
  dist/instinct8_agent-0.1.1*
```

## What's Fixed

1. **Only 2 commands now:**
   - `instinct8` - Codex-compatible CLI
   - `instinct8-agent` - Interactive mode
   - ❌ `selective-salience` removed (was redundant)

2. **All modules included:**
   - ✅ `evaluation` module included
   - ✅ `evaluation.token_budget` included
   - ✅ `evaluation.agents.codex_agent` included
   - ✅ All imports should work

3. **Import errors fixed:**
   - ✅ Removed sys.path hacks
   - ✅ Using proper package imports

## After Republishing

Users install with:
```bash
pip install instinct8-agent
```

And get 2 working commands with no import errors!
