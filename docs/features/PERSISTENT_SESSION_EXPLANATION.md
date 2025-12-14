# Why Instinct8 Now Works Like Claude Code

## The Problem

**Before:**
- `instinct8 "prompt"` → executes → exits (one-shot)
- Had to re-initialize every time
- Lost context between runs
- No persistent session

**Claude Code:**
- `claude` → starts session → stays running
- Maintains context across interactions
- Shows project info, git branch
- Waits for user input continuously

## The Solution

Now Instinct8 works both ways:

### 1. Persistent Session (Default - Like Claude Code)
```bash
instinct8                    # Starts session, stays running
instinct8> create a file     # Type prompt, press Enter
instinct8> add a function    # Context maintained!
instinct8> stats             # Check context usage
instinct8> quit              # Exit when done
```

**Features:**
- ✅ Stays running (like Claude Code)
- ✅ Maintains context across prompts
- ✅ Shows project info (name, git branch, directory)
- ✅ Built-in commands (`help`, `stats`, `salience`, etc.)
- ✅ Welcome screen with tips

### 2. One-Shot Mode (Still Available)
```bash
instinct8 "create a file"    # Executes and exits (like Codex exec)
```

## How It Works

### Persistent Session Flow

1. **Start**: `instinct8` (no args)
2. **Initialize**: Creates agent, shows welcome
3. **Loop**: Waits for input → executes → waits again
4. **Context**: Agent maintains conversation history
5. **Exit**: User types `quit` or Ctrl+C

### Context Retention

- Agent instance stays alive
- Conversation history preserved
- Compression happens automatically when threshold exceeded
- Salience set grows across interactions

## Comparison

| Feature | Claude Code | Instinct8 (Before) | Instinct8 (Now) |
|---------|-------------|-------------------|-----------------|
| Persistent session | ✅ | ❌ | ✅ |
| Context retention | ✅ | ❌ | ✅ |
| Project awareness | ✅ | ❌ | ✅ |
| One-shot mode | ❌ | ✅ | ✅ |
| Interactive commands | ✅ | Limited | ✅ |

## Why This Matters

**Benefits:**
- ✅ **Faster workflow**: No re-initialization overhead
- ✅ **Better context**: Maintains conversation history
- ✅ **More natural**: Like talking to an assistant
- ✅ **Project awareness**: Knows what you're working on

**Use Cases:**
- Long coding sessions with multiple related tasks
- Iterative development (fix → test → improve)
- Multi-file projects (context across files)
- Complex tasks requiring multiple steps

## Migration

**Old way (still works):**
```bash
instinct8 "prompt"           # One-shot execution
```

**New way (recommended):**
```bash
instinct8                   # Start session
instinct8> prompt            # Type prompts directly
instinct8> another task      # Context maintained!
```

Both work! Use persistent mode for longer sessions, one-shot for quick tasks.
