# CLI Fix Summary

## Issues Fixed

### 1. `instinct8-agent` - Now accepts direct questions

**Before:**
```bash
instinct8-agent "what can you do"
# Error: invalid choice: 'what can you do'
```

**After:**
```bash
instinct8-agent "what can you do"
# ✅ Works! Enters quick question mode
```

**Changes:**
- Added check before argparse to detect if first arg is a mode (`interactive`/`test`) or a question
- If it's a question, bypass argparse and handle directly
- Creates agent and answers question immediately

### 2. `instinct8` - Now handles multi-word prompts

**Before:**
```bash
instinct8 help me create a song
# Error: unrecognized arguments: me create a song
```

**After:**
```bash
instinct8 help me create a song
# ✅ Works! Treats entire phrase as prompt
```

**Changes:**
- Changed `prompt` argument from `nargs='?'` to `nargs='*'`
- Join all words into single prompt string
- Handles multi-word prompts correctly

## Usage Examples

### instinct8-agent

```bash
# Quick question (new!)
instinct8-agent "what can you do?"
instinct8-agent "help me build an app"

# Interactive mode (existing)
instinct8-agent interactive --goal "Build app"

# Test mode (existing)
instinct8-agent test --goal "Research" --questions "Q1" "Q2"
```

### instinct8

```bash
# Multi-word prompts (fixed!)
instinct8 help me create a song
instinct8 create a FastAPI endpoint with authentication
instinct8 "help me create a song"  # Also works with quotes

# With options
instinct8 --goal "Music app" help me create a song
```

## Version

Fixed in version **0.1.2**
