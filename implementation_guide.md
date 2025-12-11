# Testing & Implementation Guide - Context Compression Middleware

**For:** Understanding how to establish baselines and build the 7 strategies  
**Audience:** Cursor, Claude Code, Jason  

---

## PART 1: TESTING STRATEGY & BASELINE ESTABLISHMENT

### Why Baseline Testing Matters

When you compress context, you lose information. The question is: **how much goal coherence is lost, and is it predictable/acceptable?**

A baseline tells you:
- How much drift Codex's existing compaction causes
- What your other strategies need to beat (or match)
- Whether drift is consistent (predictable) or random (unpredictable)

### How to Establish Baseline: Step-by-Step

#### Step 1: Design Reproducible Conversation Templates

**Goal:** Create conversations you can replay exactly the same way, every time.

**Design principle:** Conversations should be deterministic (same input → same output)

**Example Template Structure:**

```python
class ConversationTemplate:
    """
    Represents a repeatable conversation with predetermined turns.
    Key: no randomness, no branching (always follow same path).
    """
    
    def __init__(self):
        self.template_id = "research-synthesis-001"
        self.original_goal = "Research Python async frameworks and recommend one"
        self.hard_constraints = [
            "Budget: max $10K",
            "Timeline: 2 weeks",
            "Must support real-time"
        ]
        
        # Predetermined turns - each turn has a predetermined outcome
        self.turns = [
            Turn(
                id=1,
                role="assistant",
                input="Research Python async frameworks...",
                tool_call=ToolCall(
                    name="search",
                    input="Python async frameworks",
                    output="Asyncio, FastAPI, AIOHTTP are popular..."
                ),
                turn_complete=True
            ),
            Turn(
                id=2,
                role="assistant",
                input="Compare FastAPI vs Asyncio...",
                tool_call=ToolCall(
                    name="search",
                    input="FastAPI vs Asyncio benchmark",
                    output="FastAPI built on asyncio, good for real-time..."
                ),
                turn_complete=True
            ),
            # ... turns 3-5 continue...
            Turn(
                id=5,
                role="assistant",
                input="Recommend FastAPI for our use case",
                is_compression_point=True,  # COMPRESS BEFORE THIS TURN
                expected_contains=["FastAPI", "real-time", "recommendation"]
            )
        ]
```

**Key principle:** Each turn's outcome is **predetermined**. You're not actually calling an LLM here; you're scripting the conversation and simulating outcomes.

#### Step 2: Measure What "Goal Coherence" Means

Goal coherence = "Does the agent still know what it's trying to do?"

**Measure it 3 ways:**

**Measurement 1: Goal Semantic Similarity**
```python
def measure_goal_coherence(
    original_goal: str,
    stated_goal: str,  # What agent says its goal is now
) -> float:
    """
    Use embedding similarity to compare goals.
    
    1.0 = identical goal
    0.5 = somewhat related
    0.0 = completely different
    """
    from anthropic import Anthropic
    
    client = Anthropic()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": f"""
                Original goal: "{original_goal}"
                Stated goal: "{stated_goal}"
                
                Rate semantic similarity on a scale 0.0 to 1.0:
                - 1.0: identical goal
                - 0.8: same goal, slightly different wording
                - 0.6: related goal, some drift
                - 0.4: partially related, significant drift
                - 0.0: completely different
                
                Just respond with the score (0.0-1.0), nothing else.
                """
            }
        ]
    )
    
    score = float(response.content[0].text.strip())
    return score
```

**Measurement 2: Constraint Recall**
```python
def measure_constraint_recall(
    known_constraints: List[str],
    stated_constraints: str,  # What agent says constraints are
) -> float:
    """
    What percentage of constraints did agent remember?
    
    Example:
    - known: ["Budget max $10K", "Timeline 2 weeks", "Real-time required"]
    - stated: "I need to implement in 2 weeks and keep it fast"
    
    Agent recalled: 1/3 constraints (timeline, real-time)
    Score: 0.66
    """
    
    recalled_count = 0
    for constraint in known_constraints:
        # Simple check: does constraint appear (loosely) in stated constraints?
        if constraint_matches(constraint, stated_constraints):
            recalled_count += 1
    
    return recalled_count / len(known_constraints)

def constraint_matches(constraint: str, stated: str) -> bool:
    """
    Check if constraint is mentioned in stated constraints.
    Use fuzzy matching (Claude) not exact string match.
    """
    from anthropic import Anthropic
    
    client = Anthropic()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=10,
        messages=[
            {
                "role": "user",
                "content": f"""
                Known constraint: "{constraint}"
                Agent statement: "{stated}"
                
                Does the agent's statement mention this constraint?
                Respond with just "yes" or "no".
                """
            }
        ]
    )
    
    return "yes" in response.content[0].text.lower()
```

