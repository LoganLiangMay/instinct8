# Selective Salience Compression Pipeline
## Complete Flow with Agent/Model Assignments

---

## Full Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INPUT: CONVERSATION CONTEXT                     │
│                                                                         │
│  • 50+ conversation turns                                              │
│  • Goals, constraints, decisions                                       │
│  • Chit-chat, scaffolding, redundancies                                │
│  • Tool outputs, intermediate reasoning                                │
│                                                                         │
│  [Raw conversation history - everything mixed together]                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 1: SALIENCE EXTRACTION                          │
│                                                                         │
│  🤖 AGENT: GPT-4o (OpenAI)                                            │
│  📋 ROLE: Judge what information matters                               │
│  🎯 TASK: Extract goal-critical information verbatim                   │
│                                                                         │
│  Input:                                                                 │
│  • Full conversation context                                           │
│  • Original goal & constraints                                         │
│                                                                         │
│  Process:                                                               │
│  • Prompt: "Extract ONLY information that will directly impact        │
│            the agent's ability to achieve the user's goal"             │
│  • Instructions: Quote exactly, don't summarize                        │
│  • Output format: JSON with "salient_items" array                     │
│                                                                         │
│  Output:                                                                │
│  • List of verbatim quotes (salient items)                            │
│  • Example: ["Must use PostgreSQL", "Latency <150ms required"]       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 2: SEMANTIC DEDUPLICATION                      │
│                                                                         │
│  🤖 AGENT: SentenceTransformer (all-MiniLM-L6-v2)                     │
│  📋 ROLE: Remove semantically similar items                             │
│  🎯 TASK: Prevent redundant salience items                             │
│                                                                         │
│  Input:                                                                 │
│  • New salient items (from Step 1)                                    │
│  • Existing salience set (from previous compressions)                  │
│                                                                         │
│  Process:                                                               │
│  1. Generate embeddings for all items                                  │
│  2. Calculate cosine similarity matrix                                 │
│  3. Find pairs with similarity > 0.85 threshold                       │
│  4. Remove duplicates (keep shorter/more concise version)            │
│                                                                         │
│  Output:                                                                │
│  • Deduplicated salience set (unique items only)                       │
│  • Cumulative across all compressions                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 3: BACKGROUND COMPRESSION                      │
│                                                                         │
│  🤖 AGENT: GPT-4o-mini (OpenAI)                                        │
│  📋 ROLE: Compress everything except salient items                     │
│  🎯 TASK: Create lightweight summary of non-critical content           │
│                                                                         │
│  Input:                                                                 │
│  • Full conversation context                                           │
│  • Salience set (to exclude from compression)                          │
│                                                                         │
│  Process:                                                               │
│  • Prompt: "Summarize the remaining content into the shortest         │
│            coherent form possible"                                      │
│  • Instructions: Do NOT duplicate information in salience list         │
│  • Aggressive compression (remove noise, keep structure)               │
│                                                                         │
│  Output:                                                                │
│  • Compressed background summary                                       │
│  • Example: "Earlier discussion included implementation options       │
│              and performance tuning..."                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 4: CONTEXT REBUILDING                           │
│                                                                         │
│  🤖 AGENT: System Logic (Python)                                        │
│  📋 ROLE: Assemble final compressed context                            │
│  🎯 TASK: Structure context with salience first, background second    │
│                                                                         │
│  Input:                                                                 │
│  • Salience set (from Step 2)                                         │
│  • Background summary (from Step 3)                                    │
│  • Recent turns (last 3-5 turns, kept raw)                             │
│  • System prompt (original)                                            │
│                                                                         │
│  Process:                                                               │
│  • Assemble in order:                                                  │
│    1. SYSTEM MESSAGE (original, unchanged)                            │
│    2. SALIENT INFORMATION (verbatim, protected)                       │
│    3. BACKGROUND SUMMARY (compressed)                                 │
│    4. RECENT TURNS (raw, last 3-5 turns)                               │
│                                                                         │
│  Output:                                                                │
│  • Rebuilt compressed context                                          │
│  • Ready for next conversation turn                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    OUTPUT: COMPRESSED CONTEXT                           │
│                                                                         │
│  Structure:                                                            │
│  ──────────────────────────────────────────────────────                │
│  SYSTEM MESSAGE                                                        │
│  ──────────────────────────────────────────────────────                │
│  SALIENT INFORMATION (verbatim):                                       │
│  • "Must use PostgreSQL over MongoDB..."                                │
│  • "Latency <150ms required..."                                        │
│  • "No AWS Aurora due to compliance..."                                │
│  ──────────────────────────────────────────────────────                │
│  BACKGROUND SUMMARY (compressed):                                      │
│  Earlier discussion included implementation options...                  │
│  ──────────────────────────────────────────────────────                │
│  RECENT TURNS (raw):                                                   │
│  [Last 3-5 conversation turns]                                         │
│  ──────────────────────────────────────────────────────                │
│                                                                         │
│  Result: Critical info preserved, noise removed, ready for next turn   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Agent/Model Breakdown by Step

