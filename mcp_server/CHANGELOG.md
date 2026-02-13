# Changelog

All notable changes to the instinct8-mcp package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-13

### Added
- Initial release of instinct8 MCP server for Claude Code
- Three core tools for context compression with goal drift prevention:
  - `initialize_session`: Set up protected core with goal and constraints
  - `compress_context`: Compress conversation while preserving goal information
  - `measure_drift`: Quantify goal coherence after compression
- Two resources for monitoring compression state:
  - `session://current`: Current session state with salience set and statistics
  - `strategies://list`: Available compression strategies with descriptions
- Two prompt templates for compression operations:
  - `selective_salience_extract`: Extract goal-critical information from context
  - `protected_core_compress`: Compress with Protected Core pattern
- MCP sampling integration - uses client's own LLM for all processing
- Lightweight semantic deduplication using SequenceMatcher
- No API keys required - all processing done client-side
- Minimal dependencies (~50KB install size)

### Technical Details
- Built with FastMCP framework for clean MCP protocol implementation
- BSL 1.1 license (converts to Apache-2.0 after 3 years)
- Compatible with Python 3.10+
- Requires mcp>=1.0.0

### Known Limitations
- First release - feedback welcome
- Limited to in-memory session storage (sessions don't persist across restarts)
- No custom strategy configuration yet (uses default Selective Salience)