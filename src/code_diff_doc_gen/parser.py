# src/code_diff_doc_gen/parser.py
import os
from pathlib import Path
from loguru import logger
from typing import Dict, List


def is_swift_file(file_path: str) -> bool:
    """Check if a file is a Swift source file."""
    return file_path.lower().endswith(".swift")


def parse_code(input_path: str) -> Dict[str, str]:
    """
    Parses code from the input path. Can handle both single files and directories.
    Returns a dictionary mapping file paths to their contents.
    """
    logger.info(f"Parsing code from: {input_path}")
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")

    parsed_files: Dict[str, str] = {}

    if input_path.is_file():
        if is_swift_file(str(input_path)):
            logger.debug(f"Parsing single Swift file: {input_path}")
            try:
                with open(input_path, "r", encoding="utf-8") as f:
                    parsed_files[str(input_path)] = f.read()
            except Exception as e:
                logger.error(f"Error reading file {input_path}: {e}")
                raise
    elif input_path.is_dir():
        logger.debug(f"Parsing directory: {input_path}")
        for root, _, files in os.walk(input_path):
            for file in files:
                file_path = Path(root) / file
                if is_swift_file(str(file_path)):
                    logger.debug(f"Found Swift file: {file_path}")
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            parsed_files[str(file_path)] = f.read()
                    except Exception as e:
                        logger.error(f"Error reading file {file_path}: {e}")
                        logger.warning(f"Skipping file {file_path}")
                        continue

    if not parsed_files:
        logger.warning(f"No Swift files found in {input_path}")
    else:
        logger.info(f"Successfully parsed {len(parsed_files)} Swift files")

    return parsed_files
