# Publishing Instinct8 Agent

Guide to publish Instinct8 Agent so users can install it via `brew install` or `pip install`.

## Overview

To enable `brew install instinct8`, we need to:
1. Publish to PyPI (Python Package Index)
2. Create a Homebrew formula/tap

## Step 1: Prepare for PyPI Publishing

### Update pyproject.toml

Make sure `pyproject.toml` has all required metadata:

```toml
[project]
name = "instinct8-agent"
version = "0.1.0"
description = "Instinct8 Agent - Coding agent with Selective Salience Compression"
readme = "README.md"
license = {text = "Apache-2.0"}
authors = [
    {name = "Instinct8", email = "info@instinct8.ai"}
]
keywords = ["llm", "compression", "context", "agents", "salience", "goal-preservation"]
requires-python = ">=3.9"
dependencies = [
    "openai>=1.0.0",
    "numpy>=1.24.0",
    "sentence-transformers>=2.2.0",
    "scikit-learn>=1.2.0",
    "tiktoken>=0.5.0",
]

[project.urls]
Homepage = "https://github.com/jjjorgenson/instinct8"
Documentation = "https://github.com/jjjorgenson/instinct8/blob/main/README.md"
Repository = "https://github.com/jjjorgenson/instinct8"
```

### Create Distribution Files

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# This creates:
# - dist/instinct8_agent-0.1.0.tar.gz (source distribution)
# - dist/instinct8_agent-0.1.0-py3-none-any.whl (wheel)
```

## Step 2: Publish to PyPI

### Test on TestPyPI First

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ instinct8-agent
```

### Publish to Production PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# Users can now install via:
pip install instinct8-agent
```

**Note**: You'll need PyPI credentials. Create account at https://pypi.org and get API token.

## Step 3: Create Homebrew Formula

### Option A: Homebrew Tap (Recommended)

Create a separate repository for the Homebrew formula:

```bash
# Create new repo: instinct8-homebrew
git clone https://github.com/jjjorgenson/instinct8-homebrew.git
cd instinct8-homebrew
```

Create `Formula/instinct8.rb`:

```ruby
class Instinct8 < Formula
  desc "Instinct8 Agent - Coding agent with Selective Salience Compression"
  homepage "https://github.com/jjjorgenson/instinct8"
  url "https://files.pythonhosted.org/packages/source/i/instinct8-agent/instinct8-agent-0.1.0.tar.gz"
  sha256 "SHA256_HASH_HERE"  # Calculate with: shasum -a 256 dist/instinct8_agent-0.1.0.tar.gz
  license "Apache-2.0"

  depends_on "python@3.9"

  def install
    system "python3", "-m", "pip", "install", "--prefix=#{prefix}", "."
  end

  test do
    system "#{bin}/instinct8", "--help"
  end
end
```

**Calculate SHA256:**
```bash
shasum -a 256 dist/instinct8_agent-0.1.0.tar.gz
```

### Option B: Homebrew Core (Official)

Submit to Homebrew core (requires approval):
- Fork https://github.com/Homebrew/homebrew-core
- Create formula in `Formula/instinct8.rb`
- Submit PR

## Step 4: Alternative - Use pipx for CLI Installation

Since Homebrew can be complex, consider recommending `pipx`:

```bash
# Users install via pipx (isolated Python environment)
pipx install instinct8-agent

# Then use
instinct8 "create a FastAPI endpoint"
```

## Step 5: Update Installation Instructions

Once published, update `INSTALLATION_GUIDE.md`:

```markdown
## Installation via Homebrew

```bash
brew tap jjjorgenson/instinct8
brew install instinct8
```

## Installation via pip

```bash
pip install instinct8-agent
```

## Installation via pipx (Recommended for CLI)

```bash
pipx install instinct8-agent
```
```

## Quick Publishing Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update `README.md` with installation instructions
- [ ] Build distribution: `python -m build`
- [ ] Test on TestPyPI: `twine upload --repository testpypi dist/*`
- [ ] Test installation: `pip install --index-url https://test.pypi.org/simple/ instinct8-agent`
- [ ] Publish to PyPI: `twine upload dist/*`
- [ ] Create Homebrew formula
- [ ] Test Homebrew installation
- [ ] Update documentation

## Version Management

For future releases:

```bash
# Update version in pyproject.toml
# Then rebuild and publish
python -m build
twine upload dist/*
```

## Troubleshooting

**"Package already exists"**
- Increment version number in `pyproject.toml`

**"Invalid credentials"**
- Create API token at https://pypi.org/manage/account/token/
- Use: `twine upload --username __token__ --password pypi-TOKEN dist/*`

**Homebrew formula not found**
- Make sure tap is added: `brew tap jjjorgenson/instinct8`
- Or use full path: `brew install jjjorgenson/instinct8/instinct8`
