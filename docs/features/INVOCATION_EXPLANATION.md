# Why Codex Uses npm run vs Instinct8 Direct Command

## The Difference Explained

### Codex (Your Setup)
```bash
npm run codex:prompt "prompt"
```

**Why npm run?**
- Codex uses `@openai/codex-sdk` (JavaScript SDK)
- Your `codex-prompt.js` is a **custom wrapper script**
- The wrapper provides:
  - Custom formatting/output
  - Error handling
  - Environment variable loading (.env)
  - Project-specific configuration
- npm script is just a shortcut: `npm run codex:prompt` → `node codex-prompt.js`

**Under the hood:**
- Codex SDK wraps the actual `codex` binary
- The SDK spawns the Codex CLI and communicates via JSONL
- Your wrapper adds custom formatting on top

### Instinct8 (Current)
```bash
instinct8 "prompt"
```

**Why direct command?**
- Instinct8 is a **standalone Python CLI tool**
- Installed globally via `pipx install instinct8-agent`
- No wrapper needed - it's a complete tool
- Works anywhere Python works

**Under the hood:**
- Direct Python command-line tool
- No SDK/wrapper needed
- Simpler architecture

## The Real Codex CLI

Actually, Codex **also** has a direct CLI command:
```bash
codex exec "prompt"  # Direct Codex CLI
```

But you're using the **Codex SDK** via a wrapper, which is why you use `npm run`.

## Why Use npm Wrapper?

**Advantages:**
- ✅ Custom formatting (your pretty output)
- ✅ Project-specific config
- ✅ Easy to customize per-project
- ✅ Consistent with Node.js project workflow

**Disadvantages:**
- ❌ Requires Node.js/npm
- ❌ Project-specific (not global)
- ❌ Extra layer of abstraction

## Solution: Both Options!

I've created `instinct8-prompt.js` so you can use Instinct8 the same way:

```bash
# Direct CLI (works everywhere)
instinct8 "prompt"

# npm wrapper (consistent with Codex)
npm run instinct8:prompt "prompt"
```

Both work! The npm wrapper is just for consistency with your Codex setup.
