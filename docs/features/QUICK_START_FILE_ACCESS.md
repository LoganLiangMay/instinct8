# Quick Start: File Access in Instinct8

## TL;DR

**File operations are ALREADY ENABLED!** Just run `instinct8` and start using it.

## What Works Without Flags

✅ Read files  
✅ Write files  
✅ Edit files  
✅ Create files  

## What Needs a Flag

⚠️ Execute shell commands → Use `instinct8 --allow-execution`

## Try It Now

```bash
# 1. Start Instinct8 (no flags needed!)
instinct8

# 2. Try reading files
instinct8> review my files

# 3. Try creating a file
instinct8> create a file called test.txt with "Hello World"

# 4. Try editing a file
instinct8> add a comment to package.json
```

**All of these work immediately - no configuration needed!**

## Enable Command Execution (Optional)

If you want Instinct8 to run shell commands:

```bash
# Start with execution enabled
instinct8 --allow-execution

# Now commands work
instinct8> run npm install
instinct8> execute git status
```

## Status Check

When you start Instinct8, look for this message:

```
✅ File operations enabled (read/write)
```

If you see this, file operations are working!

## Common Commands

```bash
# Read files
instinct8> review my files
instinct8> look at package.json
instinct8> show me the structure

# Create files
instinct8> create a file called hello.txt
instinct8> write a Python script

# Edit files
instinct8> add a function to main.py
instinct8> update package.json
```

**All work without any flags!**
