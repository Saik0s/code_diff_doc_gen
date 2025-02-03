# Module Design

## Core Modules

### 1. processor.py

```python
"""File processor module for CodeScribe.

Handles reading source files and creating descriptions.
"""

def read_source_files(directory: str) -> dict[str, str]:
    """Read source files from directory."""

def create_description(content: str) -> str:
    """Create description for source code."""

def save_descriptions(descriptions: dict[str, str]) -> None:
    """Save descriptions to TOML file."""
```

### 2. generator.py

```python
"""Code generator module for CodeScribe.

Generates code from descriptions using system prompts.
"""

def read_system_prompt(round_num: int) -> str:
    """Read system prompt for given round."""

def generate_code(description: str, prompt: str) -> str:
    """Generate code from description using prompt."""

def save_generated_code(code: str, round_num: int, filename: str) -> None:
    """Save generated code to appropriate round directory."""
```

### 3. diff.py

```python
"""Diff generator module for CodeScribe.

Creates and manages code comparisons.
"""

def compare_code(original: str, generated: str) -> str:
    """Compare original and generated code."""

def format_example(original: str, generated: str) -> str:
    """Format code comparison as example."""

def update_system_prompt(examples: list[str], round_num: int) -> None:
    """Update system prompt with new examples."""
```

### 4. main.py

```python
"""Main CLI module for CodeScribe."""

def init_workspace() -> None:
    """Initialize .codescribe directory structure."""

def process_files(directory: str) -> None:
    """Process source files and create descriptions."""

def generate_round(round_num: int) -> None:
    """Run generation round and create comparisons."""

def main() -> None:
    """Main CLI entry point."""
```

## File Structure

```
.codescribe/
  descriptions.toml       # File descriptions in TOML format
    [file.swift]
    path = "path/to/file"
    language = "swift"
    description = "..."

  prompts/               # System prompts
    system_0.md          # Base: "You are an expert..."
    system_1.md          # Base + Round 1 examples

  generated/             # Generated code
    round_1/
      file.swift
    round_2/
      file.swift
```

## Workflow

1. **Initialization**
   ```python
   init_workspace()
   # Creates .codescribe/ structure
   ```

2. **Processing**
   ```python
   process_files("tests/data/")
   # Creates descriptions.toml
   ```

3. **Generation**
   ```python
   generate_round(1)
   # Generates code and comparisons
   ```

4. **User Interaction**
   ```python
   # CLI prompts for another round
   # Updates system prompt if yes
   # Runs next generation round
   ```

## Testing Strategy

1. Use Swift example files from tests/data/
2. Focus on core workflow functionality
3. Test each module independently
4. Verify file operations and structure

## Implementation Notes

1. Keep functions simple and focused
2. Use type hints everywhere
3. Add clear docstrings
4. Handle errors gracefully
5. Log operations with Loguru
6. Use Typer for CLI interface
