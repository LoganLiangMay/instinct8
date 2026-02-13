# Claude Code Integration Guide

This guide explains how to use instinct8's context compression with Claude Code through the Model Context Protocol (MCP) server.

## Table of Contents
- [What is instinct8 MCP Server?](#what-is-instinct8-mcp-server)
- [Installation](#installation)
- [Configuration](#configuration)
- [Using instinct8 in Claude Code](#using-instinct8-in-claude-code)
- [Common Use Cases](#common-use-cases)
- [Troubleshooting](#troubleshooting)
- [Technical Details](#technical-details)

## What is instinct8 MCP Server?

The instinct8 MCP server provides intelligent context compression for Claude Code conversations, preventing "goal drift" - the phenomenon where AI assistants gradually forget or misremember their original objectives during long conversations.

### Key Benefits

- **No API Keys Required**: Uses Claude's own model via MCP sampling
- **Lightweight**: ~50KB install, no heavy ML dependencies
- **Privacy-Focused**: All processing stays local on your machine
- **Scientifically Validated**: 7% average drift reduction per compression

## Installation

### Step 1: Install the MCP Server

```bash
pip install instinct8-mcp
```

Or install from source:
```bash
git clone https://github.com/jjjorgenson/instinct8.git
cd instinct8/mcp_server
pip install -e .
```

### Step 2: Verify Installation

```bash
# Check that the command is available
which instinct8-mcp

# Test that it runs
instinct8-mcp --help
```

## Configuration

### Step 1: Locate Claude Code Config

Find your Claude Code configuration file:
- **macOS/Linux**: `~/.claude/claude_code_config.json`
- **Windows**: `%USERPROFILE%\.claude\claude_code_config.json`

### Step 2: Add instinct8 to MCP Servers

Edit the configuration file and add instinct8 to the `mcpServers` section:

```json
{
  "mcpServers": {
    "instinct8": {
      "command": "instinct8-mcp"
    }
  }
}
```

If you have other MCP servers already configured:

```json
{
  "mcpServers": {
    "github": {
      "command": "github-mcp"
    },
    "instinct8": {
      "command": "instinct8-mcp"
    }
  }
}
```

### Step 3: Restart Claude Code

Close and reopen Claude Code for the changes to take effect.

### Step 4: Verify Connection

In Claude Code, you should now have access to instinct8 tools. You can verify by asking:
"What MCP tools do I have available?"

## Using instinct8 in Claude Code

### Available Tools

instinct8 provides three main tools:

#### 1. `initialize_session`
Sets up a protected core with your goal and constraints.

**Example:**
```
Use the initialize_session tool to set our goal as "Build a REST API for user management"
with constraints "Use FastAPI", "Include authentication", "PostgreSQL database"
```

#### 2. `compress_context`
Compresses the conversation while preserving goal-critical information.

**Example:**
```
Our conversation is getting long. Use the compress_context tool to reduce it while
keeping our goals and important decisions intact.
```

#### 3. `measure_drift`
Quantifies how well the current context maintains the original goals.

**Example:**
```
Use the measure_drift tool to check if we're still aligned with our original objectives.
```

### Available Resources

You can also query the current session state:

- `session://current` - Shows current salience set, compression stats, and tokens saved
- `strategies://list` - Lists available compression strategies

## Common Use Cases

### Use Case 1: Long Debugging Session

When debugging complex issues across multiple files:

1. **Start Session**:
   ```
   Initialize a session with goal "Fix authentication bug in production"
   and constraints "Don't break existing tests", "Maintain backwards compatibility"
   ```

2. **Work Through Issues**:
   Continue your debugging conversation normally.

3. **Compress When Needed**:
   ```
   We've covered a lot of ground. Compress our context to focus on the key findings
   and remaining issues.
   ```

4. **Verify Alignment**:
   ```
   Check if we're still focused on the authentication bug or if we've drifted.
   ```

### Use Case 2: Feature Development

When building a new feature over multiple sessions:

1. **Define Requirements**:
   ```
   Initialize session: Build a notification system with email, SMS, and push notifications.
   Must be scalable and support templates.
   ```

2. **Develop Iteratively**:
   Work through implementation details, design decisions, code reviews.

3. **Periodic Compression**:
   ```
   Compress our discussion but preserve all architectural decisions and API designs.
   ```

### Use Case 3: Code Review and Refactoring

When reviewing and refactoring large codebases:

1. **Set Refactoring Goals**:
   ```
   Initialize: Refactor payment processing module for better testability.
   Constraints: No changes to external API, maintain audit trail.
   ```

2. **Review and Plan**:
   Discuss code issues, identify patterns, plan refactoring approach.

3. **Maintain Focus**:
   ```
   Compress context focusing on identified issues and refactoring strategy.
   ```

## Troubleshooting

### instinct8 tools not appearing in Claude Code

1. **Check Installation**:
   ```bash
   pip list | grep instinct8-mcp
   ```

2. **Verify Config Path**:
   ```bash
   cat ~/.claude/claude_code_config.json
   ```

3. **Check Command Availability**:
   ```bash
   which instinct8-mcp
   ```

4. **Restart Claude Code**:
   Fully quit and restart the application.

### "Command not found" error

If Claude Code can't find `instinct8-mcp`:

1. **Check Python Path**:
   ```bash
   python3 -m site --user-base
   ```

2. **Add to PATH** (if needed):
   ```bash
   export PATH="$PATH:$(python3 -m site --user-base)/bin"
   ```

3. **Use Full Path** in config:
   ```json
   {
     "mcpServers": {
       "instinct8": {
         "command": "/Users/username/.local/bin/instinct8-mcp"
       }
     }
   }
   ```

### Compression not preserving important information

1. **Re-initialize** with more specific goals and constraints
2. **Use explicit preservation**:
   ```
   Compress but specifically preserve the database schema decisions and API endpoints
   ```

### High sampling call count

The `compress_context` tool makes 2 sampling calls and `measure_drift` makes 1-3. This is normal and uses Claude's model efficiently.

## Technical Details

### How MCP Sampling Works

instinct8 uses MCP sampling, which means:
1. The server constructs compression prompts
2. Claude Code's model executes these prompts
3. Results are processed locally
4. No external API calls or data transmission

### Compression Strategy

instinct8 uses "Selective Salience with Protected Core":
1. **Extraction Phase**: Identifies goal-critical information
2. **Protection Phase**: Preserves critical info verbatim
3. **Compression Phase**: Summarizes only background context
4. **Deduplication**: Removes semantic duplicates

### Performance Characteristics

- **Compression Ratio**: Typically 3:1 to 5:1
- **Goal Drift Reduction**: 7% average per compression
- **Processing Time**: 2-5 seconds depending on context size
- **Memory Usage**: Minimal (~10MB for typical sessions)

### Data Privacy

- All processing happens locally on your machine
- No data is sent to external servers
- No API keys are stored or transmitted
- Session data is kept in memory only (not persisted)

## Advanced Usage

### Custom Compression Strategies

While the current version uses the default Selective Salience strategy, future versions will support:
- Strategy selection
- Custom compression thresholds
- Adjustable protection levels

### Integration with Other MCP Servers

instinct8 works alongside other MCP servers. You can combine it with:
- GitHub MCP for code repository access
- Perplexity MCP for web search
- Custom MCP servers for your specific needs

## Getting Help

- **GitHub Issues**: https://github.com/jjjorgenson/instinct8/issues
- **Documentation**: [Main README](../README.md) | [MCP Server README](../mcp_server/README.md)
- **Examples**: See [Common Use Cases](#common-use-cases) above

## Contributing

We welcome contributions! Areas where you can help:
- Testing with different Claude Code configurations
- Adding new compression strategies
- Improving documentation
- Reporting bugs and suggesting features

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.