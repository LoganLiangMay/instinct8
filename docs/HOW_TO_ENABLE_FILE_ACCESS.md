# How to Enable File Access in Instinct8

## Quick Answer

**You don't need to do anything!** File operations (read/write/edit) are **already enabled by default**.

## What's Already Working

✅ **File Reading** - Already enabled  
✅ **File Writing** - Already enabled  
✅ **File Editing** - Already enabled  
✅ **File Creation** - Already enabled  

## What Needs a Flag

⚠️ **Command Execution** - Requires `--allow-execution` flag

## How to Use

### File Operations (No Flag Needed!)

```bash
# Just start Instinct8 normally
instinct8

# These all work immediately:
instinct8> review my files              # ✅ Reads files
instinct8> create a file called test.txt  # ✅ Creates files
instinct8> edit package.json            # ✅ Edits files
instinct8> read main.py                 # ✅ Reads files
```

### Command Execution (Needs Flag)

If you want Instinct8 to execute shell commands:

```bash
# Start with --allow-execution flag
instinct8 --allow-execution

# Now commands work:
instinct8> run npm install              # ✅ Executes commands
instinct8> execute git status           # ✅ Executes commands
```

## Verification

When you start Instinct8, you'll see:

```
✅ File operations enabled (read/write)
💡 Tip: Use --allow-execution to enable command execution
```

This confirms file operations are active!

## Examples

### Example 1: Read Files (No Flag)
```bash
$ instinct8
instinct8> review my files
```
✅ **Works immediately** - no flag needed!

### Example 2: Create Files (No Flag)
```bash
$ instinct8
instinct8> create a file called hello.txt with "Hello World"
```
✅ **Works immediately** - no flag needed!

### Example 3: Edit Files (No Flag)
```bash
$ instinct8
instinct8> add a comment to main.py
```
✅ **Works immediately** - no flag needed!

### Example 4: Execute Commands (Needs Flag)
```bash
$ instinct8 --allow-execution
instinct8> run npm install
```
⚠️ **Requires `--allow-execution` flag**

## Summary

| What You Want | Flag Needed? | How to Enable |
|---------------|--------------|---------------|
| Read files | ❌ No | Already enabled! |
| Write files | ❌ No | Already enabled! |
| Edit files | ❌ No | Already enabled! |
| Create files | ❌ No | Already enabled! |
| Execute commands | ✅ Yes | `instinct8 --allow-execution` |

## Troubleshooting

### "Files aren't being read/edited"

**Check:**
1. Are you asking clearly? Try: `review my files` or `create a file`
2. Check the working directory shown at startup
3. Make sure you have file permissions

### "I see '[Would execute: ...]' messages"

This means:
- ✅ File operations are working
- ⚠️ Command execution is disabled (normal for safety)

To enable command execution:
```bash
instinct8 --allow-execution
```

## Bottom Line

**File operations work out of the box!** Just run `instinct8` and start using it. Only command execution needs a flag.
