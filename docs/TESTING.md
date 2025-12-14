# Testing and Evaluation Guide

This document explains how to run tests and evaluations for the instinct8 compression evaluation framework.

## Quick Start

```bash
# See all available commands
make help

# Run unit tests
make test

# Quick sanity check (5 samples, ~2 minutes)
make eval-quick

# Compare compression strategies
make eval-compare
```

---

## Test Matrix

Choose the right evaluation for your use case:

| Use Case | Command | Time | Description |
|----------|---------|------|-------------|
| Development testing | `make test` | ~10s | Unit tests only |
| Quick sanity check | `make eval-quick` | ~2m | 5 samples, basic metrics |
| Hierarchical testing | `make eval-hierarchical` | ~5m | Domain/category/episode recall |
| Full benchmark | `make eval-full` | ~30m | All LoCoMo samples |
| Strategy comparison | `make eval-compare` | ~15m | Compare all strategies |
| Publication-ready | `make eval-rigorous` | ~1hr | Multi-run, statistical tests |
| Real binary test | `make eval-binary` | ~10m | Test actual Codex CLI |
| App-server compaction | `make eval-appserver` | ~5m | Test compaction via JSON-RPC |

---

## Evaluation Scripts Reference

### Essential Scripts (Primary Use)

#### 1. `run_eval.py` - Master Evaluation Script
The main entry point for most evaluations.

```bash
# Basic evaluation
python scripts/run_eval.py --dataset locomo

# Compare strategies
python scripts/run_eval.py --compare

# Publication-ready with statistical rigor
python scripts/run_eval.py --rigorous --n-runs 3

# Quick test (5 samples)
python scripts/run_eval.py --dataset locomo --max-samples 5
```

**Strategies:** `amem`, `no_compression`, `recency`, `first_last`, `sliding_window`

#### 2. `run_hierarchical_eval.py` - Hierarchical Depth Evaluation
Tests information retention at different hierarchy levels.

```bash
# Single strategy
python scripts/run_hierarchical_eval.py --strategy amem

# Compare strategies
python scripts/run_hierarchical_eval.py --compare

# Available strategies: amem, codex, no_compression, recency, first_last
```

**Metrics:**
- Domain Recall (high-level summary retention)
- Category Recall (mid-level pattern retention)
- Episode Recall (specific detail retention)
- Hierarchy Drift (degradation at deeper levels)

#### 3. `run_codex_cli_eval.py` - Real Codex Binary Test
Tests against an installed Codex CLI binary.

```bash
# Auto-detect Codex installation
python scripts/run_codex_cli_eval.py

# Specify path
python scripts/run_codex_cli_eval.py --codex-path /path/to/codex
```

#### 4. `run_comparison_eval.py` - A/B Binary Comparison
Compare two Codex binary variants side-by-side.

```bash
# Compare baseline vs variant
python scripts/run_comparison_eval.py --name my-variant

# Auto-build from source
python scripts/run_comparison_eval.py --name my-variant --build-all
```

#### 5. `run_appserver_eval.py` - App-Server Compaction Test
Tests Codex compaction via JSON-RPC app-server protocol.

```bash
# Basic evaluation
python scripts/run_appserver_eval.py

# Custom settings
python scripts/run_appserver_eval.py --token-limit 5000 --turns 15

# Specify binary path
python scripts/run_appserver_eval.py --codex-path /path/to/codex
```

**Metrics:**
- Goal Retention (keyword presence after compaction)
- Constraint Retention (constraint preservation)
- Decision Retention (architectural decisions preserved)
- Compaction Events (number of compaction triggers)

### Deprecated Scripts (Use Alternatives)

| Script | Use Instead |
|--------|-------------|
| `run_rigorous_eval.py` | `run_eval.py --rigorous` |
| `run_locomo_eval.py` | `run_eval.py --dataset locomo` |
| `scripts/archive/run_codex_eval.py` | Kept as baseline reference only |

---

## Understanding Results

### Output Location
All results are saved to `results/` directory:
```
results/
├── evaluation_*.json           # run_eval.py output
├── hierarchical_*.json         # run_hierarchical_eval.py output
├── comparison_*.json           # run_comparison_eval.py output
└── codex_cli_eval_*.json       # run_codex_cli_eval.py output
```

### Key Metrics

#### QA Metrics (LoCoMo Dataset)
| Metric | Description | Good Score |
|--------|-------------|------------|
| F1 | Token overlap | > 0.6 |
| Exact Match | Exact string match | > 0.3 |
| ROUGE-L | Longest common subsequence | > 0.5 |
| BERT-F1 | Semantic similarity | > 0.7 |

#### Compression Metrics
| Metric | Description | Good Score |
|--------|-------------|------------|
| Goal Coherence | Goal retention after compression | > 0.8 |
| Constraint Recall | Constraint preservation | > 0.7 |
| Behavioral Alignment | Decision consistency | > 0.75 |

#### Hierarchical Metrics
| Metric | Description | Good Score |
|--------|-------------|------------|
| Domain Recall | High-level summary retention | > 0.8 |
| Category Recall | Mid-level pattern retention | > 0.7 |
| Episode Recall | Specific detail retention | > 0.6 |
| Hierarchy Drift | Domain - Episode (lower is better) | < 0.15 |

#### Retention Metrics (App-Server Eval)
| Metric | Description | Good Score |
|--------|-------------|------------|
| Goal Retention | Goal keywords preserved after compaction | > 0.7 |
| Constraint Retention | Project constraints preserved | > 0.6 |
| Decision Retention | Architectural decisions preserved | > 0.5 |
| Overall Retention | Average of all retention metrics | > 0.6 |

---

## Unit Tests

### Running Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_hierarchical_eval.py -v

# Quick mode (stop on first failure)
pytest tests/ -v -x --tb=short
```

### Test Coverage
| Test File | Coverage |
|-----------|----------|
| `test_metrics.py` | Basic metric imports |
| `test_strategies.py` | Strategy instantiation |
| `test_hierarchical_eval.py` | Template validation, metric calculation |

---

## Environment Setup

### Requirements
```bash
# Install dependencies
pip install -r requirements.txt

# Required environment variable for API calls
export OPENAI_API_KEY="your-key-here"
```

### Optional: Codex Binary
For `run_codex_cli_eval.py` and `run_comparison_eval.py`:
```bash
# Build from source
cd codex/codex-rs && cargo build --release

# Or install globally
npm install -g @openai/codex
```

---

## Troubleshooting

### Common Issues

**"No module named 'openai'"**
```bash
pip install openai
```

**"OPENAI_API_KEY not set"**
```bash
export OPENAI_API_KEY="sk-..."
```

**"Codex CLI not found"**
```bash
# Check if installed
which codex

# Or specify path
python scripts/run_codex_cli_eval.py --codex-path /path/to/codex
```

**Tests timing out**
```bash
# Reduce sample count
python scripts/run_eval.py --max-samples 3
```
