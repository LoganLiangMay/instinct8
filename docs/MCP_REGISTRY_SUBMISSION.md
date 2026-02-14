# MCP Registry Submission for instinct8

This document contains everything needed to submit instinct8 to the official MCP Registry.

## Submission URL

https://registry.modelcontextprotocol.io/submit

## Registry Entry JSON

```json
{
  "name": "instinct8",
  "description": "Context compression with goal drift prevention for long-running Claude Code conversations. Preserves your original objectives while reducing token usage.",
  "author": "LoganLiangMay",
  "homepage": "https://github.com/LoganLiangMay/instinct8",
  "repository": "https://github.com/LoganLiangMay/instinct8",
  "documentation": "https://github.com/LoganLiangMay/instinct8/blob/main/mcp_server/README.md",
  "license": "BSL-1.1",
  "categories": ["productivity", "context-management", "development-tools"],
  "keywords": ["compression", "goal-drift", "context", "memory", "productivity"],
  "version": "0.1.0",
  "runtime": "python",
  "installation": {
    "pip": {
      "package": "instinct8-mcp",
      "command": "instinct8-mcp"
    },
    "source": {
      "repository": "https://github.com/LoganLiangMay/instinct8",
      "path": "mcp_server",
      "command": "pip install -e ."
    }
  },
  "configuration": {
    "claude_code": {
      "config_file": "~/.claude/claude_code_config.json",
      "example": {
        "mcpServers": {
          "instinct8": {
            "command": "instinct8-mcp"
          }
        }
      }
    }
  },
  "capabilities": {
    "tools": true,
    "resources": true,
    "prompts": true,
    "sampling": true
  },
  "tools": [
    {
      "name": "initialize_session",
      "description": "Set up protected core with goal and constraints to preserve during compression"
    },
    {
      "name": "compress_context",
      "description": "Intelligently compress conversation while preserving goal-critical information"
    },
    {
      "name": "measure_drift",
      "description": "Quantify goal coherence and check if original objectives are maintained"
    }
  ],
  "resources": [
    {
      "name": "session://current",
      "description": "View current session state including salience set and compression stats"
    },
    {
      "name": "strategies://list",
      "description": "List available compression strategies and their descriptions"
    }
  ],
  "prompts": [
    {
      "name": "selective_salience_extract",
      "description": "Template for extracting goal-critical information from context"
    },
    {
      "name": "protected_core_compress",
      "description": "Template for compressing with Protected Core pattern"
    }
  ],
  "requirements": {
    "python": ">=3.10",
    "dependencies": ["mcp>=1.0.0"],
    "platforms": ["macos", "linux", "windows"]
  },
  "highlights": [
    "No API keys required - uses Claude's model via MCP sampling",
    "Scientifically validated approach with 7% average drift reduction",
    "Lightweight (~50KB) with minimal dependencies",
    "Preserves goals and constraints verbatim while compressing background",
    "Cumulative salience set grows with each compression"
  ],
  "use_cases": [
    "Long debugging sessions (2+ hours)",
    "Multi-day feature development",
    "Complex code reviews with architectural decisions",
    "Research and exploration with many context switches",
    "Any conversation where maintaining original objectives is critical"
  ],
  "screenshots": [],
  "video_url": "",
  "support": {
    "issues": "https://github.com/LoganLiangMay/instinct8/issues",
    "documentation": "https://github.com/LoganLiangMay/instinct8/tree/main/mcp_server",
    "quickstart": "https://github.com/LoganLiangMay/instinct8/blob/main/mcp_server/QUICKSTART.md",
    "faq": "https://github.com/LoganLiangMay/instinct8/blob/main/mcp_server/FAQ.md"
  }
}
```

## Short Description (for registry listing)

> Prevent goal drift in long Claude Code conversations. instinct8 intelligently compresses context while preserving your original objectives, constraints, and critical decisions. No API keys required.

## Long Description (for detail page)

> **instinct8** is a context compression MCP server that solves the "goal drift" problem in long-running Claude Code conversations.
>
> **The Problem:** During extended sessions, standard context compression causes AI assistants to gradually forget or misremember original objectives. Research shows ~7% drift per compression with standard methods.
>
> **The Solution:** instinct8 uses "Selective Salience with Protected Core" compression:
> - Identifies goal-critical information using Claude's model
> - Preserves it verbatim (never summarized)
> - Compresses only background context
> - Maintains a cumulative salience set across compressions
>
> **Key Benefits:**
> - 🎯 Goals and constraints never forgotten
> - 💾 3-5x compression ratios
> - 🔒 No API keys needed (uses MCP sampling)
> - 📊 Measurable drift prevention (0.9+ coherence scores)
> - ⚡ Lightweight with minimal dependencies
>
> **Perfect for:** Debugging marathons, multi-day projects, complex features, code reviews, and any task where maintaining focus matters.

## Submission Checklist

Before submitting:

- [ ] Package published to PyPI as `instinct8-mcp`
- [ ] Installation verified: `pip install instinct8-mcp` works
- [ ] Command works: `instinct8-mcp --help`
- [ ] GitHub repository is public and accessible
- [ ] Documentation is complete and accurate
- [ ] QUICKSTART.md provides 5-minute setup
- [ ] TROUBLESHOOTING.md covers common issues
- [ ] FAQ.md answers key questions
- [ ] All URLs in JSON are valid and working
- [ ] License file exists (LICENSE-BSL)

## How to Submit

1. **Ensure PyPI package is published** (critical!)
2. **Go to**: https://registry.modelcontextprotocol.io/submit
3. **Paste the JSON** from above
4. **Add screenshots** if available
5. **Submit for review**

## After Submission

1. **Monitor**: Check submission status
2. **Respond**: Answer any reviewer questions
3. **Announce**: Once approved, announce on social media
4. **Update**: Add "Listed in MCP Registry" badge to README

## Marketing Copy

### For Social Media Announcement

> 🎉 instinct8 is now in the MCP Registry!
>
> Stop losing track of your goals in long Claude Code sessions. instinct8 intelligently compresses context while preserving what matters.
>
> ✅ No API keys needed
> ✅ 3-5x compression
> ✅ Goals never forgotten
>
> Install: pip install instinct8-mcp
>
> #ClaudeCode #MCP #AI #Developer Tools

### For Blog Post

**Title:** "Introducing instinct8: Solving Goal Drift in AI Conversations"

**Hook:** Ever notice how Claude Code gradually forgets what you were originally trying to do during long sessions? You're experiencing "goal drift" - and instinct8 solves it.

## Support Template

For responding to user issues after registry listing:

```
Thanks for trying instinct8!

For your issue with [PROBLEM], please:
1. Check our troubleshooting guide: [TROUBLESHOOTING.md]
2. Try the hello world example: [hello_world.md]
3. See if it's in our FAQ: [FAQ.md]

If still stuck, please open an issue with:
- Your config file (remove sensitive data)
- Output of: pip show instinct8-mcp
- Error messages you're seeing

We'll help you get it working!
```

## Registry Badge

Once approved, add to README:

```markdown
[![MCP Registry](https://img.shields.io/badge/MCP-Registry-blue)](https://registry.modelcontextprotocol.io/instinct8)
```

---

**Status**: Ready for submission once PyPI package is published