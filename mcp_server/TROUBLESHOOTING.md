# 🔧 Troubleshooting Guide: instinct8 MCP Server

Follow these decision trees to solve common problems.

---

## Problem: Can't Install instinct8-mcp

```
pip install instinct8-mcp fails?
│
├─ Error: "No matching distribution found"
│  └─ Package not yet on PyPI
│     └─ Install from source:
│        git clone https://github.com/LoganLiangMay/instinct8.git
│        cd instinct8/mcp_server
│        pip install -e .
│
├─ Error: "Permission denied"
│  └─ Using system Python
│     ├─ Try: pip install --user instinct8-mcp
│     └─ Or use virtual environment:
│        python3 -m venv myenv
│        source myenv/bin/activate
│        pip install instinct8-mcp
│
└─ Error: "Python version not supported"
   └─ Requires Python 3.10+
      └─ Check version: python3 --version
         └─ Upgrade Python if needed
```

---

## Problem: MCP Tools Not Appearing in Claude Code

```
instinct8 tools not showing?
│
├─ Did you restart Claude Code?
│  ├─ No → Fully quit (Cmd+Q/Alt+F4) and reopen
│  └─ Yes → Continue ↓
│
├─ Is instinct8-mcp installed?
│  ├─ Check: pip show instinct8-mcp
│  ├─ Not found → Install it: pip install instinct8-mcp
│  └─ Found → Continue ↓
│
├─ Is config file correct?
│  ├─ macOS/Linux: ~/.claude/claude_code_config.json
│  ├─ Windows: %USERPROFILE%\.claude\claude_code_config.json
│  ├─ File doesn't exist → Create it (see below)
│  └─ File exists → Continue ↓
│
├─ Is JSON valid?
│  ├─ Test at: jsonlint.com
│  ├─ Invalid → Fix syntax errors
│  └─ Valid → Continue ↓
│
├─ Is instinct8-mcp in PATH?
│  ├─ Check: which instinct8-mcp (or where on Windows)
│  ├─ Not found → Add to PATH (see below)
│  └─ Found → Continue ↓
│
└─ Still not working?
   └─ Try absolute path in config:
      "command": "/full/path/to/instinct8-mcp"
```

### Creating Config File

```bash
# macOS/Linux
mkdir -p ~/.claude
cat > ~/.claude/claude_code_config.json << 'EOF'
{
  "mcpServers": {
    "instinct8": {
      "command": "instinct8-mcp"
    }
  }
}
EOF

# Windows (in PowerShell)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude"
@'
{
  "mcpServers": {
    "instinct8": {
      "command": "instinct8-mcp"
    }
  }
}
'@ | Out-File "$env:USERPROFILE\.claude\claude_code_config.json"
```

---

## Problem: "Command not found: instinct8-mcp"

```
Command not found?
│
├─ Where is it installed?
│  └─ pip show instinct8-mcp | grep Location
│     └─ Note the location (e.g., /usr/local/lib/python3.11/site-packages)
│
├─ Add to PATH:
│  ├─ macOS/Linux:
│  │  export PATH="$PATH:$(python3 -m site --user-base)/bin"
│  │  # Add to ~/.bashrc or ~/.zshrc to make permanent
│  │
│  └─ Windows:
│     set PATH=%PATH%;%APPDATA%\Python\Scripts
│     # Or add via System Properties → Environment Variables
│
└─ Still not found?
   └─ Use full path in config:
      └─ Find it: find / -name instinct8-mcp 2>/dev/null
         └─ Use that path in claude_code_config.json
```

---

## Problem: Tools Appear But Don't Work

```
Tools visible but failing?
│
├─ Error: "Session not initialized"
│  └─ You need to initialize first
│     └─ Use initialize_session before other tools
│
├─ Error: "Sampling failed"
│  └─ MCP sampling issue
│     ├─ Claude Code version too old?
│     ├─ Try updating Claude Code
│     └─ Check Claude Code logs (see below)
│
├─ Error: "No module named 'mcp'"
│  └─ Dependency missing
│     └─ pip install mcp>=1.0.0
│
└─ Other errors?
   └─ Check server logs
      └─ Look for error details in output
```

