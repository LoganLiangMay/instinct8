#!/bin/bash
# Example: Using Instinct8 as a Codex replacement

echo "=== Instinct8 as Codex Replacement ==="
echo ""

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY not set"
    echo "Set it with: export OPENAI_API_KEY='your-key'"
    exit 1
fi

echo "1. Basic usage (mimics 'codex exec'):"
echo "   instinct8 'create a FastAPI endpoint'"
echo ""
instinct8 "create a FastAPI endpoint" 2>/dev/null || echo "   (Run: pip install -e . first)"

echo ""
echo "2. With exec command (Codex-compatible):"
echo "   instinct8 exec 'explain this codebase'"
echo ""

echo "3. Set up alias to replace Codex:"
echo "   alias codex=instinct8"
echo "   codex exec 'create a login endpoint'"
echo ""

echo "4. With goal and constraints:"
echo "   instinct8 exec --goal 'Build auth system' --constraints 'Use JWT' 'Hash passwords' 'create login endpoint'"
echo ""

echo "✅ Instinct8 is ready to use as a Codex replacement!"
echo ""
echo "See docs/CODEX_REPLACEMENT.md for full migration guide."
