# Example: Multi-Day Feature Development

This example demonstrates using instinct8 across multiple Claude Code sessions while building a complex feature.

## Scenario

You're building a notification system that needs to support multiple channels (email, SMS, push) with templating, scheduling, and analytics.

## Day 1: Architecture Planning

### Morning: Initialize and Design

**You say:**
```
I'm starting a new notification system feature. Use initialize_session with:

Goal: "Build a multi-channel notification system with email, SMS, and push support"
Constraints:
- "Must handle 10K notifications per minute"
- "Support template variables and i18n"
- "Provide delivery status tracking"
- "Use existing message queue infrastructure"
- "GDPR compliant with data retention policies"
```

**Continue with architecture discussion:**
```
Let's design the system architecture. I'm thinking:
- Notification service as the orchestrator
- Channel-specific adapters for email/SMS/push
- Template engine with variable substitution
- Analytics service for tracking

What's your recommendation for the data model?
```

### Afternoon: First Compression

**After extensive design discussion:**
```
We've made good progress on the architecture. Compress our context but ensure you preserve:
- The agreed-upon service architecture
- The data model for notifications
- The template schema design
- The API endpoints we've defined
```

## Day 2: Implementation

### Morning: Resume and Build

**You start a new session:**
```
Yesterday we designed a notification system. Let me check where we left off.
[Claude has the compressed context from yesterday]

Let's start implementing the NotificationService class...
```

### Afternoon: API Development

**After implementing core services:**
```
Good progress on the services. Now let's build the REST API.
But first, compress our morning's work focusing on:
- Completed service implementations
- Remaining tasks
- Any issues or decisions we need to revisit
```

## Day 3: Testing and Refinement

### Morning: Drift Check

**Start the day with:**
```
Before we continue, use measure_drift to check if we're still aligned with our
original notification system goals. Have we maintained focus on multi-channel
support and the performance requirements?
```

**Claude confirms alignment or highlights any drift.**

### Continue Development

**Based on drift measurement:**
```
Good, we're on track. Today let's focus on:
1. SMS provider integration
2. Template variable validation
3. Rate limiting implementation
```

### End of Day: Final Compression

```
We're nearly done. Compress everything but keep:
- All API documentation
- Integration test scenarios
- Deployment configuration
- Performance optimization notes
- Remaining TODO items
```

## Day 4: Deployment Preparation

### Morning: Final Review

```
Let's review what we've built against our original requirements.
Show me the current session state to see our protected core.
```

**Claude shows the preserved goals and constraints.**

### Deployment Checklist

```
Based on our constraints, let's create a deployment checklist...
```

## Benefits Across Multiple Days

1. **Continuity**: Each day builds on previous work without losing context
2. **Focus**: Original goals and constraints never lost despite multiple compressions
3. **Efficiency**: Conversations stay manageable even after days of work
4. **Traceability**: Can always check alignment with original requirements

## Compression Strategy Tips

### What to Always Preserve:
- Architectural decisions
- API contracts
- Data models
- Unresolved issues
- Performance requirements

### What Can Be Compressed:
- Detailed implementation discussions
- Resolved debugging sessions
- Exploratory code that was rejected
- Verbose error messages after fixing

### When to Compress:
- At natural breakpoints (end of design phase, after major implementation)
- When context feels too large
- Before starting a new major component
- At the end of each day for multi-day projects

## Using Resources

**Check session state:**
```
Show me the current session resource to see what's in our salience set.
```

**Review available strategies:**
```
What compression strategies are available? Show me the strategies list.
```

## Key Patterns for Long Projects

1. **Initialize Once**: Set comprehensive goals/constraints at the start
2. **Compress Regularly**: Don't wait until context is overwhelming
3. **Be Specific**: Tell the tool what to preserve during compression
4. **Measure Drift**: Periodically check alignment, especially after major decisions
5. **Document Decisions**: Ensure architectural decisions enter the salience set