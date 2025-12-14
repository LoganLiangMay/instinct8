# Bug Fix v0.2.1 - UnboundLocalError Fix

## Problem

When running `instinct8-agent "What can you do?"`, the code crashed with:

```
UnboundLocalError: cannot access local variable 'args' where it is not associated with a value
```

## Root Cause

The `main()` function had two code paths:
1. **Mode-based path**: When first arg is `interactive`/`test`, creates `args` via `parser.parse_args()`
2. **Quick question path**: When first arg is a question, goes into `else` branch

The problem was that code after line 159 (checking `args.config`, `args.goal`, etc.) was **outside** the `if` block, so it executed regardless of which path was taken. But `args` was only defined inside the `if` block.

## Fix

Restructured the code so:
1. **Mode-based path**: Handles everything itself (API key check, config loading, mode execution) and returns
2. **Quick question path**: Handles everything itself (API key check, agent creation, question answering) and returns

Now `args` is only accessed in the branch where it's defined.

## Changes

- Moved API key check and config loading **inside** the `if` block for mode-based usage
- Quick question path handles its own API key check
- Both paths are now independent and don't share variable scope

## Testing

✅ Verified that `instinct8-agent "What can you do?"` no longer crashes with UnboundLocalError
✅ Mode-based usage (`instinct8-agent interactive`) still works
✅ Both paths are now properly isolated

## Version

Fixed in **v0.2.1**
