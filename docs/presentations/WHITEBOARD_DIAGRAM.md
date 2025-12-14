# Selective Salience Compression - Whiteboard Diagram

## How to Draw This on a Whiteboard

### Step 1: The Problem (Left Side)

```
┌─────────────────────────────────────┐
│   LONG CONVERSATION (50+ turns)     │
│                                      │
│  • Goals & constraints               │
│  • Key decisions                     │
│  • Critical facts                    │
│  • Chit-chat & scaffolding           │
│  • Redundant explanations            │
│  • Off-topic tangents               │
│                                      │
│  [Everything mixed together]         │
└─────────────────────────────────────┘
```

**Label:** "Problem: Context too long, need to compress"

---

### Step 2: The Split (Middle)

Draw an arrow pointing right, then split into TWO paths:

```
                    │
                    ▼
        ┌───────────────────────┐
        │   MODEL DECIDES:      │
        │   "What matters?"     │
        └───────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
```

**Label:** "Selective = Model judges importance"

---

### Step 3: Two Paths (Right Side)

**Path 1: SALIENT (Top Path)**
```
┌─────────────────────────────────────┐
│   SALIENCE SET                      │
│   (VERBATIM - Never Compressed)    │
│                                      │
│  ✓ "Must use PostgreSQL"            │
│  ✓ "Latency <150ms required"       │
│  ✓ "No AWS Aurora (compliance)"    │
│  ✓ "Budget max $10K"               │
│                                      │
│  [Protected - Exact Quotes]         │
└─────────────────────────────────────┘
```

**Path 2: BACKGROUND (Bottom Path)**
```
┌─────────────────────────────────────┐
│   BACKGROUND SUMMARY                │
│   (COMPRESSED - Aggressively)       │
│                                      │
│  "Earlier discussion included       │
│   implementation options and        │
│   performance tuning. General        │
│   architectural considerations       │
│   were discussed."                  │
│                                      │
│  [Compressed - Lightweight]        │
└─────────────────────────────────────┘
```

**Label Top:** "Signal - What Matters"  
**Label Bottom:** "Noise - Everything Else"

---

### Step 4: The Rebuild (Bottom Right)

```
        ┌───────────┬───────────┐
        │           │           │
        ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ SYSTEM   │ │ SALIENT  │ │BACKGROUND │
│ MESSAGE  │ │ (verbatim)│ │(compressed)│
└──────────┘ └──────────┘ └──────────┘
        │           │           │
        └───────────┴───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   NEW CONTEXT        │
        │   (Ready for next    │
        │    conversation turn) │
        └───────────────────────┘
```

**Label:** "Rebuilt Context: Signal First, Noise Compressed"

---

## Complete Flow (One Diagram)

```
┌─────────────────────────────────────────────────────────────┐
│                    ORIGINAL CONTEXT                         │
│         (50+ turns: goals, constraints, decisions,          │
│          chit-chat, scaffolding, redundancies)              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │   SELECTIVE EXTRACTION                │
        │   "What will matter later?"           │
        │   (Model judges importance)           │
        └───────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
    ┌──────────────────────┐  ┌──────────────────────┐
    │  SALIENCE SET        │  │  BACKGROUND           │
    │  (VERBATIM)          │  │  (COMPRESSED)         │
    │                      │  │                      │
    │  ✓ Goals            │  │  • Chit-chat         │
    │  ✓ Constraints      │  │  • Scaffolding       │
    │  ✓ Decisions        │  │  • Redundancies       │
    │  ✓ Critical facts   │  │  • Minor details     │
    │                      │  │                      │
    │  [Protected]         │  │  [Aggressively       │
    │                      │  │   compressed]        │
    └──────────────────────┘  └──────────────────────┘
                │                       │
                └───────────┬───────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │   REBUILT CONTEXT                     │
        │                                        │
        │   SYSTEM MESSAGE                      │
        │   ─────────────────                    │
        │   SALIENT INFO (verbatim) ← Protected │
        │   ─────────────────                    │
        │   BACKGROUND (compressed)             │
        │   ─────────────────                    │
        │   RECENT TURNS (raw)                  │
        └───────────────────────────────────────┘
```

---

## Key Labels to Add

**On the diagram, add these labels:**

1. **"Selective"** = Model decides what matters (not a fixed schema)
2. **"Salience"** = Goal-critical information (signal vs. noise)
3. **"Verbatim"** = Exact quotes preserved (never summarized)
4. **"Compressed"** = Aggressive summarization (removes noise)

---

## Comparison: Selective Salience vs. Protected Core

Draw side-by-side:

```
SELECTIVE SALIENCE          PROTECTED CORE
──────────────────          ──────────────
                           
Model decides what          Fixed schema:
matters                    • Goals
                          • Constraints
Adaptive                   • Decisions
                          • Facts
Tests frontier             Never compressed
capability                 
                          Always preserved
More flexible              More reliable
More error-prone           Less adaptive
```

---

## Example: Before & After

**BEFORE Compression:**
```
User: "Let's choose PostgreSQL over MongoDB because we need 
       strong relational guarantees."
Agent: "Agreed. That means we can use row-level locking..."
User: "Also, we absolutely must keep latency under 150ms..."
Agent: "Good point. We'll need connection pooling..."
[20 more turns of discussion, tangents, explanations]
```

**AFTER Selective Salience:**
```
SALIENT INFORMATION (verbatim):
• "Choose PostgreSQL over MongoDB because we need strong 
   relational guarantees"
• "We absolutely must keep latency under 150ms for regional 
   routing service"
• "We cannot use AWS Aurora due to compliance issues"

BACKGROUND SUMMARY (compressed):
Earlier discussion included implementation options and 
performance tuning. General architectural considerations 
were discussed but do not affect core decisions.
```

**Result:** Critical constraints preserved, noise removed!

---

## Talking Points While Drawing

1. **"Selective"** = The model itself decides what matters
   - Not a fixed schema
   - Tests frontier capability
   - More adaptive but more error-prone

2. **"Salience"** = Goal-critical information
   - What will impact future actions
   - Goals, constraints, decisions, critical facts
   - The "signal" vs. "noise"

3. **The Split:**
   - Top path: Salient info → Protected verbatim
   - Bottom path: Everything else → Aggressively compressed

4. **The Rebuild:**
   - Salient info comes first (most important)
   - Background compressed (saves tokens)
   - Recent turns raw (still relevant)

5. **Why This Matters:**
   - Tests if models can predict what they'll need
   - Human-like memory (remember important bits)
   - Adaptive to different task types

