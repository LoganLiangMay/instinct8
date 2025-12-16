# Codex Functionality Gap Analysis

## What Codex Actually Does

Codex is an **agentic coding assistant** that:

1. **Generates Code**: Takes prompts like "create a FastAPI endpoint" and generates actual code
2. **Executes Commands**: Runs shell commands (e.g., `pip install`, `pytest`)
3. **Modifies Files**: Creates, edits, and patches files
4. **Works Iteratively**: Can iterate on tasks, fix errors, test code
5. **Uses Tools**: Shell, file operations, patches, MCP tools

Example:
```bash
codex exec "create a FastAPI endpoint for user registration"
# → Actually generates code, creates files, runs tests
```

## What Our Current Implementation Does

Our `instinct8` CLI currently:

1. **Only Answers Questions**: Calls `answer_question()` which is a mock
2. **No Code Generation**: Doesn't generate actual code
3. **No Command Execution**: Doesn't run shell commands
4. **No File Operations**: Doesn't create/modify files
5. **Just Q&A**: Returns text responses based on keyword matching

Example:
```bash
instinct8 "create a FastAPI endpoint"
# → Returns: "The current goal is: create a FastAPI endpoint"
# → Does NOT generate code or create files
```

## The Gap

**Our `CodexAgent` is a mock for evaluation purposes**, not a real coding agent.

The `answer_question()` method says:
> "This is a mock implementation that extracts relevant information from the context. In production, this would call an LLM."

## What We Should Implement

To make `instinct8` actually work like Codex, we need:

1. **LLM Integration**: Call OpenAI/Anthropic API to generate code
2. **Code Generation**: Parse LLM responses to extract code blocks
3. **File Operations**: Create/write files with generated code
4. **Command Execution**: Run shell commands (with sandboxing)
5. **Iterative Execution**: Handle multi-turn conversations for complex tasks

## Options

### Option 1: Implement Full Codex Functionality
- Add LLM calls to generate code
- Add file operations
- Add command execution
- Add tool calling support
- **Effort**: High (weeks of work)
- **Value**: Full Codex replacement

### Option 2: Keep Current Mock, Clarify Purpose
- Update docs to clarify this is a **compression strategy wrapper**
- Not a full Codex replacement
- Useful for testing compression strategies
- **Effort**: Low (documentation)
- **Value**: Sets correct expectations

### Option 3: Hybrid - Basic Code Generation
- Add LLM calls to generate code (no execution)
- Return generated code as text
- User can copy/paste and run themselves
- **Effort**: Medium (days of work)
- **Value**: Useful for code generation without execution risk

## Recommendation

**Option 3 (Hybrid)** - Add basic LLM-based code generation:

1. Update `Instinct8Agent.answer_question()` to call LLM
2. Parse code blocks from LLM response
3. Return formatted code (or save to files optionally)
4. Keep compression strategy integration
5. Don't execute commands (safety)

This gives users actual code generation while maintaining our compression strategy focus.