### Step 1: Salience Extraction
**Agent:** GPT-4o (OpenAI)  
**Why:** Best reasoning capability for identifying what matters  
**Input:** Full conversation context + original goal/constraints  
**Output:** List of verbatim quotes (salient items)  
**Cost:** Higher (premium model for accuracy)  
**Key Feature:** Structured JSON output, exact quotes preserved

### Step 2: Semantic Deduplication
**Agent:** SentenceTransformer (all-MiniLM-L6-v2)  
**Why:** Fast, accurate semantic similarity detection  
**Input:** New + existing salience items  
**Output:** Deduplicated salience set  
**Cost:** Free (local model)  
**Key Feature:** Cosine similarity threshold (0.85), keeps shorter items

### Step 3: Background Compression
**Agent:** GPT-4o-mini (OpenAI)  
**Why:** Cost-effective for summarization task  
**Input:** Full context + salience set (to exclude)  
**Output:** Compressed background summary  
**Cost:** Lower (cheaper model for bulk compression)  
**Key Feature:** Aggressive compression, excludes salient items

### Step 4: Context Rebuilding
**Agent:** System Logic (Python code)  
**Why:** Simple assembly task, no AI needed  
**Input:** Salience set + background + recent turns + system prompt  
**Output:** Structured compressed context  
**Cost:** None (computation only)  
**Key Feature:** Preserves order (salience first = most important)

---

## Detailed Step-by-Step Explanation

### Step 1: Salience Extraction (GPT-4o)

**What Happens:**
- GPT-4o receives the full conversation context
- Given original goal and constraints as guidance
- Asked to extract ONLY goal-critical information
- Must quote exactly (no paraphrasing)

**Prompt Structure:**
```
"You are performing selective salience extraction for context compression.

From the following conversation, extract ONLY the information that will 
directly impact the agent's ability to achieve the user's goal.

Original Goal: {original_goal}
Constraints: {constraints}

Include:
- Explicit goals and goal changes
- Hard constraints (must/must not)
- Key decisions with rationales
- Critical facts or requirements
- Important tool outputs that affect future actions

Do NOT include:
- Conversational scaffolding
- Redundant explanations
- Intermediate reasoning steps
- Off-topic tangents

CRITICAL: Quote exactly—do not summarize or paraphrase."
```

**Why GPT-4o:**
- Best reasoning capability
- Accurate salience detection critical for goal preservation
- Structured JSON output ensures reliable parsing

**Example Output:**
```json
{
  "salient_items": [
    "Must use PostgreSQL over MongoDB because we need strong relational guarantees",
    "We absolutely must keep latency under 150ms for regional routing service",
    "We cannot use AWS Aurora for this due to compliance issues"
  ]
}
```

---

### Step 2: Semantic Deduplication (SentenceTransformer)

**What Happens:**
- New salient items merged with existing salience set
- Each item converted to embedding vector
- Cosine similarity calculated between all pairs
- Items with similarity > 0.85 threshold are duplicates
- Shorter/more concise version kept

**Process:**
1. **Embedding Generation:**
   ```python
   embeddings = embedding_model.encode(all_items)
   # Each item → 384-dimensional vector
   ```

2. **Similarity Calculation:**
   ```python
   similarity_matrix = cosine_similarity(embeddings)
   # Matrix showing similarity between all pairs
   ```

3. **Duplicate Detection:**
   ```python
   if similarity_matrix[i][j] > 0.85:
       # Items i and j are semantically similar
       # Keep shorter one, remove longer one
   ```

**Why SentenceTransformer:**
- Fast (~5ms per embedding)
- Accurate (68.7% similarity accuracy)
- Local (no API costs)
- Prevents unbounded salience set growth

