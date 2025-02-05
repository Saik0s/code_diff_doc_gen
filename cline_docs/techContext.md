# Technical Context

## Stack
- Python 3.11
- Guidance for LLM control
- TOML for storage
- Typer for CLI

## Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.11"
typer = "^0.9.0"
toml = "^0.10.2"
guidance = "^0.1.0"  # For LLM control
```

## Structure
```
src/code_diff_doc_gen/
  main.py          # CLI
  processor.py     # File handling
  generator.py     # Code gen with Guidance
  diff.py          # Comparisons
  utils.py         # Helpers
```

## Setup
1. Install deps
2. Set up Guidance model
3. Run script

That's all we need.
