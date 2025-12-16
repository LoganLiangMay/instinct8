# Publishing Instinct8 Agent for `brew install`

This guide shows how to publish Instinct8 Agent so users can install it with:
```bash
brew install instinct8
```

## Quick Start

### 1. Publish to PyPI

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Upload to PyPI (requires PyPI account and API token)
python -m twine upload dist/*
```

**Get PyPI credentials:**
1. Create account at https://pypi.org
2. Generate API token at https://pypi.org/manage/account/token/
3. Use: `twine upload --username __token__ --password pypi-TOKEN dist/*`

### 2. Create Homebrew Formula

**Option A: Homebrew Tap (Easiest)**

1. Create new GitHub repo: `instinct8-homebrew`
2. Copy `Formula/instinct8.rb` to that repo
3. Update SHA256 in the formula (get it from `shasum -a 256 dist/instinct8_agent-*.tar.gz`)
4. Commit and push

Users install with:
```bash
brew tap jjjorgenson/instinct8
brew install instinct8
```

**Option B: Use Publishing Script**

```bash
# Run the automated publishing script
./scripts/publish.sh
```

This will:
- Build the distribution
- Calculate SHA256
- Optionally upload to TestPyPI and PyPI
- Show you the SHA256 to update in the formula

## Step-by-Step Instructions

### Step 1: Prepare Package

The package is already configured in `pyproject.toml` with:
- Name: `instinct8-agent`
- Version: `0.1.0`
- Dependencies: All required packages
- Entry points: `instinct8` and `instinct8-agent` commands

### Step 2: Build Distribution

```bash
pip install build twine
python -m build
```

This creates `dist/` with:
- `instinct8_agent-0.1.0.tar.gz` (source)
- `instinct8_agent-0.1.0-py3-none-any.whl` (wheel)

### Step 3: Test on TestPyPI

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ instinct8-agent
instinct8 --help
```

### Step 4: Publish to PyPI

```bash
python -m twine upload dist/*
```

Now users can install with:
```bash
pip install instinct8-agent
```

### Step 5: Create Homebrew Formula

1. **Create formula repository:**
   ```bash
   # Create new repo on GitHub: instinct8-homebrew
   git clone https://github.com/jjjorgenson/instinct8-homebrew.git
   cd instinct8-homebrew
   mkdir Formula
   ```

2. **Copy formula:**
   ```bash
   cp /path/to/instinct8/Formula/instinct8.rb Formula/
   ```

3. **Get SHA256:**
   ```bash
   shasum -a 256 dist/instinct8_agent-0.1.0.tar.gz
   ```

4. **Update formula** with the SHA256 and PyPI URL

5. **Commit and push:**
   ```bash
   git add Formula/instinct8.rb
   git commit -m "Add Instinct8 formula"
   git push
   ```

### Step 6: Users Install via Homebrew

```bash
brew tap jjjorgenson/instinct8
brew install instinct8
```

## Alternative: Recommend pipx

Since Homebrew formulas can be complex, you might want to recommend `pipx` instead:

```bash
# Users install with pipx (isolated Python environment)
pipx install instinct8-agent

# Then use
instinct8 "create a FastAPI endpoint"
```

This is simpler and doesn't require maintaining a Homebrew formula.

## Updating Versions

For future releases:

1. Update version in `pyproject.toml`
2. Rebuild: `python -m build`
3. Upload: `twine upload dist/*`
4. Update Homebrew formula SHA256 and version

## Troubleshooting

**"Package already exists"**
- Increment version in `pyproject.toml`

**"Invalid credentials"**
- Use API token: `twine upload --username __token__ --password pypi-TOKEN dist/*`

**Homebrew installation fails**
- Check formula URL points to correct PyPI package
- Verify SHA256 matches the uploaded file
- Check Python version compatibility

## Files Created

- `PUBLISHING_GUIDE.md` - Detailed publishing guide
- `Formula/instinct8.rb` - Homebrew formula template
- `scripts/publish.sh` - Automated publishing script
- `.pypirc.example` - PyPI credentials template

## Next Steps

1. Run `./scripts/publish.sh` to build and get SHA256
2. Create `instinct8-homebrew` repo
3. Add formula to that repo
4. Test installation: `brew tap jjjorgenson/instinct8 && brew install instinct8`
5. Update installation docs to include Homebrew option