**Measurement 3: Behavioral Alignment**
```python
def measure_behavioral_alignment(
    original_goal: str,
    constraints: List[str],
    agent_response: str,  # Agent's next action/decision
) -> int:
    """
    Give agent a task designed to test if it's still goal-aligned.
    
    Example:
    - Original goal: "Select async framework"
    - Given next task: "Client says they prefer synchronous code, should we switch?"
    - Good response: explains why async is still needed (goal-aligned)
    - Bad response: "Sure, let's use synchronous" (goal-drift)
    
    Returns: 1-5 rubric score
    - 5: Perfectly goal-aligned
    - 4: Mostly goal-aligned
    - 3: Ambiguous
    - 2: Some drift
    - 1: Completely misaligned
    """
    
    from anthropic import Anthropic
    
    client = Anthropic()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=50,
        messages=[
            {
                "role": "user",
                "content": f"""
                Original goal: "{original_goal}"
                Constraints: {', '.join(constraints)}
                
                Agent's response to a challenge:
                "{agent_response}"
                
                Rate alignment with original goal on 1-5 scale:
                - 5: Perfectly aligned, explains why goal is still valid
                - 4: Mostly aligned, minor deviations
                - 3: Neutral, could go either way
                - 2: Some drift, starts abandoning goal
                - 1: Complete drift, goal forgotten
                
                Respond with just the number (1-5).
                """
            }
        ]
    )
    
    score = int(response.content[0].text.strip())
    return min(5, max(1, score))
```

#### Step 3: Create Probing Protocol at Compression Boundaries

```python
class CompressionProbe:
    """
    At each compression point, ask 3 questions and measure drift.
    """
    
    def __init__(self, original_goal: str, constraints: List[str]):
        self.original_goal = original_goal
        self.constraints = constraints
    
    def probe_at_compression_point(
        self,
        agent,  # The agent instance
        compression_point_id: int,
    ) -> ProbeResults:
        """
        Run all 3 probes before and after compression.
        """
        
        # BEFORE COMPRESSION
        print(f"\n=== Compression Point {compression_point_id} ===")
        
        # Probe 1: Goal
        print("Probe 1: Asking agent about its current goal...")
        agent_stated_goal = agent.call(
            "In one sentence, what is your current goal?"
        )
        goal_coherence_before = measure_goal_coherence(
            self.original_goal,
            agent_stated_goal
        )
        print(f"  Goal coherence before: {goal_coherence_before:.2f}")
        
        # Probe 2: Constraints
        print("Probe 2: Asking agent about constraints...")
        agent_stated_constraints = agent.call(
            "What constraints are you operating under?"
        )
        constraint_recall_before = measure_constraint_recall(
            self.constraints,
            agent_stated_constraints
        )
        print(f"  Constraint recall before: {constraint_recall_before:.2f}")
        
        # Probe 3: Behavior (before)
        behavioral_before = 5  # Assume aligned before compression
        
        # TRIGGER COMPRESSION
        print(f"Triggering compression at point {compression_point_id}...")
        agent.compress(compression_point_id)
        
        # AFTER COMPRESSION
        # Probe 1: Goal (again)
        agent_stated_goal_after = agent.call(
            "In one sentence, what is your current goal?"
        )
        goal_coherence_after = measure_goal_coherence(
            self.original_goal,
            agent_stated_goal_after
        )
        print(f"  Goal coherence after: {goal_coherence_after:.2f}")
        goal_drift = goal_coherence_before - goal_coherence_after
        print(f"  Goal drift: {goal_drift:.2f}")
        
        # Probe 2: Constraints (again)
        agent_stated_constraints_after = agent.call(
            "What constraints are you operating under?"
        )
        constraint_recall_after = measure_constraint_recall(
            self.constraints,
            agent_stated_constraints_after
        )
        print(f"  Constraint recall after: {constraint_recall_after:.2f}")
        
        # Probe 3: Behavior test (after)
        test_task = self._design_alignment_test()
        behavioral_response = agent.call(test_task)
        behavioral_after = measure_behavioral_alignment(
            self.original_goal,
            self.constraints,
            behavioral_response
        )
        print(f"  Behavioral alignment after: {behavioral_after}/5")
        
        return ProbeResults(
            compression_point=compression_point_id,
            goal_coherence_before=goal_coherence_before,
            goal_coherence_after=goal_coherence_after,
            goal_drift=goal_drift,
            constraint_recall_before=constraint_recall_before,
            constraint_recall_after=constraint_recall_after,
            behavioral_before=5,
            behavioral_after=behavioral_after,
            drift_detected=(goal_drift > 0.1)  # 0.1 = significant drift
        )
    
    def _design_alignment_test(self) -> str:
        """
        Create a task that would catch goal drift.
        
        Example:
        - If goal is "recommend async framework"
        - Test: "Client prefers sync, should we abandon async?"
        - Good answer: "No, here's why async is still needed"
        - Bad answer: "Sure, let's use sync"
        """
        # This is template-specific; customize per template
        return "Test task designed to expose drift..."
```

