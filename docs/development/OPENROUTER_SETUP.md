# Using OpenRouter with Context Compression Evaluation

This project now supports both **Anthropic API** and **OpenRouter API** for running evaluations.

## Quick Setup

### Option 1: Use OpenRouter (Recommended for cost savings)

1. **Get an OpenRouter API key:**
   - Sign up at https://openrouter.ai
   - Get your API key from the dashboard

2. **Set the environment variable:**
   ```bash
   export OPENROUTER_API_KEY="your-openrouter-api-key-here"
   ```

3. **Optional: Set the model** (defaults to Claude 3.5 Sonnet):
   ```bash
   export OPENROUTER_MODEL="anthropic/claude-3.5-sonnet"
   ```

   Other popular models:
   - `anthropic/claude-3.5-sonnet` (default)
   - `anthropic/claude-3-opus`
   - `openai/gpt-4-turbo`
   - `google/gemini-pro-1.5`
   - See full list: https://openrouter.ai/models

4. **Run the evaluation:**
   ```bash
   source venv/bin/activate
   python3 -m evaluation.harness \
     --template templates/research-synthesis-001.json \
     --trials 3 \
     --output results/baseline_results.json
   ```

### Option 2: Use Anthropic API (Original)

1. **Set the environment variable:**
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
   ```

2. **Run the evaluation** (same command as above)

## How It Works

The system automatically detects which API to use:
- If `OPENROUTER_API_KEY` is set → Uses OpenRouter
- Else if `ANTHROPIC_API_KEY` is set → Uses Anthropic
- Else → Defaults to Anthropic (will fail without key)

## Model Selection

### OpenRouter Models
OpenRouter uses model IDs like `anthropic/claude-3.5-sonnet`. Set via:
```bash
export OPENROUTER_MODEL="anthropic/claude-3.5-sonnet"
```

### Anthropic Models
Anthropic uses model names like `claude-sonnet-4-20250514`. These are hardcoded in the code.

## Cost Comparison

OpenRouter often provides:
- Lower costs for the same models
- Access to multiple providers (Anthropic, OpenAI, Google, etc.)
- Unified API for switching models easily

## Troubleshooting

**Error: "OPENROUTER_API_KEY not set"**
- Make sure you've exported the environment variable
- Check: `echo $OPENROUTER_API_KEY`

**Error: "openai package required"**
- Install: `pip install openai`

**Error: "Could not resolve authentication"**
- Verify your API key is correct
- Make sure the environment variable is set in the same shell session

## Example: Running with OpenRouter

```bash
# Set your OpenRouter key
export OPENROUTER_API_KEY="sk-or-v1-..."

# Optional: Choose a different model
export OPENROUTER_MODEL="anthropic/claude-3-opus"

# Run evaluation
cd /Users/isaac/Documents/Instinct8/instinct8
source venv/bin/activate
python3 -m evaluation.harness \
  --template templates/research-synthesis-001.json \
  --trials 3 \
  --output results/openrouter_results.json
```

The evaluation will automatically use OpenRouter and the specified model!

