# Changelog

All notable changes to Instinct8 Agent will be documented in this file.

## [0.4.1] - 2024-12-14

### Fixed
- **Tips Header**: Removed semicolon from "Tips:" header (now just "Tips") to fix spacing

## [0.4.0] - 2024-12-14

### Fixed
- **Tips Box Bullet**: Changed from Unicode bullet "•" to ASCII dash "-" to avoid wide character rendering issues
- **Line Formatting**: Added guaranteed exact-length line formatting using string slicing

### Changed
- **Bullet Character**: Now uses "-" instead of "•" for better terminal compatibility

## [0.3.9] - 2024-12-14

### Fixed
- **Tips Box Spacing**: Completely rewrote line formatting logic with explicit assertions
- **Padding Calculation**: Simplified and fixed padding calculation to ensure exact alignment

## [0.3.8] - 2024-12-14

### Fixed
- **Tips Box Spacing**: Fixed spacing issue with bullet points - ensured proper line content calculation
- **Line Formatting**: Added explicit line content validation to prevent spacing issues

## [0.3.7] - 2024-12-14

### Fixed
- **Tips Box Border**: Fixed right border alignment - corrected padding calculation
- **Header Color**: Changed "💡 Tips:" header from yellow to #67BED9 blue-cyan
- **Line Length**: Fixed line length calculation to ensure proper 60-character width

## [0.3.6] - 2024-12-14

### Changed
- **Color Scheme**: Changed accent color from orange to #67BED9 (custom blue-cyan)
- **UI Colors**: Updated all borders, highlights, and accents to use new color

## [0.3.5] - 2024-12-14

### Fixed
- **Tips Box Formatting**: Fixed right border alignment in tips box
- **Spacing Calculation**: Corrected padding calculation to account for visible text length

## [0.3.4] - 2024-12-14

### Changed
- **Startup Logo**: Replaced text logo with beautiful unicorn ASCII art 🦄

## [0.3.3] - 2024-12-14

### Added
- **File Access Status**: Shows file operations status at startup
- **Documentation**: Added `docs/FILE_ACCESS_GUIDE.md` explaining file access

### Changed
- **Startup Messages**: Shows file operations enabled status and command execution status

## [0.3.2] - 2024-12-14

### Major: Beautiful Terminal UI & Directory Awareness

**BREAKING CHANGE**: Terminal UI completely redesigned to match Claude Code style!

### Added
- **Styled Terminal UI**: 
  - Colored welcome box with logo (ASCII art)
  - Orange-brown borders and accents (like Claude Code)
  - Styled input prompt with green `>` symbol
  - Color-coded actions (green for success, orange for errors)
- **Directory Awareness**: Agent now stores and uses working directory consistently
- **File Operations**: All file operations use agent's working directory (not current shell directory)

### Fixed
- **Directory Tracking**: Agent knows its working directory and uses it for all file operations
- **File Reading**: "review my files" now correctly reads files from working directory
- **Path Resolution**: Relative paths resolved relative to agent's working directory

### Changed
- **UI Module**: New `selective_salience/ui.py` with styling utilities
- **Welcome Screen**: Professional colored box with logo, project info, and tips
- **Input Prompt**: Styled `> instinct8>` prompt (green `>`, white text)

### Technical Details
- Agent stores `_working_directory` at initialization
- All file operations (`_read_file`, `_write_file`, `_read_files_from_prompt`) use working directory
- Commands execute in working directory context
- UI uses ANSI color codes (no external dependencies)

## [0.3.1] - 2024-12-14

### Fixed
- **File Reading**: Agent now actually reads files when asked to "review files" or "look at files"
- **Clean Startup**: Suppressed verbose Strategy H initialization messages
- **File Operations**: Agent proactively reads files mentioned in prompts and includes them in context
- **Directory Listing**: When asked to review "all files", agent lists and reads project files

### Changed
- **Startup Messages**: Clean, professional startup without verbose logging
- **File Context**: Automatically includes file contents when user asks to review files

## [0.3.0] - 2024-12-14

### Major: Persistent Interactive Session (Like Claude Code!)

**BREAKING CHANGE**: `instinct8` with no arguments now starts a persistent session!

### Added
- **Persistent Interactive Mode**: `instinct8` (no args) starts a session that stays running
- **Context Retention**: Maintains conversation context across multiple prompts
- **Project Awareness**: Shows project name, git branch, working directory
- **Built-in Commands**: `help`, `stats`, `salience`, `compress`, `reset`, `quit`
- **Welcome Screen**: Shows project info and tips (like Claude Code)

