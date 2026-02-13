# Example: Long Debugging Session

This example shows how to use instinct8 during an extended debugging session to maintain focus on the original issue.

## Scenario

You're debugging a complex authentication issue in a production system that involves multiple components: frontend, API gateway, auth service, and database.

## Step 1: Initialize the Session

**You say:**
```
I need to debug an authentication issue where users are randomly getting logged out.
Use the initialize_session tool to set up our debugging session.

Goal: "Fix random user logout bug in production authentication system"
Constraints:
- "Don't modify database schema"
- "Maintain backwards compatibility with v1 API"
- "Keep audit trail intact"
- "Fix must be deployable without downtime"
```

**Claude responds using the tool and confirms the session is initialized.**

## Step 2: Investigation Phase

**You continue your debugging conversation:**
```
Let's start by checking the auth service logs. I'm seeing these errors...
[paste logs]

Now let's look at the session storage implementation...
[discuss code]

Check the token refresh logic...
[more investigation]
```

## Step 3: Compress When Context Gets Long

**After extensive investigation, you say:**
```
We've covered a lot of ground investigating different parts of the system.
Use the compress_context tool to reduce our conversation while keeping:
- The symptoms we've identified
- The components we've ruled out
- The suspicious areas we need to investigate further
- Any code snippets that showed potential issues
```

**Claude compresses the context, preserving critical debugging information.**

## Step 4: Continue Investigation

**With compressed context, you continue:**
```
Based on what we've found, let's focus on the token refresh race condition
in the API gateway. Can you show me how we could add proper locking?
```

## Step 5: Verify We Haven't Drifted

**Before implementing the fix:**
```
Use the measure_drift tool to verify we're still focused on fixing the random
logout bug and haven't drifted into general refactoring.
```

**Claude measures drift and confirms alignment with original goal.**

## Step 6: Implement and Test Fix

**You proceed with the solution:**
```
Great, we're still on track. Let's implement the mutex lock for token refresh...
```

## Benefits Demonstrated

1. **Maintained Focus**: Despite investigating multiple components, stayed focused on the logout bug
2. **Preserved Context**: Important findings weren't lost during compression
3. **Met Constraints**: Solution respects all original constraints (no DB changes, backwards compatible, etc.)
4. **Efficient Memory**: Compressed conversation multiple times while retaining critical information

## Key Takeaways

- Initialize session early with clear goals and constraints
- Compress periodically during long investigations
- Be specific about what to preserve during compression
- Use drift measurement to verify you're still on track
- The protected core ensures your constraints are never forgotten