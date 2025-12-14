# Fixing Import Errors

The package needs to include all required modules. Here's what needs to be fixed:

## Issues Found

1. **Missing `evaluation` module** - `strategies.strategy_b_codex` imports from `evaluation.token_budget`
2. **Import paths** - Need to work when installed as a package
3. **Redundant command** - `selective-salience` should be removed

## Fixes Applied

1. ✅ Updated `pyproject.toml` to include `evaluation` module
2. ✅ Removed `selective-salience` command
3. ✅ Fixed import paths in `compressor.py` and `codex_integration.py`
4. ✅ Added `MANIFEST.in` to ensure all files are included

## Next Steps

1. **Rebuild the package:**
   ```bash
   source venv/bin/activate
   python -m build
   ```

2. **Test locally before republishing:**
   ```bash
   pip install dist/instinct8_agent-0.1.0-py3-none-any.whl --force-reinstall
   instinct8-agent --help
   ```

3. **If it works, republish:**
   ```bash
   python -m twine upload dist/*
   ```

## Commands After Fix

Users will have **2 commands**:
- `instinct8` - Codex-compatible CLI
- `instinct8-agent` - Interactive agent mode

The `selective-salience` command has been removed.
