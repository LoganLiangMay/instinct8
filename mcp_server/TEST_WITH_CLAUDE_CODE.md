# Testing instinct8 MCP with Claude Code

This checklist helps verify the MCP server works correctly with Claude Code.

## Pre-Testing Setup

### 1. Verify Local Installation
```bash
# Check package is built
ls -la dist/
# Should show: instinct8_mcp-0.1.0-py3-none-any.whl

# Install locally
pip install dist/instinct8_mcp-0.1.0-py3-none-any.whl

# Verify command works
instinct8-mcp --help
```

### 2. Configure Claude Code
```bash
# Edit configuration
code ~/.claude/claude_code_config.json
```

Add:
```json
{
  "mcpServers": {
    "instinct8": {
      "command": "instinct8-mcp"
    }
  }
}
```

### 3. Restart Claude Code
- Fully quit Claude Code (Cmd+Q on Mac)
- Reopen Claude Code

## Functional Tests

### Test 1: Tool Discovery
**In Claude Code, say:**
```
What MCP tools do you have available? List all tools from instinct8.
```

**Expected:** Claude should list:
- initialize_session
- compress_context
- measure_drift

### Test 2: Initialize Session
**Say:**
```
Use the initialize_session tool to set up a session with:
Goal: "Test the MCP server integration"
Constraints: ["Keep test simple", "Verify all tools work"]
```

**Expected:** Successful initialization confirmation

### Test 3: Check Session State
**Say:**
```
Show me the current session resource from instinct8
```

**Expected:** JSON showing:
- goal
- constraints
- salience_set (empty initially)
- compression_count (0)
- tokens_saved (0)

### Test 4: Compress Context
**Say:**
```
Let's test compression. First, let me tell you about various topics...
[Add some conversation]

Now use compress_context to reduce our conversation while keeping the test goal.
```

**Expected:**
- Compression completes
- Session state shows compression_count: 1
- Some tokens_saved value

### Test 5: Measure Drift
**Say:**
```
Use measure_drift to check if we're still aligned with testing the MCP server
```

**Expected:**
- Goal coherence score (0.8-1.0)
- Constraint recall score
- Behavior alignment score

### Test 6: List Strategies
**Say:**
```
Show me the available compression strategies from instinct8
```

**Expected:** List of strategies with descriptions

## Error Scenarios to Test

### Test 7: Tool Error Handling
**Say:**
```
Try to compress without initializing first (in a new conversation)
```

**Expected:** Graceful error about no session initialized

### Test 8: MCP Sampling
**Say:**
```
When you compress context, do you see the sampling requests being made to Claude?
```

**Expected:** Confirmation that MCP sampling is being used

## Performance Tests

### Test 9: Large Context
Create a long conversation and test compression performance:
1. Generate ~50 messages
2. Compress
3. Check timing and effectiveness

### Test 10: Multiple Compressions
1. Initialize session
2. Add context
3. Compress
4. Add more context
5. Compress again
6. Verify salience set grows appropriately

## Integration Tests

### Test 11: With Other MCP Servers
If you have other MCP servers configured:
```
Use both instinct8 and [other server] tools in the same conversation
```

**Expected:** Both work without conflicts

### Test 12: Session Persistence
1. Initialize a session
2. Close Claude Code
3. Reopen Claude Code
4. Check if session persists (it shouldn't - in-memory only)

## Debugging Issues

### If Tools Don't Appear
```bash
# Check if MCP server is in PATH
which instinct8-mcp

# Check Claude Code logs
# Mac: ~/Library/Application Support/Claude/logs/
# Look for MCP-related errors
```

### If Commands Fail
```bash
# Test the server directly
instinct8-mcp --version

# Check Python version (needs 3.10+)
python3 --version

# Verify all dependencies
pip show mcp
```

### If Sampling Doesn't Work
- Ensure Claude Code version supports MCP sampling
- Check that the config file is valid JSON
- Verify no other MCP servers are conflicting

## Success Criteria

✅ All 6 functional tests pass
✅ Error handling works correctly
✅ No crashes or hangs
✅ Sampling calls are visible
✅ Session state tracking works
✅ Compression actually reduces context

## Known Limitations

- Sessions are in-memory only (don't persist)
- Only one active session at a time
- Fixed compression strategy (Selective Salience)
- No custom configuration yet

## Reporting Issues

If you encounter problems:
1. Note the exact error message
2. Save Claude Code logs
3. Check the Python console output
4. Report at: https://github.com/LoganLiangMay/instinct8/issues

Include:
- Claude Code version
- Python version
- OS version
- Steps to reproduce
- Error messages/logs