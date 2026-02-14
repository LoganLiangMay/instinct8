# URGENT: Publish instinct8-mcp to PyPI

The package is built and ready. This is **blocking all users** from installing.

## Quick Publish (If you have PyPI account)

```bash
# From /Applications/Projects/instinct8_2
python3 -m twine upload dist/*

# Enter your PyPI username and password/token
```

## First Time Setup (If no PyPI account)

1. **Create PyPI Account**: https://pypi.org/account/register/

2. **Create API Token**:
   - Go to https://pypi.org/manage/account/token/
   - Name: "instinct8-mcp publishing"
   - Scope: "Entire account" (for first upload)
   - Copy the token (starts with `pypi-`)

3. **Configure Token**:
   ```bash
   # Create/edit ~/.pypirc
   cat > ~/.pypirc << 'EOF'
   [pypi]
   username = __token__
   password = YOUR_TOKEN_HERE
   EOF

   chmod 600 ~/.pypirc
   ```

4. **Upload Package**:
   ```bash
   cd /Applications/Projects/instinct8_2
   python3 -m twine upload dist/*
   ```

## Verify Success

After uploading:
```bash
# Test installation
pip install instinct8-mcp

# Verify it works
instinct8-mcp --help
```

## Impact

Once published, users can finally:
- Install with `pip install instinct8-mcp` ✓
- Follow the documentation ✓
- Use instinct8 with Claude Code ✓

**Current Status**: 100% of users blocked
**After Publishing**: Installation possible!

## Files Ready

✅ `dist/instinct8_mcp-0.1.0-py3-none-any.whl` (18KB)
✅ `dist/instinct8_mcp-0.1.0.tar.gz` (22KB)

Both files are built and ready for upload.