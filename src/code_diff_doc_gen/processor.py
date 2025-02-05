"""File processor module for CodeScribe.

Handles reading source files and creating descriptions using Guidance.
"""

from pathlib import Path
import toml
import guidance
from loguru import logger
from typing import Dict


def read_source_files(directory: str) -> Dict[str, str]:
    """Read source files from directory.

    Args:
        directory: Path to directory containing source files

    Returns:
        Dict mapping filenames to their contents

    Raises:
        FileNotFoundError: If directory doesn't exist
        IOError: If files can't be read
    """
    source_dir = Path(directory)
    if not source_dir.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    files: Dict[str, str] = {}

    logger.info(f"Reading source files from {directory}")

    try:
        # Recursively get all .swift files
        for file_path in source_dir.rglob("*.swift"):
            relative_path = file_path.relative_to(source_dir)
            files[str(relative_path)] = file_path.read_text()
            logger.debug(f"Read file: {relative_path}")

    except IOError as e:
        logger.error(f"Error reading files: {e}")
        raise

    logger.info(f"Found {len(files)} source files")
    return files


def create_description(content: str, lm: guidance.models.Model) -> str:
    """Create description for source code using Guidance.

    Args:
        content: Source code content to describe
        lm: Guidance language model to use

    Returns:
        Generated description of the code
    """
    # Create Guidance program
    program = guidance(
        """
    {{#system~}}
    You are an expert code analyzer. Describe the functionality of the provided code concisely.
    Focus on what the code does, not how it does it.
    {{~/system}}

    {{#user~}}
    Describe this code:
    ```
    {{code}}
    ```
    {{~/user}}

    {{#assistant~}}
    {{gen 'description' temperature=0 max_tokens=200}}
    {{~/assistant}}
    """
    )

    # Run program with content
    result = program(lm, code=content)

    # Extract and clean description
    description = result["description"].strip()
    logger.debug(f"Generated description: {description}")

    return description
    return "Source code description placeholder"


def save_descriptions(descriptions: Dict[str, str]) -> None:
    """Save descriptions to TOML file.

    Args:
        descriptions: Dict mapping filenames to descriptions

    Raises:
        IOError: If file can't be written
    """
    output_dir = Path(".codescribe")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "descriptions.toml"

    logger.info(f"Saving descriptions to {output_file}")

    try:
        # Convert to TOML format
        data = {
            filename: {
                "path": filename,
                "language": "swift",  # Hardcoded for now
                "description": desc,
            }
            for filename, desc in descriptions.items()
        }

        output_file.write_text(toml.dumps(data))
        logger.info("Descriptions saved successfully")

    except IOError as e:
        logger.error(f"Error saving descriptions: {e}")
        raise
