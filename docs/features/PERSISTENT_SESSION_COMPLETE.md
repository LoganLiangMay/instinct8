# Persistent Session Mode - Complete! 🎉

## What Changed

Instinct8 now works **exactly like Claude Code** - a persistent interactive session!

## Before vs After

### Before (One-Shot)
```bash
instinct8 "create a file"     # Executes → exits
instinct8 "add a function"   # Re-initializes → executes → exits
# Lost context between runs ❌
```

### After (Persistent Session)
```bash
instinct8                     # Starts session → stays running
instinct8> create a file      # Executes → waits for next input
instinct8> add a function     # Context maintained! ✅
instinct8> stats              # Check usage
instinct8> quit               # Exit when done
```

## Features

### ✅ Persistent Session
- Stays running (like Claude Code)
- Waits for user input continuously
- No re-initialization needed

### ✅ Context Retention
- Maintains conversation history
- Agent instance stays alive
- Compression happens automatically
- Salience set grows across interactions

### ✅ Project Awareness
- Shows project name
- Detects git branch
- Shows working directory
- Context-aware responses

### ✅ Built-in Commands
- `help` - Show commands
- `stats` - Show context usage
- `salience` - Show preserved salience set
- `compress` - Manually trigger compression
- `reset` - Reset agent state
- `quit` - Exit session

## Usage

### Start Persistent Session
```bash
# Basic
instinct8

# With goal
instinct8 --goal "Build FastAPI app"

# With constraints
instinct8 --goal "Build app" --constraints "Use JWT" "Hash passwords"
```

### In Session
```
instinct8> create a login endpoint
instinct8> add error handling
instinct8> write tests
instinct8> stats
instinct8> quit
```

### One-Shot Mode (Still Works)
```bash
instinct8 "create a file"    # Executes and exits
```

## How It Works

1. **Start**: `instinct8` (no args) → starts session
2. **Initialize**: Creates agent, shows welcome, detects project
3. **Loop**: 
   - Waits for input (`instinct8>` prompt)
   - Executes prompt
   - Maintains context
   - Waits again
4. **Exit**: User types `quit` or Ctrl+C

## Comparison with Claude Code

| Feature | Claude Code | Instinct8 |
|---------|-------------|-----------|
| Persistent session | ✅ | ✅ |
| Context retention | ✅ | ✅ |
| Project awareness | ✅ | ✅ |
| Git branch detection | ✅ | ✅ |
| Interactive commands | ✅ | ✅ |
| Welcome screen | ✅ | ✅ |

## Benefits

- ✅ **Faster**: No initialization overhead
- ✅ **Smarter**: Maintains context
- ✅ **Natural**: Like talking to an assistant
- ✅ **Efficient**: Better for multi-step tasks

## Version

Implemented in **v0.3.0**