---

## Problem: Configuration File Confusion

```
Which config file?
│
├─ Multiple files mentioned in docs?
│  └─ Use THIS one for your OS:
│     ├─ macOS: ~/.claude/claude_code_config.json
│     ├─ Linux: ~/.claude/claude_code_config.json
│     └─ Windows: %USERPROFILE%\.claude\claude_code_config.json
│
├─ File already exists with other servers?
│  └─ Add instinct8 to existing "mcpServers" section:
│     {
│       "mcpServers": {
│         "existing-server": { ... },
│         "instinct8": {
│           "command": "instinct8-mcp"
│         }
│       }
│     }
│
└─ JSON syntax errors?
   └─ Common mistakes:
      ├─ Missing comma between servers
      ├─ Extra comma after last item
      ├─ Wrong quotes (use double quotes ")
      └─ Validate at: jsonlint.com
```

---

## Problem: Session Lost After Restart

```
Session disappeared?
│
└─ This is EXPECTED behavior
   └─ Sessions are in-memory only
      └─ Not persisted across restarts
         └─ Workaround: Re-initialize after restart
            └─ Future feature: Session export/import
```

---

## Common Error Messages

### "ModuleNotFoundError: No module named 'instinct8_mcp'"
```bash
# Package not installed
pip install instinct8-mcp
```

### "PermissionError: [Errno 13] Permission denied"
```bash
# Install with --user flag
pip install --user instinct8-mcp
```

### "JSONDecodeError: Expecting property name"
```bash
# Fix JSON syntax in config file
# Common: trailing commas, single quotes
```

### "instinct8-mcp: command not found"
```bash
# Add Python bin to PATH
export PATH="$PATH:$(python3 -m site --user-base)/bin"
```

---

## Diagnostic Commands

Run these to gather information:

```bash
# 1. Check Python version
python3 --version

# 2. Check if package installed
pip show instinct8-mcp

# 3. Find installation location
pip show instinct8-mcp | grep Location

# 4. Check if command exists
which instinct8-mcp  # macOS/Linux
where instinct8-mcp  # Windows

# 5. Test the command directly
instinct8-mcp --help

# 6. Check config file
cat ~/.claude/claude_code_config.json  # macOS/Linux
type %USERPROFILE%\.claude\claude_code_config.json  # Windows

# 7. Validate JSON
python3 -m json.tool ~/.claude/claude_code_config.json

# 8. Check PATH
echo $PATH  # macOS/Linux
echo %PATH%  # Windows
```

---

## Claude Code Logs

Find logs for advanced debugging:

- **macOS**: `~/Library/Application Support/Claude/logs/`
- **Windows**: `%APPDATA%\Claude\logs\`
- **Linux**: `~/.config/Claude/logs/`

Look for:
- MCP server startup errors
- Connection failures
- Sampling errors

---

## Still Stuck?

### Quick Checklist

- [ ] Python 3.10+ installed
- [ ] `pip install instinct8-mcp` succeeded
- [ ] Config file exists at correct location
- [ ] JSON is valid (no syntax errors)
- [ ] Claude Code fully restarted
- [ ] `instinct8-mcp` command works in terminal
- [ ] No error messages in Claude Code

### Get Help

1. **GitHub Issues**: https://github.com/LoganLiangMay/instinct8/issues
   - Include diagnostic command outputs
   - Share your config file (remove sensitive data)
   - Describe what you tried

2. **Quick Test**: Try the minimal example in [QUICKSTART.md](QUICKSTART.md)

3. **Alternative**: Install from source
   ```bash
   git clone https://github.com/LoganLiangMay/instinct8.git
   cd instinct8/mcp_server
   pip install -e .
   ```

---

## Prevention Tips

1. **Always restart Claude Code** after config changes
2. **Validate JSON** before saving config
3. **Use absolute paths** if relative paths fail
4. **Check logs** when things go wrong
5. **Keep Python updated** (3.10+ required)

---

**Remember**: Most issues are installation or config related. The decision trees above solve 90% of problems!