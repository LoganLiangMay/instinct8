# Context Compression Strategies
# This package contains implementations of different compression strategies
# for long-running LLM agents.

from .strategy_base import CompressionStrategy, Turn, ToolCall, ProbeResults
from .strategy_b_codex import StrategyB_CodexCheckpoint, create_codex_strategy
from .strategy_d_amem import StrategyD_AMemStyle, create_amem_strategy
from .strategy_g_hybrid import StrategyG_Hybrid, create_hybrid_strategy
from .strategy_h_selective_salience import SelectiveSalienceStrategy

__all__ = [
    # Base
    "CompressionStrategy",
    "Turn",
    "ToolCall",
    "ProbeResults",
    # Strategy B - Codex
    "StrategyB_CodexCheckpoint",
    "create_codex_strategy",
    # Strategy D - A-MEM
    "StrategyD_AMemStyle",
    "create_amem_strategy",
    # Strategy G - Hybrid GraphRAG
    "StrategyG_Hybrid",
    "create_hybrid_strategy",
    # Strategy H - Selective Salience
    "SelectiveSalienceStrategy",
]

