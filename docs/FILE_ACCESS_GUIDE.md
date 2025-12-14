# File Access Guide for Instinct8

## Current Status

**Good news!** Instinct8 **already has access** to read and write files in your working directory by default. You don't need to do anything special!

## What's Already Enabled

### ✅ File Reading (Always Enabled)
Instinct8 can read files when you ask:
- `review my files`
- `look at package.json`
- `read the website files`
- `show me the structure`

### ✅ File Writing (Always Enabled)
Instinct8 can create and edit files:
- `create a file called note.txt`
- `write a Python script`
- `add a function to main.py`

### ⚠️ Command Execution (Requires Flag)
Shell commands require the `--allow-execution` flag:
- `run npm install`
- `execute git status`
- `run tests`

## How to Use

### Basic File Operations (No Flags Needed)

```bash
# Start Instinct8
instinct8

# Read files
instinct8> review my files
instinct8> look at package.json
instinct8> show me the structure

# Create/edit files
instinct8> create a file called hello.txt with "Hello World"
instinct8> write a Python script that prints hello
instinct8> add a function to main.py
```

### Enable Command Execution

If you want Instinct8 to execute shell commands:

```bash
# Start with execution enabled
instinct8 --allow-execution

# Or in one-shot mode
instinct8 --allow-execution "run npm install"
```

**⚠️ Warning**: Only enable execution if you trust the agent. Commands can modify your system!

## Working Directory

Instinct8 uses the directory where you run it as its working directory:

```bash
cd /Users/isaac/Documents/Instinct8/i8-website
instinct8  # Working directory: /Users/isaac/Documents/Instinct8/i8-website
```

All file operations happen relative to this directory.

## File Permissions

Instinct8 uses the same permissions as your user account. If you can read/write files, Instinct8 can too.

### Common Issues

**"Permission denied" errors:**
- Check file permissions: `ls -l filename`
- Make sure you own the file or have write access
- Try running Instinct8 from a directory you own

**"File not found" errors:**
- Make sure you're in the right directory
- Use absolute paths if needed: `/full/path/to/file.txt`
- Check the working directory shown at startup

## Examples

### Example 1: Review Files
```bash
instinct8
instinct8> review my files and tell me the structure
```
✅ **Works immediately** - no flags needed!

### Example 2: Create Files
```bash
instinct8
instinct8> create a text file called note.txt with "Hello from Instinct8"
```
✅ **Works immediately** - file will be created!

### Example 3: Edit Files
```bash
instinct8
instinct8> add a comment to the top of main.py saying "Created by Instinct8"
```
✅ **Works immediately** - file will be edited!

### Example 4: Execute Commands
```bash
instinct8 --allow-execution
instinct8> run npm install
```
⚠️ **Requires `--allow-execution` flag**

## Troubleshooting

### Files Not Being Read

**Problem**: Agent says "I can't read files" or shows "[Would execute: ls]"

**Solution**: 
- Make sure you're asking to "review", "look at", or "read" files
- Check the working directory shown at startup
- Try: `instinct8> review all files`

### Files Not Being Created

**Problem**: Agent says it created a file but it's not there

**Solution**:
- Check the working directory (shown at startup)
- Look for the file in that directory
- Check file permissions: `ls -l`

### Permission Errors

**Problem**: "Permission denied" when creating/editing files

**Solution**:
- Make sure you're in a directory you own
- Check file permissions: `ls -l`
- Try: `chmod 755 directory_name`

## Security Considerations

### File Operations (Safe)
- ✅ Reading files: Safe, read-only
- ✅ Creating new files: Safe, creates in your directory
- ✅ Editing files: Safe, modifies files you own

### Command Execution (Use Caution)
- ⚠️ Shell commands: Can modify your system
- ⚠️ Only enable if you trust the agent
- ⚠️ Review commands before executing

## Summary

| Operation | Enabled By Default? | Flag Needed? |
|-----------|-------------------|--------------|
| Read files | ✅ Yes | No |
| Write files | ✅ Yes | No |
| Create files | ✅ Yes | No |
| Edit files | ✅ Yes | No |
| Execute commands | ❌ No | `--allow-execution` |

**Bottom line**: File operations work out of the box! Only command execution requires a flag.
