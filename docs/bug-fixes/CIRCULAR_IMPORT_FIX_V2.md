# Circular Import Fix v2 - Complete Solution

## Problem

Circular import chain:
1. `selective_salience/compressor.py` → imports `SelectiveSalienceStrategy` from `strategies.strategy_h_selective_salience`
2. `strategies/__init__.py` → imports `strategy_b_codex` at top level
3. `strategies/strategy_b_codex.py` → imports `evaluation.token_budget` at top level
4. `evaluation/__init__.py` → imports `harness`
5. `evaluation/harness.py` → imports `strategies.strategy_b_codex` → **CYCLE!**

## Solution Applied

### 1. Made `strategies/__init__.py` imports lazy

**Before:**
```python
from .strategy_b_codex import StrategyB_CodexCheckpoint, create_codex_strategy
from .strategy_h_selective_salience import SelectiveSalienceStrategy
# ... etc
```

**After:**
```python
# Only import base classes (no circular dependencies)
from .strategy_base import CompressionStrategy, Turn, ToolCall, ProbeResults

# Strategy imports - lazy to avoid circular dependencies
# Import directly from their modules when needed
```

### 2. Made token_budget import lazy in `strategy_b_codex.py`

**Before:**
```python
from evaluation.token_budget import TokenBudget, should_compact, BUDGET_8K
```

**After:**
```python
# Lazy import inside __init__ and compress methods
if token_budget is None:
    from evaluation.token_budget import BUDGET_8K
    self.token_budget = BUDGET_8K
```

### 3. Made strategy imports lazy in `harness.py`

**Before:**
```python
from strategies.strategy_b_codex import StrategyB_CodexCheckpoint
from strategies.strategy_h_selective_salience import SelectiveSalienceStrategy
```

**After:**
```python
# Import inside functions where needed
from strategies.strategy_h_selective_salience import SelectiveSalienceStrategy  # Inside function
```

## Result

Now the import chain is:
1. `compressor.py` → imports `SelectiveSalienceStrategy` directly
2. `strategies/__init__.py` → only imports base classes (no cycle)
3. `strategy_h_selective_salience` → no evaluation imports (no cycle)

✅ **No circular import!**

## Testing

```bash
# Test locally
python3 -c "from selective_salience import Instinct8Agent; print('✅ Works!')"

# Install new version
pip install dist/instinct8_agent-0.1.2-py3-none-any.whl --force-reinstall

# Test installed version
instinct8-agent --help
```

## Version

Fixed in version **0.1.2**
