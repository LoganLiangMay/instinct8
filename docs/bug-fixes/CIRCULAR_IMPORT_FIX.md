# Circular Import Fix

## Problem

Circular import between:
- `evaluation/__init__.py` → `harness` → `strategies.strategy_b_codex` → `evaluation.token_budget`

## Solution Applied

### 1. Made strategy imports lazy in `harness.py`

**Before:**
```python
from strategies.strategy_b_codex import StrategyB_CodexCheckpoint
from strategies.strategy_h_selective_salience import SelectiveSalienceStrategy
```

**After:**
```python
# Removed top-level imports
# Import inside functions where needed:
from strategies.strategy_h_selective_salience import SelectiveSalienceStrategy  # Inside function
```

### 2. Made token_budget import lazy in `strategy_b_codex.py`

**Before:**
```python
from evaluation.token_budget import TokenBudget, should_compact, BUDGET_8K
```

**After:**
```python
# Removed top-level import
# Import inside __init__ and compress methods where needed
```

## Testing

After rebuilding, test with:
```bash
pip install dist/instinct8_agent-0.1.1-py3-none-any.whl --force-reinstall
instinct8-agent --help
```

This should work without circular import errors.

## Version

Fixed in version **0.1.1**
