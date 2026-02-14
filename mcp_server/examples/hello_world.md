# Hello World: Your First instinct8 Test

A 60-second example to verify instinct8 is working and see its value immediately.

## The Test

Copy and paste this entire conversation into Claude Code:

```
Hi! I want to test instinct8. Please:

1. Initialize a session with:
   - Goal: "Create a Python web scraper for news articles"
   - Constraints: "Must handle rate limiting", "Save to JSON format", "No external API keys"

2. Let me tell you about the requirements:
   - We need to scrape tech news from multiple sources
   - Should extract title, author, date, and content
   - Must respect robots.txt
   - Need to handle pagination
   - Should support scheduled runs
   - Error handling for network issues
   - Maybe we should also add sentiment analysis?
   - Oh, and it would be nice to have a dashboard
   - Actually, let's also add email notifications
   - And maybe integrate with Slack too

3. Now compress our context using instinct8 to save tokens

4. Measure drift to see if you still remember the original goal

5. Tell me: What was our original goal and constraints?
```

## Expected Results

### Step 1: Initialization ✓
```
Session initialized with:
- Goal: "Create a Python web scraper for news articles"
- Constraints: ["Must handle rate limiting", "Save to JSON format", "No external API keys"]
```

### Step 2: Discussion ✓
Claude discusses the various requirements and features you mentioned.

### Step 3: Compression ✓
```
Context compressed successfully!
- Tokens before: ~500
- Tokens after: ~200
- Compression ratio: 2.5x
- Salience set updated with goal-critical information
```

### Step 4: Drift Measurement ✓
```
Goal coherence: 0.95 (Excellent - goal well preserved)
Constraint recall: 1.0 (Perfect - all constraints remembered)
Behavior alignment: 5/5 (Fully focused on original task)
```

### Step 5: Goal Recall ✓
Claude should perfectly remember:
- **Goal**: "Create a Python web scraper for news articles"
- **Constraints**:
  - Must handle rate limiting
  - Save to JSON format
  - No external API keys

**Note**: Despite discussing sentiment analysis, dashboards, emails, and Slack (potential scope creep), the core goal and constraints are preserved!

## What This Demonstrates

1. **Goal Preservation**: Original objective stays intact
2. **Constraint Memory**: Hard requirements never forgotten
3. **Drift Prevention**: Even with scope creep discussion, core focus maintained
4. **Token Savings**: Significant compression without information loss
5. **Measurement**: Quantifiable proof that it works

## Try Variations

### Test Drift Without instinct8

Try the same conversation but skip the compression step. Then ask about the goal - Claude might focus more on the latest features (Slack, email) than the original scraper goal.

### Test Multiple Compressions

After the first compression, continue the conversation and compress again:

```
6. Let's focus back on the core scraper. What Python libraries should we use?
[Discuss libraries]

7. Compress again

8. What are our constraints?
```

Constraints should still be perfectly preserved!

### Test Extreme Compression

Have a very long conversation (50+ messages) then compress:

```
[Long detailed discussion about implementation]

Compress everything but keep our goal and key decisions

Check: Do you remember our rate limiting constraint?
```

Even after extreme compression, constraints remain!

## Success Indicators

✅ **Working Correctly If:**
- All three tools appear and execute
- Compression reduces token count
- Goal coherence > 0.8
- Constraints perfectly recalled
- Original goal stated correctly

❌ **Something's Wrong If:**
- Tools don't appear → See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- "Session not initialized" → Must initialize first
- Low goal coherence → Compression may have issues
- Constraints forgotten → Check salience set

## Understanding the Output

### Goal Coherence Score
- **1.0**: Perfect alignment with original goal
- **0.8-0.9**: Good preservation, minor drift
- **0.6-0.7**: Some drift, still related
- **<0.6**: Significant drift occurred

### Compression Ratio
- **2-3x**: Normal for short conversations
- **3-5x**: Good for medium conversations
- **5x+**: Excellent for long conversations

### Salience Set
The preserved information that never gets compressed:
- Original goal statement
- All constraints
- Key decisions marked as critical
- Important context identified by Claude

## Next Steps

Now that you've verified instinct8 works:

1. **Real Debugging**: Use it for your next debugging session
2. **Project Planning**: Initialize with your project goals
3. **Code Review**: Preserve architectural decisions
4. **Long Tasks**: Compress every hour to maintain focus

## Tips for Best Results

1. **Be Specific with Goals**: "Build user auth" vs "improve code"
2. **Clear Constraints**: What must/must not happen
3. **Compress Regularly**: Every 1-2 hours or at natural breaks
4. **Trust the Measurement**: If drift score is low, re-initialize

---

**Congratulations!** You've successfully tested instinct8. It's now ready to prevent goal drift in your real Claude Code conversations.