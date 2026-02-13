# Example: Measuring and Preventing Goal Drift

This example demonstrates how to actively monitor and prevent goal drift during long conversations.

## What is Goal Drift?

Goal drift occurs when an AI assistant gradually loses track of the original objectives during a long conversation, especially after context compression. You might start debugging a specific bug but end up refactoring unrelated code.

## Scenario: Refactoring Gone Wrong

You're tasked with optimizing database queries, but the conversation risks drifting into unnecessary architectural changes.

## Step 1: Set Clear Boundaries

**You say:**
```
I need to optimize slow database queries in our reporting module.
Initialize a session with:

Goal: "Optimize database queries in reporting module to reduce page load time under 2 seconds"
Constraints:
- "No schema changes allowed"
- "Must maintain existing API contracts"
- "Cannot break existing reports"
- "Changes must be backward compatible"
- "Focus only on query optimization, not refactoring"
```

## Step 2: Work Progresses

**After analyzing queries and discussing optimizations:**
```
I notice the code structure here is pretty messy. Maybe we should refactor
the entire ReportGenerator class while we're at it...

Actually, wait. Let's measure drift first to check if refactoring aligns
with our goals. Use the measure_drift tool.
```

**Claude measures drift and responds:**
```
Goal Coherence: 0.6
Constraint Recall: 0.8
Behavior Alignment: 3/5

We're starting to drift. Refactoring the ReportGenerator class wasn't part
of the original goal. We should focus on query optimization only.
```

## Step 3: Course Correction

**You respond:**
```
Good catch. Let's get back to query optimization. What specific queries
have we identified as slow?
```

## Example: Proactive Drift Detection

### Scenario: Feature Creep

**Original request:**
```
Initialize session:
Goal: "Add user avatar upload feature"
Constraints:
- "Max file size 5MB"
- "Only JPEG and PNG"
- "Store in existing S3 bucket"
```

**After some discussion:**
```
We've added avatar upload. Should we also add:
- Image cropping?
- Filters and effects?
- Avatar history?
- Social media import?

Let me measure drift before we continue...
```

**Claude measures and warns:**
```
Goal Coherence: 0.5 - Significant drift detected!
We've moved beyond "add user avatar upload" into building a full image
editing suite. The original goal was just upload functionality.
```

## Systematic Drift Prevention

### Pattern 1: Regular Checkpoints

```
Every 30 minutes of discussion, I'll use measure_drift to ensure we're on track.
```

### Pattern 2: Before Major Decisions

```
Before we add this new feature, let's measure drift to ensure it aligns
with our original objectives.
```

### Pattern 3: After Compression

```
We just compressed the context. Let's measure drift to ensure the compression
didn't lose sight of our goals.
```

## Interpreting Drift Scores

### Goal Coherence (0.0 - 1.0)
- **1.0**: Perfect alignment with original goal
- **0.8+**: On track, minor variations acceptable
- **0.6-0.7**: Some drift, needs attention
- **<0.6**: Significant drift, course correction needed

### Constraint Recall (0.0 - 1.0)
- **1.0**: All constraints being followed
- **0.8+**: Most constraints maintained
- **0.6-0.7**: Some constraints being ignored
- **<0.6**: Major constraint violations

### Behavior Alignment (1-5 scale)
- **5**: Perfectly focused on original task
- **4**: Mostly aligned with minor diversions
- **3**: Mixed focus, some unrelated work
- **2**: Significant unrelated activities
- **1**: Completely off track

## Real-World Example: API Redesign Drift

### Initial Goal
```
Initialize session:
Goal: "Add pagination to GET /users endpoint"
Constraints: ["Maintain backward compatibility", "Use cursor-based pagination"]
```

### Conversation Evolves
```
You: Let's add pagination to /users
Claude: [implements pagination]
You: Should we also paginate /posts?
Claude: [implements for /posts]
You: Maybe we should standardize all list endpoints?
Claude: [starts designing new API structure]
You: We could version the entire API...
```

### Drift Detection
```
You: Wait, measure drift before we continue.

Claude:
Goal Coherence: 0.3 - Severe drift!
Original: "Add pagination to GET /users endpoint"
Current: "Redesigning entire API structure"

Constraint Recall: 0.5
Lost track of "Maintain backward compatibility" while designing new API version.
```

### Recovery
```
You: Let's refocus. We only need pagination for /users endpoint.
Compress our discussion but only keep the /users pagination implementation.
```

## Tips for Preventing Drift

1. **Specific Goals**: "Add pagination to /users" vs "Improve API"
2. **Clear Constraints**: Explicitly state what NOT to do
3. **Regular Measurement**: Check drift every 30-60 minutes
4. **Question Scope Creep**: "Does this align with our original goal?"
5. **Compress Strategically**: Remove off-topic discussions during compression

## When Drift Might Be Acceptable

Sometimes you discover the goal should change:

```
You: We're drifting from query optimization into schema redesign,
but I realize the schema is the root cause. Let's reinitialize:

New Goal: "Redesign reporting schema for better query performance"
New Constraints: ["Migration plan required", "Zero downtime deployment"]
```

## Conclusion

Goal drift is natural in long conversations, but instinct8 helps you:
1. Detect drift before it becomes problematic
2. Maintain focus on original objectives
3. Preserve constraints throughout the conversation
4. Make conscious decisions about when to change goals

Use `measure_drift` proactively, not just reactively!