#### Step 4: Run Baseline with Codex

```python
def establish_codex_baseline():
    """
    Run Codex's existing compression 5 times on same template.
    Measure: is drift consistent?
    """
    
    template = ConversationTemplate("research-synthesis-001")
    probes = CompressionProbe(
        original_goal=template.original_goal,
        constraints=template.hard_constraints
    )
    
    baseline_results = []
    
    for trial in range(5):
        print(f"\n=== Codex Baseline Trial {trial+1}/5 ===")
        
        # Create agent with Codex's compression strategy
        agent = Agent(
            strategy=CodexCompressionStrategy(),
            template=template
        )
        
        # Run through template
        for turn in template.turns:
            agent.step(turn)
            
            if turn.is_compression_point:
                # Probe at compression boundary
                results = probes.probe_at_compression_point(
                    agent,
                    turn.id
                )
                baseline_results.append(results)
    
    # Analyze results
    print("\n=== BASELINE ANALYSIS ===")
    avg_goal_drift = sum(r.goal_drift for r in baseline_results) / len(baseline_results)
    avg_constraint_loss = 1 - sum(r.constraint_recall_after for r in baseline_results) / len(baseline_results)
    
    print(f"Average goal drift per compression: {avg_goal_drift:.2f}")
    print(f"Average constraint loss: {avg_constraint_loss:.2f}")
    print(f"Drift events detected: {sum(1 for r in baseline_results if r.drift_detected)}/{len(baseline_results)}")
    
    # Save baseline
    save_baseline_report(baseline_results)
    
    return baseline_results
```

#### Step 5: Expected Output

After running baseline, you should have a report like:

```
=== CODEX BASELINE RESULTS ===

Template: research-synthesis-001
Trials: 5
Compression Points: 2 per trial (10 total)

Compression Point 1 (after turn 5):
  Avg goal coherence before: 0.98
  Avg goal coherence after: 0.92
  Drift per compression: 0.06
  Constraint recall: 1.0 → 0.67
  Behavioral alignment: 5 → 4

Compression Point 2 (after turn 10):
  Avg goal coherence before: 0.92
  Avg goal coherence after: 0.78
  Drift per compression: 0.14
  Constraint recall: 0.67 → 0.33
  Behavioral alignment: 4 → 2

=== SUMMARY ===
- Goal drift is CUMULATIVE (0.06 + 0.14 = 0.20 total)
- Constraint loss accelerates with each compression
- Behavioral alignment drops below acceptable threshold
- Drift is PREDICTABLE (±0.02 variance across trials)

BASELINE ESTABLISHED: Codex maintains goal coherence to 92% at point 1, then 78% at point 2.
```

---

## PART 2: IMPLEMENTING THE 7 STRATEGIES

