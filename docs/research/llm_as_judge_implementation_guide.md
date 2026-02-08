# LLM-as-Judge Implementation Guide for Strategy H

**Purpose:** Comprehensive breakdown of how to implement LLM-as-Judge evaluation for Selective Salience Compression (Strategy H)

**Platform:** OpenAI API (GPT-4o, GPT-4 Turbo, GPT-4o-mini)

**No Code:** This guide focuses on design principles, process, and best practices

---

## Table of Contents

1. [Core Design Principles](#core-design-principles)
2. [Rubric Design](#rubric-design)
3. [Prompt Engineering](#prompt-engineering)
4. [Judge Selection](#judge-selection)
5. [Evaluation Process](#evaluation-process)
6. [Quality Assurance](#quality-assurance)
7. [Calibration & Validation](#calibration--validation)
8. [Scaling Considerations](#scaling-considerations)
9. [Bias Mitigation](#bias-mitigation)
10. [Iteration & Improvement](#iteration--improvement)

---

## Core Design Principles

### Principle 1: Clarity Over Cleverness

**What:** Make the evaluation task as explicit and unambiguous as possible.

**Why:** LLMs perform best when they understand exactly what's expected. Ambiguity leads to inconsistent evaluations.

**How:**
- Define every term explicitly (what is "goal-critical"?)
- Provide concrete examples of good vs bad salience
- Use numbered criteria with clear scoring scales
- Avoid abstract concepts without definitions

### Principle 2: Structured Output

**What:** Require judges to output evaluations in a structured format (JSON, XML, or strict template).

**Why:** Structured output ensures:
- Consistent format across evaluations
- Easy parsing and aggregation
- Less ambiguity in interpretation
- Better error detection

**How:**
- Define exact JSON schema for evaluation output
- Include required fields and optional fields
- Specify data types and ranges
- Provide example outputs

### Principle 3: Multi-Judge Consensus

**What:** Use multiple judge models and aggregate their scores.

**Why:** 
- Reduces variance from individual model quirks
- Catches errors (if one judge is way off, others catch it)
- Provides confidence intervals
- More reliable than single-judge evaluations

**How:**
- Use 3-5 different judge models
- Aggregate scores (mean, median, or weighted)
- Track inter-judge agreement
- Flag evaluations with high disagreement for review

### Principle 4: Calibration First

**What:** Validate judges against known ground truth before scaling.

**Why:** You need to know if judges are accurate before trusting them at scale.

**How:**
- Start with 5-10 templates with human-annotated ground truth
- Run judges on these templates
- Measure correlation with ground truth
- Only scale if correlation is acceptable (>0.75)

### Principle 5: Iterative Refinement

**What:** Continuously improve rubric and prompts based on evaluation results.

**Why:** Initial rubrics are rarely perfect. You'll discover edge cases and ambiguities.

**How:**
- Track evaluation quality metrics
- Identify common failure modes
- Update rubric to address failures
- Re-calibrate periodically

---

## Rubric Design

### Step 1: Define Evaluation Dimensions

**What to Evaluate:**

1. **Item-Level Evaluation** (for each extracted salience item)
   - Goal Relevance: Does this directly relate to achieving the goal?
   - Constraint Criticality: Is this a hard constraint that must be preserved?
   - Decision Importance: Is this a key decision that affects future actions?
   - Fact Necessity: Will this fact be needed for future actions?
   - Verbatim Accuracy: Is this quoted correctly from the conversation?

2. **Set-Level Evaluation** (for the entire salience set)
   - Completeness: Are all critical items included?
   - Precision: Are irrelevant items excluded?
   - Coverage: Do items cover all important categories (goals, constraints, decisions)?
   - Redundancy: Are there duplicate or overlapping items?

3. **Context-Level Evaluation** (for the compression as a whole)
   - Goal Coherence Preservation: Will this maintain goal alignment?
   - Information Loss: What critical information was lost?
   - Noise Introduction: What irrelevant information was added?

### Step 2: Create Scoring Scales

**For Each Dimension:**

- **5-Point Scale** (recommended):
  - 5 = Excellent/Critical (must preserve)
  - 4 = Good/Important (should preserve)
  - 3 = Moderate/Useful (nice to have)
  - 2 = Low/Minor (probably not needed)
  - 1 = Poor/Irrelevant (definitely not needed)

- **Binary Scale** (for simpler dimensions):
  - 1 = Salient (should be preserved)
  - 0 = Not Salient (can be compressed)

**Why 5-Point Scale:**
- Provides nuance (not just yes/no)
- Allows for borderline cases
- Standard in evaluation research
- Easy to aggregate and interpret

### Step 3: Provide Examples

**Include in Rubric:**

1. **Example of Perfect Salience** (score 5)
   - Show what a perfectly extracted item looks like
   - Explain why it's perfect

2. **Example of Good Salience** (score 4)
   - Show what a good but not perfect item looks like
   - Explain what makes it good but not perfect

3. **Example of Poor Salience** (score 2)
   - Show what a poor extraction looks like
   - Explain why it's poor

4. **Example of Irrelevant Salience** (score 1)
   - Show what should NOT be extracted
   - Explain why it's irrelevant

**Why Examples Matter:**
- LLMs learn from examples more than definitions
- Examples reduce ambiguity
- Examples help calibrate judges
- Examples serve as reference during evaluation

### Step 4: Define Edge Cases

**Common Edge Cases to Address:**

1. **Implicit Constraints**
   - How to evaluate when constraint is implied but not stated?
   - Should judges infer implicit constraints?

2. **Goal Evolution**
   - What if goal changes mid-conversation?
   - Should both original and evolved goals be preserved?

3. **Context-Dependent Salience**
   - What if something is salient now but won't be later?
   - How to evaluate time-dependent salience?

4. **Partial Quotes**
   - What if model extracts part of a statement?
   - Is partial extraction acceptable?

5. **Paraphrased Quotes**
   - What if model paraphrases instead of quoting verbatim?
   - How much paraphrasing is acceptable?

**How to Handle:**
- Explicitly define how to handle each edge case in rubric
- Provide examples of edge cases
- Include decision rules (if X, then Y)

---

## Prompt Engineering

### Component 1: Role Definition

**What:** Tell the judge what role they're playing.

**Example:**
"You are an expert evaluator assessing whether an AI model correctly identified goal-critical information during context compression. Your task is to evaluate the quality of salience extraction."

**Why:** 
- Sets context for the evaluation
- Helps judge understand their role
- Reduces role confusion

### Component 2: Task Definition

**What:** Clearly explain what the judge needs to do.

**Example:**
"Evaluate each item in the model's extracted salience set. For each item, determine:
1. Is this item goal-critical?
2. Is this item a constraint, decision, fact, or goal?
3. Is this item quoted accurately?
4. Should this item have been extracted?"

**Why:**
- Makes the task explicit
- Reduces ambiguity
- Guides judge's thinking

### Component 3: Context Provision

**What:** Provide all necessary context for evaluation.

**Must Include:**
- Original goal (what the agent is trying to achieve)
- Constraints (hard requirements)
- Full conversation context (what was said)
- Model's extracted salience (what model thinks is important)
- Compression point (when compression happened)

**Why:**
- Judges need full context to evaluate accurately
- Missing context leads to poor evaluations
- Context helps judges understand goal relevance

### Component 4: Rubric Integration

**What:** Embed the rubric directly in the prompt.

**How:**
- Include all evaluation criteria
- Include scoring scales
- Include examples
- Include edge case handling

**Why:**
- Judges need rubric accessible during evaluation
- Reduces need to "remember" criteria
- Ensures consistency

### Component 5: Output Format Specification

**What:** Specify exactly how judges should format their output.

**Must Include:**
- Exact JSON schema
- Required fields
- Optional fields
- Data types
- Example output

**Why:**
- Ensures parseable output
- Reduces format errors
- Makes aggregation easier

### Component 6: Chain-of-Thought Reasoning

**What:** Ask judges to explain their reasoning.

**Example:**
"For each item, provide:
- Score (1-5)
- Reasoning (why this score)
- Category (goal/constraint/decision/fact)
- Confidence (high/medium/low)"

**Why:**
- Helps identify judge errors
- Provides transparency
- Useful for rubric refinement
- Builds trust in evaluations

---

## Judge Selection

### OpenAI Model Considerations

**Available OpenAI Models for Evaluation:**

1. **GPT-4o** (Recommended for highest quality)
   - Best reasoning capability
   - Latest OpenAI model (2024)
   - Multimodal capabilities (if needed)
   - Higher cost but best accuracy

2. **GPT-4 Turbo** (Recommended for balanced quality/cost)
   - Strong reasoning capability
   - Proven reliability
   - Good balance of quality and cost
   - Widely used in production

3. **GPT-4o-mini** (Recommended for cost-effective evaluation)
   - Good reasoning capability
   - Significantly cheaper than GPT-4o
   - Fast response times
   - Good for high-volume evaluations

4. **GPT-3.5 Turbo** (Backup/fallback only)
   - Very fast and cheap
   - Lower quality reasoning
   - Use only for simple evaluations or when cost is critical

### Criteria for Judge Models

**1. Reasoning Capability**
- Must be able to understand complex evaluation tasks
- Must be able to reason about goal relevance
- Must be able to identify subtle distinctions

**Recommended Models:**
- GPT-4o (best reasoning, OpenAI's latest)
- GPT-4 Turbo (strong reasoning, proven)
- GPT-4o-mini (good balance, cost-effective)

**2. Consistency**
- Must produce similar scores for similar inputs
- Must not have high variance
- Must be reliable

**How to Test:**
- Run same evaluation multiple times
- Measure score variance
- Prefer models with low variance

**3. Cost-Effectiveness**
- Must be affordable at scale
- Balance cost vs quality

**Considerations:**
- Use cheaper models for simple evaluations
- Use expensive models for complex evaluations
- Consider caching evaluations

**4. Speed**
- Must complete evaluations in reasonable time
- Must not bottleneck evaluation pipeline

**Considerations:**
- API latency matters
- Batch processing helps
- Parallel evaluation helps

### Recommended Judge Panel

**Primary Judges (3 models):**
1. GPT-4o (highest quality, OpenAI's latest multimodal model)
2. GPT-4 Turbo (high quality, proven reliability)
3. GPT-4o-mini (good quality, cost-effective)

**Why This Mix:**
- Same model family but different capabilities (reduces some shared biases)
- Different cost points (allows optimization)
- Different strengths (complementary)
- All OpenAI models (consistent API, easier integration)

**Backup Judges (optional):**
- GPT-3.5 Turbo (very fast, lower quality, very cheap)
- GPT-4 (older but still reliable)

**When to Use:**
- GPT-4o-mini: For rapid iteration, simple evaluations, cost-sensitive scenarios
- GPT-4 Turbo: For standard evaluations, balanced quality/cost
- GPT-4o: For complex evaluations, highest accuracy needed

---

## Evaluation Process

### Phase 1: Preparation

**Step 1: Template Selection**
- Select templates to evaluate
- Ensure diversity (different task types, complexity levels)
- Include edge cases

**Step 2: Context Preparation**
- Extract conversation context
- Extract original goal and constraints
- Extract model's salience set
- Format for prompt

**Step 3: Prompt Assembly**
- Assemble prompt from components
- Include rubric, examples, context
- Validate prompt completeness

### Phase 2: Execution

**Step 1: Single-Judge Evaluation**
- Send prompt to first judge
- Receive evaluation
- Parse structured output
- Validate output format

**Step 2: Multi-Judge Evaluation**
- Repeat for each judge model
- Collect all evaluations
- Track which judge evaluated what

**Step 3: Error Handling**
- Detect malformed outputs
- Retry failed evaluations
- Log errors for analysis

### Phase 3: Aggregation

**Step 1: Score Aggregation**
- Calculate mean/median scores across judges
- Calculate confidence intervals
- Identify high-disagreement cases

**Step 2: Metric Calculation**
- Calculate precision estimate (from noise level)
- Calculate recall estimate (from completeness)
- Calculate F1 estimate
- Calculate category-specific metrics

**Step 3: Quality Checks**
- Flag evaluations with high judge disagreement
- Flag evaluations with missing required fields
- Flag evaluations with suspicious patterns

### Phase 4: Analysis

**Step 1: Individual Item Analysis**
- Review item-level scores
- Identify patterns (what gets high/low scores)
- Identify failure modes

**Step 2: Set-Level Analysis**
- Review completeness scores
- Review noise level scores
- Identify missing critical items
- Identify irrelevant items

**Step 3: Comparative Analysis**
- Compare with ground truth (if available)
- Compare across templates
- Compare across compression points

---

## Quality Assurance

### Checkpoint 1: Output Validation

**What to Check:**
- Is output valid JSON?
- Are all required fields present?
- Are scores within valid ranges (1-5)?
- Is reasoning provided?
- Are examples properly formatted?

**Action if Failed:**
- Retry evaluation
- Flag for manual review
- Log error for analysis

### Checkpoint 2: Consistency Checks

**What to Check:**
- Do judges agree on scores? (inter-judge agreement)
- Are scores consistent across similar items?
- Are there suspicious patterns (all 5s, all 1s)?

**Action if Failed:**
- Flag for manual review
- Investigate rubric ambiguity
- Consider rubric refinement

### Checkpoint 3: Completeness Checks

**What to Check:**
- Did judge evaluate all items?
- Did judge provide reasoning for all scores?
- Did judge identify missing items?

**Action if Failed:**
- Request re-evaluation
- Flag incomplete evaluations
- Investigate why incomplete

### Checkpoint 4: Reasonableness Checks

**What to Check:**
- Are scores reasonable given context?
- Does reasoning match scores?
- Are identified missing items actually missing?

**Action if Failed:**
- Flag for manual review
- Investigate judge errors
- Consider judge replacement

---

## Calibration & Validation

### Calibration Process

**Step 1: Ground Truth Creation**
- Select 5-10 templates
- Have humans annotate ground truth salience
- Measure inter-annotator agreement
- Build consensus ground truth

**Step 2: Judge Calibration**
- Run judges on calibration templates
- Compare judge scores with ground truth
- Calculate correlation coefficients
- Identify judge biases

**Step 3: Rubric Refinement**
- Analyze disagreements
- Identify rubric ambiguities
- Refine rubric based on findings
- Re-calibrate judges

**Step 4: Threshold Setting**
- Determine acceptable correlation (>0.75)
- Set quality thresholds
- Define when to trust judges vs use ground truth

### Validation Process

**Ongoing Validation:**
- Periodically re-run judges on calibration templates
- Track correlation over time
- Detect judge drift
- Re-calibrate if needed

**Cross-Validation:**
- Use different templates for calibration vs evaluation
- Ensure judges generalize
- Avoid overfitting to calibration set

---

## Scaling Considerations

### Challenge 1: Cost Management

**Problem:** LLM-as-Judge can be expensive at scale.

**OpenAI Pricing Considerations (as of 2025):**
- GPT-4o: ~$5-15 per 1M input tokens, ~$15-60 per 1M output tokens
- GPT-4 Turbo: ~$10 per 1M input tokens, ~$30 per 1M output tokens
- GPT-4o-mini: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- GPT-3.5 Turbo: ~$0.50 per 1M input tokens, ~$1.50 per 1M output tokens

**Solutions:**
- Use cheaper models for simple evaluations
- Cache evaluations (don't re-evaluate same items)
- Use GPT-4o-mini for initial screening, GPT-4o for final evaluation
- Optimize prompts to reduce token usage
- Use structured outputs to reduce parsing overhead

**Cost Optimization Strategy:**
- Tier 1: GPT-4o-mini for initial screening and simple evaluations
- Tier 2: GPT-4 Turbo for standard evaluation (balanced quality/cost)
- Tier 3: GPT-4o for complex/ambiguous cases requiring highest accuracy

**Token Optimization:**
- Keep prompts concise but complete
- Use system messages efficiently
- Set appropriate `max_tokens` (don't request more than needed)
- Consider using `response_format` for structured outputs (reduces parsing)

### Challenge 2: Latency Management

**Problem:** LLM evaluations can be slow.

**Solutions:**
- Parallel evaluation (evaluate multiple items simultaneously)
- Async evaluation (don't block on evaluations)
- Pre-evaluation (evaluate common patterns ahead of time)
- Caching (cache evaluations for identical inputs)

### Challenge 3: Quality Maintenance

**Problem:** Quality may degrade at scale.

**Solutions:**
- Regular quality audits
- Spot-check evaluations
- Compare with ground truth periodically
- Monitor quality metrics

### Challenge 4: Error Handling

**Problem:** Errors increase at scale.

**Solutions:**
- Robust error handling
- Automatic retries
- Fallback to simpler evaluation
- Human review for edge cases

---

## Bias Mitigation

### Common Biases in LLM Judges

**1. Position Bias**
- Judges may favor items at beginning/end of list
- **Mitigation:** Randomize item order

**2. Length Bias**
- Judges may favor longer items
- **Mitigation:** Normalize for length in rubric

**3. Recency Bias**
- Judges may favor recent information
- **Mitigation:** Explicitly instruct to evaluate based on goal relevance, not recency

**4. Confirmation Bias**
- Judges may favor items that confirm expectations
- **Mitigation:** Provide counter-examples in rubric

**5. Model-Specific Biases**
- Different models have different biases
- **Mitigation:** Use diverse judge panel

### Mitigation Strategies

**1. Rubric Design**
- Explicitly address common biases
- Provide examples that counteract biases
- Include instructions to avoid biases

**2. Multi-Judge Consensus**
- Use diverse judge models
- Aggregate scores (reduces individual biases)
- Track bias patterns

**3. Calibration**
- Identify biases during calibration
- Adjust rubric to counteract biases
- Monitor for bias drift

**4. Human Oversight**
- Periodically review evaluations
- Identify bias patterns
- Refine rubric based on findings

---

## Iteration & Improvement

### Feedback Loop

**Step 1: Collect Feedback**
- Track evaluation quality metrics
- Collect human feedback on evaluations
- Identify common failure modes
- Document edge cases

**Step 2: Analyze Patterns**
- What types of items get mis-evaluated?
- What rubric ambiguities cause errors?
- What judge behaviors are problematic?

**Step 3: Refine Rubric**
- Address identified ambiguities
- Add examples for common failures
- Clarify edge case handling
- Update scoring criteria

**Step 4: Re-Calibrate**
- Re-run calibration on updated rubric
- Measure improvement
- Iterate until quality acceptable

### Continuous Improvement

**Metrics to Track:**
- Inter-judge agreement (should be >0.75)
- Correlation with ground truth (should be >0.75)
- Evaluation consistency (low variance)
- Error rates (should be <5%)

**Review Cadence:**
- Weekly: Review quality metrics
- Monthly: Analyze failure modes
- Quarterly: Major rubric refinement
- Annually: Full re-calibration

---

## Implementation Roadmap

### Week 1-2: Design & Prototype
- Design initial rubric
- Create example prompts
- Test with 2-3 templates
- Refine based on initial results

### Week 3-4: Calibration
- Create ground truth for 5-10 templates
- Run judges on calibration set
- Measure correlation
- Refine rubric based on findings

### Week 5-6: Validation
- Test on new templates
- Measure generalization
- Identify remaining issues
- Finalize rubric

### Week 7+: Scale
- Deploy to all templates
- Monitor quality metrics
- Iterate based on feedback
- Maintain calibration

---

## Key Success Criteria

**Judge Quality:**
- Inter-judge agreement >0.75
- Correlation with ground truth >0.75
- Error rate <5%
- Consistent evaluations

**Evaluation Quality:**
- Complete evaluations (>95%)
- Valid outputs (>98%)
- Reasonable scores (no obvious errors)
- Useful reasoning provided

**Process Quality:**
- Scalable (can evaluate 100+ templates)
- Cost-effective (<$1 per template with GPT-4o-mini, <$3 with GPT-4 Turbo)
- Fast (<30 seconds per template with GPT-4o-mini, <60 seconds with GPT-4o)
- Reliable (<1% failure rate)
- Rate limit compliant (respects OpenAI API limits)

## OpenAI-Specific Implementation Notes

### API Configuration

**Authentication:**
- Use OpenAI API key from environment variable
- Never commit API keys to version control
- Use different keys for different environments (dev/staging/prod)

**API Client Setup:**
- Use official `openai` Python library
- Configure with appropriate timeout values
- Set up retry logic for transient failures
- Monitor API usage and costs

### Structured Outputs (Recommended)

**Why Use Structured Outputs:**
- OpenAI supports JSON mode and function calling for structured outputs
- Reduces parsing errors
- Ensures consistent format
- More reliable than parsing free-form JSON

**Implementation Approach:**
- Use `response_format={"type": "json_object"}` for JSON mode
- Or use function calling to define exact schema
- Specify JSON schema in prompt for best results

### Rate Limit Management

**Understanding Limits:**
- Rate limits are per model and per tier
- Limits include: requests per minute (RPM), tokens per minute (TPM)
- Different models have different limits
- Check your tier limits in OpenAI dashboard

**Best Practices:**
- Monitor your usage
- Implement exponential backoff
- Use async requests to maximize throughput
- Consider upgrading tier if hitting limits
- Distribute load across multiple API keys if needed

### Error Handling

**Common OpenAI API Errors:**
- Rate limit errors (429) → exponential backoff
- Invalid request errors (400) → validate inputs
- Authentication errors (401) → check API key
- Server errors (500/502/503) → retry with backoff

**Error Handling Strategy:**
- Implement retry logic with exponential backoff
- Log all errors for analysis
- Have fallback strategy (e.g., use cheaper model)
- Alert on persistent failures

### Cost Monitoring

**Track Costs:**
- Monitor token usage per evaluation
- Track costs per template
- Set up budget alerts
- Use OpenAI's usage dashboard

**Cost Optimization Tips:**
- Use GPT-4o-mini for most evaluations
- Only use GPT-4o for complex cases
- Cache identical evaluations
- Optimize prompts to reduce tokens
- Set appropriate `max_tokens` (don't request more than needed)

---

## Common Pitfalls to Avoid

**1. Over-Complex Rubrics**
- Too many criteria confuse judges
- Keep rubric focused on key dimensions

**2. Under-Specified Prompts**
- Ambiguity leads to inconsistent evaluations
- Be explicit about everything

**3. Single-Judge Evaluations**
- High variance, unreliable
- Always use multiple judges

**4. Skipping Calibration**
- Don't trust judges without validation
- Always calibrate against ground truth

**5. Ignoring Bias**
- Biases compound at scale
- Actively mitigate biases

**6. No Iteration**
- Initial rubrics are rarely perfect
- Continuously refine based on feedback

---

## Conclusion

LLM-as-Judge is a powerful evaluation method when implemented carefully. The key is:

1. **Clear rubric design** with examples and edge cases
2. **Structured prompts** with explicit instructions
3. **Multi-judge consensus** for reliability
4. **Calibration** against ground truth
5. **Continuous iteration** based on feedback

Follow these principles, and you'll have a scalable, reliable evaluation system for Strategy H.

---

*Document created: 2025-01-XX*  
*Last updated: 2025-01-XX*

