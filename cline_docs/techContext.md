# Technical Context

## Stack
- Python 3.11
- OpenAI API for LLM operations
- TOML for configuration storage
- Typer for CLI interface
- Loguru for logging
- Difflib for code comparisons

## Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.11"
typer = "^0.9.0"
toml = "^0.10.2"
openai = "^1.0.0"  # For LLM operations
loguru = "^0.7.0"  # For logging
```

## Structure
```
src/code_diff_doc_gen/
  main.py          # CLI interface
  processor.py     # File handling and descriptions
  generator.py     # Code generation with OpenAI
  diff.py          # Code comparisons
  llm.py          # OpenAI client wrapper
  utils.py         # Helper functions

.codescribe/
  descriptions.toml       # File descriptions
  prompts/               # System prompts
    system_0.md          # Base prompt
    system_N.md          # With examples
  generated/             # Output code
    round_N/            # By round
```

## Setup
1. Install dependencies:
   ```bash
   pip install poetry
   poetry install
   ```

2. Configure OpenAI:
   - Set OPENAI_API_KEY environment variable
   - Default model: gpt-4

3. Initialize workspace:
   ```bash
   python -m code_diff_doc_gen init
   ```

4. Run workflow:
   ```bash
   # Process source files
   python -m code_diff_doc_gen process <directory>

   # Generate code (round N)
   python -m code_diff_doc_gen generate N
   ```

## Development
- Use Black for formatting
- Tests with pytest
- Loguru for structured logging
- Type hints throughout codebase
