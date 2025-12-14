# PyPI API Token Setup

Guide on where and how to provide your PyPI API token when publishing.

## Option 1: Command Line (Easiest - Recommended)

Provide the token directly in the upload command:

```bash
python -m twine upload --username __token__ --password pypi-YOUR_TOKEN_HERE dist/*
```

**Replace `pypi-YOUR_TOKEN_HERE` with your actual token from PyPI.**

Example:
```bash
python -m twine upload --username __token__ --password pypi-AgEIcHlwaS5vcmcCJGY4ZjE2YjY0LWE5YzQtNDY5Yi1hYzY1LWIzYzE2YjY0LWE5YzQAAIsCJXYxMjM0NTY3OC0xMjM0LTQ1NjctODkwMS0xMjM0NTY3ODkwMTIzAAIFFgA dist/*
```

## Option 2: Environment Variables

Set environment variables before running twine:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE

python -m twine upload dist/*
```

**To make this permanent**, add to your shell config:

```bash
# For bash
echo 'export TWINE_USERNAME=__token__' >> ~/.bashrc
echo 'export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE' >> ~/.bashrc
source ~/.bashrc

# For zsh
echo 'export TWINE_USERNAME=__token__' >> ~/.zshrc
echo 'export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE' >> ~/.zshrc
source ~/.zshrc
```

## Option 3: .pypirc File (Traditional)

Create `~/.pypirc` file in your home directory:

```bash
# Create the file
nano ~/.pypirc
```

Add this content:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

**Replace the tokens with your actual tokens.**

Then upload:
```bash
python -m twine upload dist/*
```

**Security Note**: Make sure to set proper permissions:
```bash
chmod 600 ~/.pypirc
```

## Option 4: Interactive Prompt

If you don't provide credentials, twine will prompt you:

```bash
python -m twine upload dist/*
# Username: __token__
# Password: pypi-YOUR_TOKEN_HERE
```

## Getting Your PyPI Token

1. **Create PyPI account** (if you don't have one):
   - Go to https://pypi.org/account/register/

2. **Generate API token**:
   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Give it a name (e.g., "instinct8-agent")
   - Choose scope:
     - **Entire account** (can upload any project)
     - **Project: instinct8-agent** (only this project)
   - Click "Add token"
   - **Copy the token immediately** (you won't see it again!)
   - Format: `pypi-AgEIcHlwaS5vcmcC...` (starts with `pypi-`)

3. **Use the token**:
   - Username: `__token__` (literally these characters)
   - Password: Your token (the `pypi-...` string)

## Quick Reference

**For TestPyPI:**
```bash
python -m twine upload --repository testpypi \
  --username __token__ \
  --password pypi-YOUR_TEST_TOKEN \
  dist/*
```

**For Production PyPI:**
```bash
python -m twine upload \
  --username __token__ \
  --password pypi-YOUR_TOKEN \
  dist/*
```

## Security Best Practices

1. ✅ **Use project-scoped tokens** when possible (more secure)
2. ✅ **Never commit tokens** to git (add to `.gitignore`)
3. ✅ **Use environment variables** or `.pypirc` (not command line history)
4. ✅ **Rotate tokens** periodically
5. ✅ **Delete unused tokens** from PyPI account

## Troubleshooting

**"Invalid credentials"**
- Make sure username is exactly `__token__` (with underscores)
- Make sure password includes the full token starting with `pypi-`
- Check that token hasn't expired or been revoked

**"Token not found"**
- Go to https://pypi.org/manage/account/token/ and verify token exists
- Make sure you copied the entire token

**"Permission denied"**
- If using project-scoped token, make sure project name matches exactly
- Try using account-scoped token instead

## Recommended Approach

For one-time publishing, use **Option 1** (command line):
```bash
python -m twine upload --username __token__ --password pypi-YOUR_TOKEN dist/*
```

For frequent publishing, use **Option 3** (`.pypirc` file):
- Set it up once
- Then just run `python -m twine upload dist/*`
