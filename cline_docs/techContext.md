# Technical Context

## Stack
- Python 3.11+
- uv for package management
- OpenAI API for LLM
- instructor for structured output
- libcst for code parsing
- typer for CLI
- json module for state persistence

## Setup
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
export OPENAI_API_KEY=your-key
```

## Development
- Black formatting
- Ruff linting
- Pytest for core tests
- Type hints required
