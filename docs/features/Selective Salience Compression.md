# **Selective Salience Compression**

### ***(a.k.a. “Agent-as-Judge” Compression)***

## **🔹 Brief: How It Works (High-Level)**

Selective Salience Compression asks the *agent itself* to decide which parts of the conversation matter for staying aligned with the user’s goal. Instead of summarizing everything equally, the system first extracts a set of **salient facts**—goal-relevant statements, constraints, decisions, tool outputs—and preserves those verbatim. Everything else (chit-chat, scaffolding, intermediate thinking) is compressed into a lightweight summary.

This method tests whether a model can reliably identify “what will matter later” and preserve it — separating **signal** from **noise** before compression.

---

# **🔹 More Detailed Explanation (with mechanics)**

### **1\. The Core Idea**

Selective Salience Compression assumes:

* Not all tokens are equally important  
* Humans naturally remember the *important bits*  
* The agent might be able to *judge importance* too

Rather than compressing a block of text directly, you:

1. **Ask the model to extract only the key information** relevant to the goal.  
2. **Preserve those key bits verbatim**, never summarized.  
3. Summarize the *rest* of the block more aggressively.

This creates a two-part memory:

* **Salience Set (verbatim)** → “these details matter”  
* **Background Summary (compressed)** → “everything else”

---

### **2\. Why This Is Distinct From Protected Core**

* *Protected Core* relies on **your schema** for what to protect.  
* *Selective Salience* relies on **the model’s own salience evaluation**.

This makes it:

* More adaptive  
* More flexible  
* More error-prone  
* More interesting to measure

It tests:  
 **Can a model reliably identify the goal-critical information it will need later?**

---

# **🔹 The Pipeline (Step-by-Step)**

### **Step 1 — Identify Salient Information**

You prompt the model:

“From the following text, extract the information that will directly impact the agent’s ability to achieve the user’s goal. Include goals, constraints, decisions, important facts, and tool outputs. Do **not** summarize—quote exactly.”

This produces the **Salience Set**.

---

### **Step 2 — Compress Everything Else**

Prompt:

“Now summarize the remaining content into the shortest coherent form possible. Do not duplicate information contained in the salience list.”

This creates the **Background Summary**.

---

### **Step 3 — Rebuild Context**

At the next turn, the context becomes:

`SYSTEM MESSAGE (as usual)`  
`SALIENT INFORMATION (verbatim)`  
`BACKGROUND SUMMARY (compressed)`  
`RECENT MESSAGES`  
`CURRENT TASK`

---

### **Step 4 — Repeat at Each Compression Trigger**

The salience vector grows or shrinks depending on the model’s extraction at each step.

---

# **🔹 Detailed Example**

Let’s simulate a small example to show why this method matters.

---

## **Context Before Compression**

User \+ agent have been working for 15 minutes on designing a system with this conversation fragment:

`User: Let's choose PostgreSQL over MongoDB because we need strong relational guarantees.`  
`Agent: Agreed. That means we can use row-level locking to handle the concurrency issue.`  
`User: Also, we absolutely must keep the latency under 150ms for the regional routing service.`  
`Agent: Good point. We'll need connection pooling and maybe read replicas.`  
`User: One more thing — we cannot use AWS Aurora for this due to compliance issues.`  
`Then they discuss implementation details, off-topic tangents, minor reasoning steps, and re-explanations.`

---

# **🔹 What Selective Salience Extraction Produces**

### **Salience Set (Verbatim Preserved)**

`- "Choose PostgreSQL over MongoDB because we need strong relational guarantees."`  
`- "We absolutely must keep the latency under 150ms for the regional routing service."`  
`- "We cannot use AWS Aurora for this due to compliance issues."`  
`- "Row-level locking may be required to handle concurrency."`

This preserves:  
 ✔ key choices  
 ✔ constraints  
 ✔ rationales  
 ✔ requirements

---

### **Background Summary (Compressed)**

`Earlier discussion included options for implementation and performance tuning.`  
`The agent and user explored several minor alternatives but committed to PostgreSQL.`  
`General architectural considerations were discussed but do not affect the core decisions.`

This removes:

* chit-chat  
* redundant restatements  
* isolated reasoning hops  
* explorations that don’t affect final decisions

---

# **🔹 Now Rebuild the Context**

Next prompt becomes:

`SYSTEM: (same as usual)`

`SALIENT INFORMATION:`  
`- Choose PostgreSQL over MongoDB because we need strong relational guarantees.`  
`- We absolutely must keep the latency under 150ms for the regional routing service.`  
`- We cannot use AWS Aurora for this due to compliance issues.`  
`- Row-level locking may be required to handle concurrency.`

`BACKGROUND SUMMARY:`  
`(Essentially non-critical context, compressed)`

`RECENT MESSAGES:`  
`(last 3-5 messages)`

---

# **🔹 Why This Method Is Unique**

### **1\. It tests model judgment**

Instead of telling the agent what matters, it must *infer* what matters.

Some failures you might see:

* The model misses a constraint

* Or includes irrelevant things as “salient”

* Or loses a subtle but critical detail

This makes it a *real* benchmark for salience detection, which is a frontier capability.

---

### **2\. It simulates human-like memory**

People remember:

* The decisions

* The constraints

* The “why”  
   …not every sentence of the conversation.

Agents need that too.

---

### **3\. It allows compression without losing mission-critical info**

It reduces token usage *but* preserves:

* goals

* constraints

* decisions

This is exactly what you’re measuring in Instinct8.

---

# **🔹 Potential Variants (Bonus)**

You can test sub-flavors:

1. **Conservative Salience Extraction**

   * Keep more details in the verbatim set.

2. **Aggressive Salience Extraction**

   * Only preserve the top 1–3 key facts.

3. **Model-Filtered Salience Ranking**

   * Ask model to score importance 1–10.

4. **Top-K Salience Compression**

   * Keep only K salient facts.

This gives richness to your experimental matrix.

