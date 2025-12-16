# Instinct8 Agent - Quick Start

## 1. Install

```bash
pip install instinct8-agent
```

## 2. Set API Key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 3. Run Instinct8

### File Operations (Default)

```bash
instinct8
```

File operations work immediately:
- `review my files` - Read files
- `create hello.py` - Create files  
- `edit main.py` - Edit files

### Command Execution (Optional)

```bash
instinct8 --allow-execution
```

Now you can execute commands:
- `run npm install` - Run shell commands
- `execute python test.py` - Execute scripts

## Example

```bash
$ instinct8 --allow-execution

instinct8> create a FastAPI login endpoint
✅ Created app.py

instinct8> run pip install fastapi
✅ Installed dependencies

instinct8> review my code
📄 FastAPI login endpoint with JWT auth
```

**Done!** Instinct8 remembers your goals even in long conversations.
