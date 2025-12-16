# Codex vs Instinct8: Invocation Methods

## The Difference

### Codex (Your Setup)
- **Uses**: Node.js wrapper script (`codex-prompt.js`)
- **Invoked via**: `npm run codex:prompt "prompt"`
- **How it works**: 
  - Uses `@openai/codex-sdk` (JavaScript SDK)
  - Wraps Codex API calls in a Node.js script
  - Provides custom formatting and error handling
  - Requires Node.js and npm

### Instinct8 (Current)
- **Uses**: Direct Python CLI command
- **Invoked via**: `instinct8 "prompt"`
- **How it works**:
  - Standalone Python package installed via pip/pipx
  - Direct command-line tool
  - No wrapper needed
  - Works anywhere Python works

## Why the Difference?

### Codex SDK Approach
- **Pros**: 
  - Easy to customize (JavaScript wrapper)
  - Project-specific configuration
  - Can add custom formatting/logging
  - Works well in Node.js projects
  
- **Cons**:
  - Requires Node.js/npm
  - Need to maintain wrapper script
  - Not globally available (project-specific)

### Instinct8 Direct CLI Approach
- **Pros**:
  - Globally available (installed via pipx)
  - No wrapper needed
  - Works in any project/language
  - Simpler for users
  
- **Cons**:
  - Less customizable per-project
  - Can't easily add project-specific logic

## Options

### Option 1: Keep Instinct8 as Direct CLI (Current)
- ✅ Simple: `instinct8 "prompt"`
- ✅ Works everywhere
- ✅ No dependencies

### Option 2: Create npm Wrapper (Like Codex)
- Create `instinct8-prompt.js` wrapper
- Add to `package.json`: `"instinct8": "node instinct8-prompt.js"`
- Use: `npm run instinct8 "prompt"`
- **Pros**: Consistent with Codex, customizable
- **Cons**: Requires Node.js, more setup

### Option 3: Both (Recommended)
- Keep direct CLI: `instinct8 "prompt"` (works everywhere)
- Add npm wrapper: `npm run instinct8 "prompt"` (for Node.js projects)
- Best of both worlds!

## Recommendation

**Keep both!** Instinct8 works as a direct CLI (simpler), but we can also create an npm wrapper script for consistency with your Codex setup.

Would you like me to create an `instinct8-prompt.js` wrapper that works like your `codex-prompt.js`?
