"""Code generator module for CodeScribe.

Generates code from descriptions using Guidance and system prompts.
"""

from pathlib import Path
import guidance
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


@guidance
def generate_code(lm: guidance.models.Model, description: str, prompt: str) -> str:
    """Generate code from description using Guidance.

    Args:
        lm: Guidance language model to use
        description: Source code description
        prompt: System prompt to use

    Returns:
        Generated code
    """
    # Create Guidance program
    program = guidance(
        """
    {{#system~}}
    You are an expert in the detected language and frameworks. Generate code from the provided description.
    {{prompt}}
    {{~/system}}

    {{#user~}}
    Generate code for this description:
    {{description}}
    {{~/user}}

    {{#assistant~}}
    {{gen 'code' temperature=0 max_tokens=1000}}
    {{~/assistant}}
    """
    )

    # Run program
    result = program(lm, description=description, prompt=prompt)

    # Extract and clean generated code
    code = result["code"].strip()
    logger.debug(f"Generated code: {code}")

    return code
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