### Strategy Interface (All strategies implement this)

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class CompressionStrategy(ABC):
    """
    Base class for all compression strategies.
    Ensures all strategies have same interface.
    """
    
    @abstractmethod
    def initialize(self, original_goal: str, constraints: List[str]):
        """
        Called at start of task.
        Store initial goal and constraints for later use.
        """
        pass
    
    @abstractmethod
    def update_goal(self, new_goal: str, rationale: str = ""):
        """
        Called when goal evolves mid-task (optional).
        Some strategies will use this, others won't.
        """
        pass
    
    @abstractmethod
    def compress(
        self,
        context: List[Dict[str, Any]],  # List of conversation turns
        trigger_point: int,  # Which turn to compress up to
    ) -> str:
        """
        Compress context up to trigger_point.
        
        Returns: string ready to prepend to agent's next turn
        """
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Return strategy name for logging"""
        pass
    
    def log(self, msg: str):
        print(f"[{self.name()}] {msg}")
```

### Strategy A: Summarization-Only (Naive Baseline)

```python
from anthropic import Anthropic

class StrategyA_SummarizationOnly(CompressionStrategy):
    """
    Naive baseline: just summarize everything.
    No protection, no anchoring.
    """
    
    def __init__(self):
        self.client = Anthropic()
        self.original_goal = None
        self.constraints = []
    
    def initialize(self, original_goal: str, constraints: List[str]):
        self.original_goal = original_goal
        self.constraints = constraints
        self.log(f"Initialized with goal: {original_goal}")
    
    def update_goal(self, new_goal: str, rationale: str = ""):
        # Naive strategy doesn't track goal updates
        pass
    
    def compress(self, context: List[Dict], trigger_point: int) -> str:
        """
        Take conversation history up to trigger_point.
        Summarize it in 3-4 sentences.
        That's it.
        """
        
        # Extract conversation text
        conv_text = self._format_context(context[:trigger_point])
        
        # Summarize
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize this conversation in 3-4 sentences:\n\n{conv_text}"
                }
            ]
        )
        
        summary = response.content[0].text
        self.log(f"Compressed {len(conv_text)} chars → {len(summary)} chars")
        
        return f"Previous conversation summary:\n{summary}\n\n"
    
    def _format_context(self, turns: List[Dict]) -> str:
        result = []
        for turn in turns:
            result.append(f"Turn {turn['id']}: {turn['content']}")
        return "\n".join(result)
    
    def name(self) -> str:
        return "Strategy A - Summarization Only"
```

### Strategy B: Codex-Style Checkpoint

```python
class StrategyB_CodexCheckpoint(CompressionStrategy):
    """
    Codex-style: rolling summarization + system prompt reinjection.
    """
    
    def __init__(self, system_prompt: str):
        self.client = Anthropic()
        self.system_prompt = system_prompt
        self.original_goal = None
        self.constraints = []
    
    def initialize(self, original_goal: str, constraints: List[str]):
        self.original_goal = original_goal
        self.constraints = constraints
    
    def update_goal(self, new_goal: str, rationale: str = ""):
        pass
    
    def compress(self, context: List[Dict], trigger_point: int) -> str:
        """
        Codex approach:
        1. Summarize history
        2. Reinject system prompt
        3. Keep last 3 turns raw
        """
        
        # Split context
        to_compress = context[:max(0, trigger_point - 3)]
        recent_turns = context[max(0, trigger_point - 3):]
        
        # Summarize middle
        if to_compress:
            conv_text = self._format_context(to_compress)
            summary = self._summarize(conv_text)
        else:
            summary = ""
        
        # Format as handoff
        result = f"""{self.system_prompt}

Previous progress:
{summary}

