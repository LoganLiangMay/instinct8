# v1-core: Python Selective Salience

**Branch:** `main`
**Status:** Active, v0.4.2, published to PyPI
**Package:** `instinct8-agent`

## Description

Python-based context compression middleware with 9+ strategies for preventing goal drift in long-running LLM agent conversations. This is the primary production version of Instinct8.

## Key Directories

- `selective_salience/` — Core Python package
- `strategies/` — 9+ compression strategy implementations
- `evaluation/` — Evaluation framework with LLM-as-judge metrics
- `templates/` — 22 conversation templates for testing
- `tests/` — Unit tests

## Key Features

- Selective Salience Compression (Strategy H)
- Protected Core + Goal Re-assertion (Strategy F)
- Codex-compatible CLI (`instinct8` command)
- Interactive agent mode (`instinct8-agent` command)
- LLM-as-judge evaluation with 3 core metrics
- Published to PyPI as `instinct8-agent`

## Quick Start

```bash
pip install instinct8-agent
export OPENAI_API_KEY="your-key"
instinct8 "Hello, what can you do?"
```

## Related Branches

- `feature/package-selective-salience` — PyPI packaging (partially merged)
- `feature/pr01-selective-salience` — PR#01 enhancements, presentations
- `feature/strategy-i-hybrid-implementation` — Strategy I (A-MEM + Protected Core)
- `feature/h-mem` — Hierarchical Memory (H-MEM) implementation
- `feature/instinct8-goal-preservation` — Goal preservation framework (merged)
