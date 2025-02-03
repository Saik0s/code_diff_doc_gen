"""Code generator module for CodeScribe.

Generates code from descriptions using system prompts.
"""

from pathlib import Path
from loguru import logger
from typing import Optional


def read_system_prompt(round_num: int) -> str:
    """Read system prompt for given round.

    Args:
        round_num: Generation round number

    Returns:
        System prompt content

    Raises:
        FileNotFoundError: If prompt file doesn't exist
        IOError: If prompt file can't be read
    """
    prompt_dir = Path(".codescribe/prompts")
    prompt_file = prompt_dir / f"system_{round_num}.md"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    logger.info(f"Reading system prompt for round {round_num}")

    try:
        return prompt_file.read_text()
    except IOError as e:
        logger.error(f"Error reading prompt file: {e}")
        raise


def generate_code(description: str, prompt: str) -> str:
    """Generate code from description using prompt.

    Args:
        description: Source code description
        prompt: System prompt to use

    Returns:
        Generated code
    """
    # TODO: Implement actual code generation
    # For now return placeholder
    return "Generated code placeholder"


def save_generated_code(code: str, round_num: int, filename: str) -> None:
    """Save generated code to appropriate round directory.

    Args:
        code: Generated code content
        round_num: Generation round number
        filename: Original source filename

    Raises:
        IOError: If file can't be written
    """
    output_dir = Path(f".codescribe/generated/round_{round_num}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / filename

    logger.info(f"Saving generated code to {output_file}")

    try:
        output_file.write_text(code)
        logger.info("Generated code saved successfully")
    except IOError as e:
        logger.error(f"Error saving generated code: {e}")
        raise
