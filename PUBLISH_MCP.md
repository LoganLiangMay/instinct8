# Publishing instinct8-mcp to PyPI

The MCP server package has been prepared and is ready to publish. Follow these steps:

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **API Token**: Generate a token at https://pypi.org/manage/account/token/
3. **Configure Token**: Save to `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJGNhNzg5ZTk1LT... (your token here)
```

## Publishing Steps

### 1. Verify Package
```bash
# Check the package contents
tar tzf dist/instinct8_mcp-0.1.0.tar.gz

# Test installation locally
pip install dist/instinct8_mcp-0.1.0-py3-none-any.whl
```

### 2. Upload to Test PyPI (Optional but Recommended)
```bash
# Upload to test server first
python3 -m twine upload --repository testpypi dist/*

# Test installation from test server
pip install --index-url https://test.pypi.org/simple/ instinct8-mcp
```

### 3. Upload to Production PyPI
```bash
# Upload to PyPI
python3 -m twine upload dist/*

# Should output:
# Uploading distributions to https://upload.pypi.org/legacy/
# Uploading instinct8_mcp-0.1.0-py3-none-any.whl
# Uploading instinct8_mcp-0.1.0.tar.gz
# View at: https://pypi.org/project/instinct8-mcp/0.1.0/
```

### 4. Verify Installation
```bash
# Test installation from PyPI
pip install instinct8-mcp

# Verify it runs
instinct8-mcp --help
```

## After Publishing

1. **Update Documentation**:
   - Announce on social media
   - Create a blog post about the MCP integration
   - Submit to Claude Code MCP server registry (if exists)

2. **Monitor Feedback**:
   - Watch for issues on GitHub
   - Check PyPI download statistics
   - Respond to user questions

## Current Status

✅ Package built successfully (dist/ directory contains both wheel and source)
✅ CHANGELOG.md created
✅ Main README updated with MCP server section
✅ Dependencies installed and tested
✅ Server module loads without errors

⚠️ **Action Required**: You need to run the `twine upload` command with your PyPI credentials

## Troubleshooting

If you encounter "403 Forbidden":
- Verify your API token is valid
- Check if the package name is already taken
- Try a different name if needed (e.g., instinct8-mcp-server)

If you encounter "400 Bad Request":
- Check that version 0.1.0 hasn't been uploaded already
- Increment version in pyproject.toml if needed
- Rebuild with `python3 -m build`