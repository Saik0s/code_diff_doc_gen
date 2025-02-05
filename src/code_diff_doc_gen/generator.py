"""Code generator module for CodeScribe.

Generates code from descriptions using OpenAI.
"""

from pathlib import Path
from loguru import logger
from typing import Optional

from .llm import LLMClient, Message


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


def generate_code(llm: LLMClient, description: str, prompt: str) -> str:
    """Generate code from description using OpenAI.

    Args:
        llm: LLM client to use
        description: Source code description
        prompt: System prompt to use

    Returns:
        Generated code
    """
    messages = [
        Message(
            role="system",
            content=f"""You are an expert in the detected language and frameworks. Generate code from the provided description.
{prompt}""",
        ),
        Message(
            role="user",
            content=f"""Generate code for this description:
{description}""",
        ),
    ]

    code = llm.complete(messages, temperature=0, max_tokens=1000)
    logger.debug(f"Generated code: {code}")
    return code


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