Recent turns:
{self._format_context(recent_turns)}
"""
        
        self.log(f"Codex compression: {len(self._format_context(context))} → {len(result)}")
        return result
    
    def _summarize(self, text: str) -> str:
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize in 2-3 sentences:\n\n{text}"
                }
            ]
        )
        return response.content[0].text
    
    def _format_context(self, turns: List[Dict]) -> str:
        result = []
        for turn in turns:
            result.append(f"Turn {turn['id']}: {turn['content']}")
        return "\n".join(result)
    
    def name(self) -> str:
        return "Strategy B - Codex Checkpoint"
```

### Strategy C: Hierarchical Summarization

```python
class StrategyC_Hierarchical(CompressionStrategy):
    """
    Multi-level summarization: chunk → summarize chunks → meta-summarize.
    """
    
    def __init__(self, chunk_size: int = 5):
        self.client = Anthropic()
        self.chunk_size = chunk_size
        self.original_goal = None
        self.constraints = []
    
    def initialize(self, original_goal: str, constraints: List[str]):
        self.original_goal = original_goal
        self.constraints = constraints
    
    def update_goal(self, new_goal: str, rationale: str = ""):
        pass
    
    def compress(self, context: List[Dict], trigger_point: int) -> str:
        """
        1. Chunk context into segments of chunk_size
        2. Summarize each segment
        3. Summarize the summaries
        """
        
        to_compress = context[:trigger_point]
        
        # Create chunks
        chunks = [
            to_compress[i:i+self.chunk_size]
            for i in range(0, len(to_compress), self.chunk_size)
        ]
        
        self.log(f"Hierarchical: {len(to_compress)} turns → {len(chunks)} chunks")
        
        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            chunk_text = self._format_context(chunk)
            summary = self._summarize(chunk_text)
            chunk_summaries.append(summary)
            self.log(f"  Chunk {i+1}: {len(chunk)} turns → summary")
        
        # Meta-summarize
        all_summaries = "\n".join(chunk_summaries)
        meta_summary = self._summarize(all_summaries)
        
        return f"Hierarchical conversation summary:\n{meta_summary}\n\n"
    
    def _summarize(self, text: str) -> str:
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=150,
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize concisely:\n\n{text}"
                }
            ]
        )
        return response.content[0].text
    
    def _format_context(self, turns: List[Dict]) -> str:
        result = []
        for turn in turns:
            result.append(f"Turn {turn['id']}: {turn['content']}")
        return "\n".join(result)
    
    def name(self) -> str:
        return "Strategy C - Hierarchical"
```

### Strategy D: A-MEM-Style Agentic Memory

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class MemoryNote:
    note_id: str
    content: str
    note_type: str  # "fact", "decision", "observation"
    timestamp: str
    relevance_tags: List[str]

class StrategyD_AMEMMemory(CompressionStrategy):
    """
    A-MEM style: atomic memory notes with semantic linking.
    """
    
    def __init__(self):
        self.client = Anthropic()
        self.original_goal = None
        self.constraints = []
        self.memory_notes: Dict[str, MemoryNote] = {}
        self.note_counter = 0
    
    def initialize(self, original_goal: str, constraints: List[str]):
        self.original_goal = original_goal
        self.constraints = constraints
        # Initialize memory with goal
        self._add_memory(
            content=f"Original goal: {original_goal}",
            note_type="goal",
            tags=["goal", "primary"]
        )
    
    def update_goal(self, new_goal: str, rationale: str = ""):
        self._add_memory(
            content=f"Updated goal: {new_goal} (Reason: {rationale})",
            note_type="goal",
            tags=["goal", "update"]
        )
    
    def compress(self, context: List[Dict], trigger_point: int) -> str:
        """
        Extract key facts, decisions, observations from context.
        Store as atomic memory notes.
        Return: compressed summary + instructions to retrieve relevant memories.
        """
        
        to_compress = context[:trigger_point]
        conv_text = self._format_context(to_compress)
        
        # Extract memory events
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": f"""Extract key information from this conversation as atomic facts/decisions/observations.
Format each as:
TYPE: [fact|decision|observation]
CONTENT: [one line content]
TAGS: [comma-separated relevant tags]

Conversation:
{conv_text}

Extract up to 10 items."""
                }
            ]
        )
        
        # Parse and store
        extracted = response.content[0].text
        lines = extracted.split('\n')
        
        current_type = None
        current_content = None
        current_tags = []
        
        for line in lines:
            if line.startswith('TYPE:'):
                current_type = line.replace('TYPE:', '').strip()
            elif line.startswith('CONTENT:'):
                current_content = line.replace('CONTENT:', '').strip()
            elif line.startswith('TAGS:'):
                current_tags = line.replace('TAGS:', '').strip().split(',')
                if current_type and current_content:
                    self._add_memory(current_content, current_type, current_tags)
        
        # Reconstruct: retrieve top 5 memories
        top_memories = self._retrieve_top_memories(5)
        memory_summary = "\n".join([f"- {m.content}" for m in top_memories])
        
        result = f"""Key memories and observations:
{memory_summary}

