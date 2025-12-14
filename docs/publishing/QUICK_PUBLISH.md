# Quick Publish Guide

## 1. Get PyPI Token

1. Create account: https://pypi.org
2. Get token: https://pypi.org/manage/account/token/
3. Save token

## 2. Set Up Virtual Environment (macOS)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install tools
pip install build twine

# Build
python -m build

# Test on TestPyPI first (optional)
python -m twine upload --repository testpypi \
  --username __token__ \
  --password pypi-YOUR_TEST_TOKEN \
  dist/*

# Publish to PyPI
python -m twine upload \
  --username __token__ \
  --password pypi-YOUR_TOKEN \
  dist/*
```

**Or use the automated script:**
```bash
./scripts/publish.sh
```

**Where to get token:**
1. Create account: https://pypi.org
2. Get token: https://pypi.org/manage/account/token/
3. Copy token (starts with `pypi-`)
4. Use `__token__` as username, token as password

## 3. Done!

Users can now install with:
```bash
pip install instinct8-agent
```

See PUBLISH_CHECKLIST.md for detailed steps.
