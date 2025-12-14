# Publishing Checklist - Open Source

Quick checklist to publish Instinct8 Agent to PyPI.

## Pre-Publishing Checklist

- [x] Package name set: `instinct8-agent`
- [x] Version set: `0.1.0`
- [x] License: Apache 2.0
- [x] Entry points configured: `instinct8` and `instinct8-agent`
- [x] Dependencies listed in `pyproject.toml`
- [x] README.md exists and is informative
- [ ] **TODO**: Get PyPI account and API token
- [ ] **TODO**: Test build locally
- [ ] **TODO**: Test on TestPyPI first

## Step-by-Step Publishing

### 1. Get PyPI Credentials

1. Create account at https://pypi.org
2. Go to https://pypi.org/manage/account/token/
3. Create API token (scope: entire account or just this project)
4. Save token securely

### 2. Install Build Tools

```bash
pip3 install build twine
```

### 3. Build Distribution

```bash
python3 -m build
```

This creates:
- `dist/instinct8_agent-0.1.0.tar.gz`
- `dist/instinct8_agent-0.1.0-py3-none-any.whl`

### 4. Test on TestPyPI First

```bash
# Upload to TestPyPI
python3 -m twine upload --repository testpypi \
  --username __token__ \
  --password pypi-YOUR_TEST_TOKEN \
  dist/*

# Test installation
pip3 install --index-url https://test.pypi.org/simple/ instinct8-agent
instinct8 --help
```

### 5. Publish to Production PyPI

```bash
# Upload to PyPI with token
python3 -m twine upload \
  --username __token__ \
  --password pypi-YOUR_TOKEN \
  dist/*

# Or if you set up .pypirc file:
python3 -m twine upload dist/*
```

**Get your token:**
1. Go to https://pypi.org/manage/account/token/
2. Create new token
3. Copy it (starts with `pypi-`)
4. Use `__token__` as username, your token as password

### 6. Verify Installation

```bash
# Install from PyPI
pip install instinct8-agent

# Test commands
instinct8 --help
instinct8-agent --help
instinct8 "Hello, what can you do?"
```

## Quick Publish Script

Or use the automated script:

```bash
./scripts/publish.sh
```

## After Publishing

- [ ] Update installation docs to mention PyPI
- [ ] Test installation on clean environment
- [ ] Announce release (GitHub, social media, etc.)
- [ ] Monitor for issues/feedback

## Version Updates

For future releases:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md (if you create one)
3. Rebuild: `python -m build`
4. Upload: `python -m twine upload dist/*`

## Troubleshooting

**"Package already exists"**
- Increment version in `pyproject.toml`

**"Invalid credentials"**
- Use API token: `twine upload --username __token__ --password pypi-TOKEN dist/*`

**"Command not found: python"**
- Use `python3` instead of `python`

## Notes

- ✅ Code will be **open source** and visible to everyone
- ✅ Users can inspect, modify, and fork
- ✅ Great for community building
- ✅ Easy distribution via PyPI
