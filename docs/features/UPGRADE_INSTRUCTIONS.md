# Upgrade Instructions for Users

## How to Update Instinct8 Agent

If you already have `instinct8-agent` installed, here's how to update to the latest version.

### Method 1: Standard Upgrade (Recommended)

```bash
pip install --upgrade instinct8-agent
```

**Or with pipx:**
```bash
pipx upgrade instinct8-agent
```

### Method 2: Force Reinstall

If you're having issues, force reinstall:

```bash
pip install --upgrade --force-reinstall instinct8-agent
```

**Or with pipx:**
```bash
pipx reinstall instinct8-agent
```

### Method 3: Uninstall and Reinstall

```bash
pip uninstall instinct8-agent
pip install instinct8-agent
```

## Verify Update

After upgrading, verify you have the latest version:

```bash
# Check version
pip show instinct8-agent

# Test commands (should work without errors)
instinct8 --help
instinct8-agent --help
```

## What Changed in 0.1.1

- ✅ **Fixed import errors** - All modules now included properly
- ✅ **Removed `selective-salience` command** - Now only 2 commands:
  - `instinct8` - Codex-compatible CLI
  - `instinct8-agent` - Interactive mode
- ✅ **Better package structure** - All dependencies included

## Troubleshooting

**"Command not found after upgrade"**
```bash
# Reinstall to refresh command paths
pip install --force-reinstall instinct8-agent
```

**"Still getting import errors"**
```bash
# Clear pip cache and reinstall
pip cache purge
pip install --upgrade --force-reinstall instinct8-agent
```

**"Version didn't update"**
```bash
# Check current version
pip show instinct8-agent

# If still 0.1.0, force upgrade
pip install --upgrade --force-reinstall instinct8-agent
```

## Automatic Updates

Users can check for updates:
```bash
pip list --outdated | grep instinct8-agent
```

If an update is available, run:
```bash
pip install --upgrade instinct8-agent
```
