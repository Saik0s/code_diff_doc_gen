# Technical Context

## Stack
- Python 3.11+
- uv for package management
- OpenAI API for LLM - via `openai` and `python-dotenv` libraries
- instructor for structured output -  `instructor` library for structured LLM responses using Pydantic models
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

### Environment Variables
To run this project, you will need to set up the following environment variables. These variables are used to configure the OpenAI API keys and model names for both evaluation and target models. Create a `.env.example` file in the project root with the following variables:

- `EVAL_OPENAI_API_KEY`: OpenAI API key for evaluation.
- `EVAL_OPENAI_BASE_URL`: OpenAI base URL for evaluation.
- `EVAL_MODEL_NAME`: Model name for evaluation.
- `TARGET_OPENAI_API_KEY`: OpenAI API key for the target model.
- `TARGET_OPENAI_BASE_URL`: OpenAI base URL for the target model.
- `TARGET_MODEL_NAME`: Model name for the target model.

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
