# instinct8 MCP Server Examples

This directory contains practical examples of using the instinct8 MCP server with Claude Code for various scenarios.

## Available Examples

### 1. [Debugging Session](debugging_session.md)
Learn how to use instinct8 during extended debugging sessions to maintain focus on the original issue while investigating multiple system components.

**Key concepts:**
- Initializing with clear debugging goals
- Compressing investigation history
- Preserving critical findings
- Verifying alignment with original bug

### 2. [Feature Development](feature_development.md)
See how to use instinct8 across multiple days while building complex features, maintaining continuity and focus throughout the development cycle.

**Key concepts:**
- Multi-day session management
- Strategic compression points
- Preserving architectural decisions
- Daily drift checks

### 3. [Goal Drift Prevention](goal_drift_prevention.md)
Understand how to actively monitor and prevent goal drift, with real examples of drift detection and course correction.

**Key concepts:**
- Interpreting drift scores
- Proactive drift detection patterns
- Recovery from drift
- When drift might be acceptable

## Quick Start Guide

### Basic Pattern

1. **Initialize** with clear goals and constraints
2. **Work** on your task normally
3. **Compress** when context gets large
4. **Measure** drift periodically
5. **Adjust** if you've strayed from goals

### Example Commands

**Start a session:**
```
Initialize a session with goal "Fix memory leak in image processor"
and constraints "Don't break API", "Maintain performance benchmarks"
```

**Compress intelligently:**
```
Compress our discussion but preserve:
- Root cause analysis
- Proposed solutions
- Code changes made
```

**Check alignment:**
```
Measure drift to ensure we're still focused on the memory leak
```

## When to Use Each Pattern

| Scenario | Initialize | Compress | Measure Drift |
|----------|------------|----------|---------------|
| Bug fixing | Once at start | Every 1-2 hours | Before implementing fix |
| Feature development | Start of project | End of each component | Daily |
| Code review | Per file/module | After each major file | Before suggestions |
| Research/exploration | Per topic | When switching focus | Before conclusions |
| Refactoring | Per component | After analysis | Before changes |

## Best Practices

### DO:
- ✅ Set specific, measurable goals
- ✅ Include "what not to do" in constraints
- ✅ Compress before context becomes overwhelming
- ✅ Be explicit about what to preserve during compression
- ✅ Measure drift at natural checkpoints

### DON'T:
- ❌ Set vague goals like "improve code"
- ❌ Wait until context is huge to compress
- ❌ Ignore drift warnings
- ❌ Compress without preservation instructions
- ❌ Reinitialize unless goals genuinely changed

## Common Pitfalls and Solutions

### Pitfall 1: Over-Compression
**Problem:** Losing important details during compression
**Solution:** Be specific about what to preserve

### Pitfall 2: Under-Compression
**Problem:** Context becomes too large and unwieldy
**Solution:** Compress every 1-2 hours or at natural breakpoints

### Pitfall 3: Constraint Creep
**Problem:** Adding constraints during conversation without updating session
**Solution:** Either reinitialize or explicitly note new constraints for preservation

### Pitfall 4: Ignoring Drift
**Problem:** Continuing despite drift warnings
**Solution:** Take drift scores seriously and course-correct

## Advanced Techniques

### Layered Compression
For very long projects, compress in layers:
1. Detailed compression every 2 hours
2. Summary compression daily
3. Executive compression weekly

### Checkpoint Preservation
Before risky changes:
```
Compress current state as "checkpoint before database migration"
```

### Parallel Explorations
When exploring multiple solutions:
```
Compress as "Solution A: microservices approach"
[explore alternative]
Compress as "Solution B: monolithic approach"
```

## Integration with Other Tools

instinct8 works alongside other MCP servers:
- Use GitHub MCP to fetch code, then instinct8 to maintain focus during review
- Use web search MCP for research, then instinct8 to preserve key findings
- Combine with database MCP while optimizing queries with instinct8 goals

## Feedback and Contributions

Found a great use case? Have a pattern to share? Please contribute!
- Add new examples via PR
- Share your experiences in issues
- Suggest improvements to existing examples

## Quick Reference Card

```bash
# Initialize session
Goal: "Your specific objective"
Constraints: ["Limitation 1", "Don't do X", "Maintain Y"]

# Compress with preservation
Compress but keep: [critical info, decisions, current task]

# Check drift
Measure drift to verify alignment

# View state
Show current session resource

# List strategies
Show available compression strategies
```