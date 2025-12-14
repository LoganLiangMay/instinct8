# Quick Start - Publishing (macOS)

## Step 1: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 2: Install Build Tools

```bash
pip install build twine
```

## Step 3: Build

```bash
python -m build
```

## Step 4: Get PyPI Token

1. Go to https://pypi.org/manage/account/token/
2. Create new token
3. Copy it (starts with `pypi-`)

## Step 5: Publish

```bash
python -m twine upload \
  --username __token__ \
  --password pypi-YOUR_TOKEN_HERE \
  dist/*
```

## Done!

Users can now install with:
```bash
pip install instinct8-agent
```

## Or Use the Script

```bash
./scripts/publish.sh
```

The script will:
- Create venv automatically
- Install tools
- Build distribution
- Prompt for upload
