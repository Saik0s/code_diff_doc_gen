# Technical Context

## Stack
- Python 3.11+
- uv for package management
- OpenAI API for LLM
- instructor for structured output
- libcst for code parsing
- typer for CLI
- json module for state persistence
- loguru for logging
- rich for terminal UI and progress reporting

## Setup
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv run code-diff-doc-gen --help
```

## Development
- Black formatting
- Ruff linting
- Pytest for core tests
- Type hints required

## Logging and UI
- Structured logging with loguru
- Rich progress bars and spinners
- Color-coded output
- Detailed operation tracking
- Error tracebacks with syntax highlighting
- Progress reporting for long-running operations
