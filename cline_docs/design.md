# Module Design

## processor.py
```python
def read_source_files(directory: str) -> dict[str, str]:
    """Read source files."""

def create_description(content: str, lm: guidance.models.Model) -> str:
    """Create description using Guidance."""

def save_descriptions(descriptions: dict[str, str]) -> None:
    """Save to TOML."""
```

## generator.py
```python
def read_system_prompt(round_num: int) -> str:
    """Read prompt for round."""

@guidance
def generate_code(lm: guidance.models.Model, description: str, prompt: str) -> str:
    """Generate code using Guidance."""

def save_generated_code(code: str, round_num: int, filename: str) -> None:
    """Save generated code."""
```

## diff.py
```python
def compare_code(original: str, generated: str) -> str:
    """Compare code versions."""

def format_example(original: str, generated: str) -> str:
    """Format as example."""

def update_system_prompt(examples: list[str], round_num: int) -> None:
    """Update prompt with examples."""
```

## main.py
```python
def init() -> None:
    """Setup workspace."""

def process(directory: str) -> None:
    """Process files."""

def generate(round_num: int) -> None:
    """Run generation round."""
```

Simple functions using Guidance for LLM control.