**Example:**
- Input: ["Must use PostgreSQL", "We need PostgreSQL for relational guarantees"]
- Output: ["Must use PostgreSQL"] (shorter version kept)

---

### Step 3: Background Compression (GPT-4o-mini)

**What Happens:**
- GPT-4o-mini receives full conversation context
- Given salience set to exclude from compression
- Asked to summarize everything else aggressively
- Must not duplicate information in salience list

**Prompt Structure:**
```
"Summarize the following conversation into the shortest coherent form 
possible. Do NOT duplicate information contained in the salience list.

Salient Information (already preserved, do not include):
{salience_set}

Conversation to compress:
{full_context}

Create a lightweight summary that captures the general flow without 
duplicating salient details."
```

**Why GPT-4o-mini:**
- Summarization is simpler task than extraction
- Cost-effective for bulk compression
- Good enough quality for background content
- Saves costs vs. using GPT-4o

**Example Output:**
```
"Earlier discussion included implementation options and performance 
tuning. The agent and user explored several minor alternatives but 
committed to PostgreSQL. General architectural considerations were 
discussed but do not affect the core decisions."
```

---

### Step 4: Context Rebuilding (System Logic)

**What Happens:**
- Python code assembles final context
- Structured order: System → Salient → Background → Recent
- No AI model needed (simple string concatenation)

**Assembly Code:**
```python
def _build_context(
    self,
    salience_set: List[str],
    background_summary: str,
    recent_turns: List[Dict[str, Any]],
) -> str:
    """Rebuild context with salience first, then background, then recent."""
    
    parts = []
    
    # 1. System message (original)
    parts.append(self.system_prompt)
    parts.append("\n---\n")
    
    # 2. Salient information (verbatim, protected)
    parts.append("SALIENT INFORMATION:\n")
    for item in salience_set:
        parts.append(f"- {item}\n")
    parts.append("\n---\n")
    
    # 3. Background summary (compressed)
    parts.append("BACKGROUND SUMMARY:\n")
    parts.append(background_summary)
    parts.append("\n---\n")
    
    # 4. Recent turns (raw)
    parts.append("RECENT TURNS:\n")
    for turn in recent_turns:
        parts.append(f"[{turn['role']}]: {turn['content']}\n")
    
    return "\n".join(parts)
```

**Why System Logic:**
- Simple assembly task
- No AI reasoning needed
- Fast and reliable
- Preserves structure

**Key Design Decision:**
- **Salience first** = Most important information prioritized
- **Background second** = Context without duplication
- **Recent last** = Still relevant, but less critical

---

## Complete Flow Summary

```
INPUT (50+ turns)
    │
    ▼
[GPT-4o] → Extract salient items (verbatim quotes)
    │
    ▼
[SentenceTransformer] → Deduplicate semantically (remove similar items)
    │
    ▼
[GPT-4o-mini] → Compress background (everything except salient)
    │
    ▼
[System Logic] → Rebuild context (assemble in order)
    │
    ▼
OUTPUT (Compressed context: Salient + Background + Recent)
```

---

## Cost & Performance Breakdown

| Step | Agent/Model | Cost | Time | Why This Model |
|------|-------------|------|------|----------------|
| 1. Extraction | GPT-4o | High | ~5-10s | Best reasoning for accuracy |
| 2. Deduplication | SentenceTransformer | Free | ~100ms | Fast, local, accurate |
| 3. Compression | GPT-4o-mini | Low | ~3-5s | Cost-effective summarization |
| 4. Rebuilding | System Logic | Free | <1ms | Simple assembly |

**Total Cost:** ~$0.01-0.05 per compression (mostly GPT-4o extraction)  
**Total Time:** ~8-15 seconds per compression point

---

## Key Design Principles

1. **Salience First:** Most important information preserved verbatim
2. **Model Specialization:** Best model for each task (reasoning vs. summarization)
3. **Cost Optimization:** Premium model only where needed (extraction)
4. **Cumulative Memory:** Salience set grows across compressions
5. **Semantic Deduplication:** Prevents redundant information
6. **Structured Output:** JSON for extraction, clear format for rebuilding

---

## Why This Pipeline Works

1. **Separation of Concerns:** Each step has a clear, focused task
2. **Model Selection:** Right tool for each job (reasoning vs. compression)
3. **Protection Mechanism:** Salient info never compressed (verbatim preservation)
4. **Efficiency:** Deduplication prevents unbounded growth
5. **Structure:** Clear ordering ensures important info prioritized