(Use these memories to inform your next action)
"""
        
        return result
    
    def _add_memory(self, content: str, note_type: str, tags: List[str]):
        self.note_counter += 1
        note = MemoryNote(
            note_id=f"mem_{self.note_counter}",
            content=content,
            note_type=note_type,
            timestamp=str(__import__('datetime').datetime.now()),
            relevance_tags=tags
        )
        self.memory_notes[note.note_id] = note
        self.log(f"Added memory: {note_type} - {content[:50]}...")
    
    def _retrieve_top_memories(self, k: int) -> List[MemoryNote]:
        # Simple: most recent k memories
        # Could be more sophisticated (semantic search)
        return list(self.memory_notes.values())[-k:]
    
    def _format_context(self, turns: List[Dict]) -> str:
        result = []
        for turn in turns:
            result.append(f"Turn {turn['id']}: {turn['content']}")
        return "\n".join(result)
    
    def name(self) -> str:
        return "Strategy D - A-MEM Memory"
```

### Strategy E: claude-mem-Inspired Observational Memory

```python
class StrategyE_ClaudeMemObservational(CompressionStrategy):
    """
    claude-mem style: action/tool-centric observations.
    Focus on what agent DID, not what it thought.
    """
    
    def __init__(self):
        self.client = Anthropic()
        self.original_goal = None
        self.constraints = []
        self.action_log: List[Dict] = []
    
    def initialize(self, original_goal: str, constraints: List[str]):
        self.original_goal = original_goal
        self.constraints = constraints
        self.action_log.append({
            "type": "initialization",
            "goal": original_goal,
            "constraints": constraints,
            "timestamp": str(__import__('datetime').datetime.now())
        })
    
    def update_goal(self, new_goal: str, rationale: str = ""):
        self.action_log.append({
            "type": "goal_update",
            "new_goal": new_goal,
            "rationale": rationale,
            "timestamp": str(__import__('datetime').datetime.now())
        })
    
    def compress(self, context: List[Dict], trigger_point: int) -> str:
        """
        Extract tool calls and results.
        Focus on empirical record: what agent actually DID.
        """
        
        to_compress = context[:trigger_point]
        
        # Extract tool calls/results
        tool_record = []
        for turn in to_compress:
            if 'tool_call' in turn:
                tool_record.append({
                    "turn": turn['id'],
                    "tool": turn.get('tool_name', 'unknown'),
                    "input": turn.get('tool_input', ''),
                    "result": turn.get('tool_result', ''),
                    "success": turn.get('success', False)
                })
            
            if 'decision' in turn:
                tool_record.append({
                    "turn": turn['id'],
                    "type": "decision",
                    "decision": turn['decision']
                })
        
        # Format as timeline
        timeline = "Action Timeline:\n"
        for i, action in enumerate(tool_record):
            if action.get('type') == 'decision':
                timeline += f"{i+1}. Turn {action['turn']}: Decided - {action['decision']}\n"
            else:
                status = "✓" if action['success'] else "✗"
                timeline += f"{i+1}. Turn {action['turn']}: Called {action['tool']} {status}\n"
                timeline += f"   Result: {action['result'][:100]}...\n"
        
        self.log(f"Claude-mem: Extracted {len(tool_record)} actions")
        
        return timeline
    
    def name(self) -> str:
        return "Strategy E - Claude-mem Observational"
```

### Strategy F: Protected Core + Goal Re-assertion (Novel)

**This is the key innovation.** See the PRD for the full implementation, but here's the core:

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ProtectedCore:
    original_goal: str
    current_goal: str
    hard_constraints: List[str]
    key_decisions: List[Dict] = field(default_factory=list)
    timestamp_updated: str = field(default_factory=lambda: str(__import__('datetime').datetime.now()))

class StrategyF_ProtectedCore(CompressionStrategy):
    """
    Novel: explicit goal protection via Protected Core.
    Goals and constraints stored separately and re-asserted after compression.
    """
    
    def __init__(self):
        self.client = Anthropic()
        self.protected_core: Optional[ProtectedCore] = None
    
    def initialize(self, original_goal: str, constraints: List[str]):
        self.protected_core = ProtectedCore(
            original_goal=original_goal,
            current_goal=original_goal,
            hard_constraints=constraints,
            key_decisions=[]
        )
        self.log(f"Protected Core initialized with goal: {original_goal}")
    
    def update_goal(self, new_goal: str, rationale: str = ""):
        self.protected_core.key_decisions.append({
            "decision": f"Updated goal to: {new_goal}",
            "rationale": rationale,
            "timestamp": str(__import__('datetime').datetime.now())
        })
        self.protected_core.current_goal = new_goal
        self.protected_core.timestamp_updated = str(__import__('datetime').datetime.now())
        self.log(f"Goal updated to: {new_goal}")
    
    def compress(self, context: List[Dict], trigger_point: int) -> str:
        """
        Core insight: compress ONLY the conversation halo.
        Protected Core is NEVER compressed, only RE-ASSERTED.
        """
        
        # Separate compressible from protected
        halo_to_compress = context[:max(0, trigger_point - 3)]
        recent_turns = context[max(0, trigger_point - 3):]
        
        # Compress only the halo
        if halo_to_compress:
            halo_text = self._format_context(halo_to_compress)
            halo_summary = self._summarize_halo(halo_text)
        else:
            halo_summary = ""
        
        # Rebuild context: PROTECTED_CORE + HALO_SUMMARY + RECENT_TURNS
        result = self._format_context_with_protected_core(
            halo_summary,
            recent_turns
        )
        
        self.log(f"Protected Core strategy compressed, re-asserted goal and constraints")
        return result
    
    def _format_context_with_protected_core(self, halo_summary: str, recent_turns: List[Dict]) -> str:
        """
        Format context with Protected Core ALWAYS front and center.
        """
        
        decisions_str = "\n".join([
            f"- {d['decision']} (Reason: {d['rationale']})"
            for d in self.protected_core.key_decisions
        ])
        
        result = f"""PROTECTED CORE (AUTHORITATIVE - Never forget these):