### Changed
- **Default Behavior**: `instinct8` without prompt → starts interactive session (not help)
- **One-shot Mode**: `instinct8 "prompt"` still works for single execution
- **Better UX**: More intuitive, Claude Code-like experience

### Usage

```bash
# Persistent session (NEW!)
instinct8                    # Starts interactive session
instinct8> create a file     # Type prompts directly
instinct8> add a function    # Context maintained!
instinct8> quit              # Exit when done

# One-shot mode (still works)
instinct8 "create a file"    # Executes and exits
```

## [0.2.2] - 2024-12-14

### Fixed
- **File creation now works!** - Instinct8 now actually creates files from code blocks (like Codex)
- Files are created by default (safe operation, unlike command execution)
- Improved filename inference from prompts and LLM responses
- Better detection of file creation intent in LLM responses

### Changed
- File creation no longer requires `--allow-execution` flag
- Code blocks (Python, JS, etc.) automatically create files
- Text files (`.txt`) are created automatically
- Bash commands still require `--allow-execution` for safety

## [0.2.1] - 2024-12-14

### Fixed
- **Fixed UnboundLocalError in agent_cli.py** - `args` variable scope issue when using quick question mode
- Quick question mode (`instinct8-agent "question"`) now works correctly
- Properly handles both mode-based and quick question paths

## [0.2.0] - 2024-12-14

### Major: Full Codex Replacement

**BREAKING CHANGE**: Instinct8Agent now generates actual code instead of mock responses!

### Added
- **Real LLM Code Generation**: `execute()` method now calls OpenAI API to generate code
- **File Operations**: Automatically creates files from generated code blocks
- **Command Execution**: Can execute shell commands (with `--allow-execution` flag)
- **Codex-style System Prompt**: Uses proper coding agent prompt
- **Code Block Parsing**: Extracts and processes code blocks from LLM responses
- **Selective Salience Compression**: Fully integrated with real agent operations

### Changed
- `answer_question()` now uses real LLM instead of mock
- `execute()` is the main entry point (like Codex's `exec`)
- File operations are automatic when code blocks are detected
- Commands are only executed if `allow_execution=True`

### Usage
```python
from selective_salience import Instinct8Agent

agent = Instinct8Agent()
agent.initialize(goal="Build FastAPI app", constraints=["Use JWT"])
response = agent.execute("create a login endpoint")
# Now generates actual Python code!
```

## [0.1.2] - 2024-12-14

### Fixed
- **Fixed circular import bug** - Made imports lazy to break cycle between `evaluation` and `strategies` modules
- Strategy imports in `harness.py` now lazy (imported inside functions)
- Token budget imports in `strategy_b_codex.py` now lazy (imported inside methods)
- Package should now install and run without import errors

### Changed
- Removed redundant `selective-salience` command (only 2 commands now: `instinct8` and `instinct8-agent`)

## [0.1.1] - 2024-12-14

### Fixed
- Fixed import errors - All required modules (`evaluation`, `strategies`) now properly included in package
- Fixed package structure - Removed sys.path hacks, using proper package imports
- Removed redundant `selective-salience` command - Now only 2 commands: `instinct8` and `instinct8-agent`

### Changed
- Package now includes full `evaluation` module (was missing before)
- Improved import paths for better compatibility when installed via pip

### Upgrade Instructions
```bash
pip install --upgrade instinct8-agent
```

## [0.1.0] - 2024-12-XX

### Added
- Initial release of Instinct8 Agent
- Selective Salience Compression strategy
- CLI commands: `instinct8` and `instinct8-agent`
- Codex-compatible `exec` interface
- Interactive agent mode
- Python API for programmatic usage
- Support for goal and constraint preservation
- Semantic deduplication for salience sets
- Token budget management

### Features
- **Instinct8 CLI**: Drop-in replacement for Codex `exec` command
- **Instinct8 Agent**: Interactive coding agent with Selective Salience Compression
- **Selective Salience Compression**: Preserves goal-critical information verbatim
- **Python API**: `Instinct8Agent` and `SelectiveSalienceCompressor` classes

### Installation
```bash
pip install instinct8-agent
```

### Usage
```bash
# Basic usage
instinct8 "create a FastAPI endpoint"

# Interactive mode
instinct8-agent interactive --goal "Build app" --constraints "Use JWT"

# As Codex replacement
alias codex=instinct8
codex exec "create a login endpoint"
```
