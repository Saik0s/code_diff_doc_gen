"""Diff generator module for CodeScribe.

Creates and manages code comparisons.
"""

from pathlib import Path
from loguru import logger
from typing import List, Optional
import difflib


def compare_code(original: str, generated: str) -> str:
    """Compare original and generated code.

    Args:
        original: Original source code
        generated: Generated code to compare

    Returns:
        Unified diff string
    """
    original_lines = original.splitlines()
    generated_lines = generated.splitlines()

    logger.info("Generating code comparison")

    diff = difflib.unified_diff(
        generated_lines,
        original_lines,
        fromfile="Generated",
        tofile="Original",
        lineterm="",
    )

    return "\n".join(diff)


def format_example(original: str, generated: str) -> str:
    """Format code comparison as example.

    Args:
        original: Original source code
        generated: Generated code

    Returns:
        Formatted example string
    """
    return f"""
# Bad (Generated)
```swift
{generated}
```

# Good (Original)
```swift
{original}
```

Key Differences:
{compare_code(original, generated)}
"""


def update_system_prompt(examples: List[str], round_num: int) -> None:
    """Update system prompt with new examples.

    Args:
        examples: List of formatted example strings
        round_num: Current generation round number

    Raises:
        FileNotFoundError: If base prompt doesn't exist
        IOError: If files can't be read/written
    """
    prompt_dir = Path(".codescribe/prompts")
    prompt_dir.mkdir(parents=True, exist_ok=True)

    # Read base prompt
    base_prompt_file = prompt_dir / "system_0.md"
    if not base_prompt_file.exists():
        raise FileNotFoundError("Base prompt file not found")

    try:
        base_prompt = base_prompt_file.read_text()
    except IOError as e:
        logger.error(f"Error reading base prompt: {e}")
        raise

    # Create new prompt with examples
    new_prompt = f"{base_prompt}\n\n# Examples\n\n"
    new_prompt += "\n\n".join(examples)

    # Save new prompt
    new_prompt_file = prompt_dir / f"system_{round_num}.md"

    logger.info(f"Saving updated prompt for round {round_num}")

    try:
        new_prompt_file.write_text(new_prompt)
        logger.info("System prompt updated successfully")
    except IOError as e:
        logger.error(f"Error saving updated prompt: {e}")
        raise