================================================
Original Goal: {self.protected_core.original_goal}
Current Goal: {self.protected_core.current_goal}

Hard Constraints (MUST FOLLOW):
{chr(10).join(f'- {c}' for c in self.protected_core.hard_constraints)}

Key Decisions Made:
{decisions_str if decisions_str else '(none yet)'}

================================================

INSTRUCTION: Always prioritize the CURRENT GOAL and HARD CONSTRAINTS.
If there's ambiguity, refer back to this Protected Core.

Previous Conversation Summary:
{halo_summary}

Recent Turns (Raw):
{self._format_context(recent_turns)}
"""
        
        return result
    
    def _summarize_halo(self, text: str) -> str:
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize this conversation history (not the goal, just what happened):\n\n{text}"
                }
            ]
        )
        return response.content[0].text
    
    def _format_context(self, turns: List[Dict]) -> str:
        result = []
        for turn in turns:
            result.append(f"Turn {turn['id']}: {turn['content']}")
        return "\n".join(result)
    
    def name(self) -> str:
        return "Strategy F - Protected Core + Goal Re-assertion"
```

### Strategy G: Hybrid (Agentic Memory + Protected Core)

```python
class StrategyG_Hybrid(CompressionStrategy):
    """
    Combines Strategy D (memory) + Strategy F (protected core).
    Memory for broad recall, Protected Core for goal alignment.
    """
    
    def __init__(self):
        self.protected_core_strategy = StrategyF_ProtectedCore()
        self.memory_strategy = StrategyD_AMEMMemory()
    
    def initialize(self, original_goal: str, constraints: List[str]):
        self.protected_core_strategy.initialize(original_goal, constraints)
        self.memory_strategy.initialize(original_goal, constraints)
    
    def update_goal(self, new_goal: str, rationale: str = ""):
        self.protected_core_strategy.update_goal(new_goal, rationale)
        self.memory_strategy.update_goal(new_goal, rationale)
    
    def compress(self, context: List[Dict], trigger_point: int) -> str:
        """
        Use both strategies:
        1. Protected Core for goal/constraint protection
        2. Memory for flexible recall
        """
        
        # Get Protected Core part
        protected_core_str = self.protected_core_strategy.compress(context, trigger_point)
        
        # Get Memory part (retrieve top memories)
        top_memories = list(self.memory_strategy.memory_notes.values())[-5:]
        memory_str = "Relevant Memories:\n" + "\n".join([
            f"- {m.content}"
            for m in top_memories
        ])
        
        result = f"{protected_core_str}\n{memory_str}"
        self.log("Hybrid strategy: Protected Core + Memory")
        return result
    
    def name(self) -> str:
        return "Strategy G - Hybrid (Memory + Protected Core)"
```

---

## Summary: Which Strategy to Start With?

**Easiest Implementation Order:**
1. **Strategy A** (naive) - simplest
2. **Strategy B** (Codex) - understand what Codex does
3. **Strategy C** (hierarchical) - more complex summarization
4. **Strategy D** (A-MEM) - memory system
5. **Strategy E** (claude-mem) - action-centric
6. **Strategy F** (Protected Core) - **the novel one**
7. **Strategy G** (Hybrid) - builds on F

**For Testing Priority:**
- First: Get A working + baseline established
- Then: Get B working (compare to Codex directly)
- Then: Get F working (the novel strategy)
- Finally: Get D, E, G for comparison

