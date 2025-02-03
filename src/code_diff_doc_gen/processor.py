"""File processor module for CodeScribe.

Handles reading source files and creating descriptions.
"""

from pathlib import Path
import toml
from loguru import logger
from typing import Dict, Optional


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


def create_description(content: str) -> str:
    """Create description for source code.

    Args:
        content: Source code content to describe

    Returns:
        Generated description of the code
    """
    # TODO: Implement actual description generation
    # For now return placeholder
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
