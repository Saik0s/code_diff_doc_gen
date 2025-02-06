"""Process source files for code generation."""

import asyncio
from pathlib import Path
from typing import List, Dict
import aiofiles
from loguru import logger
import time
import json

from code_diff_doc_gen.llm import generate_file_description


async def read_file(
    path: Path, existing_data: Dict[str, Dict] = None
) -> Dict[str, str]:
    """Read file content asynchronously if needed.

    Args:
        path: Path to the file
        existing_data: Previously processed file data

    Returns:
        Dict containing file info and description or None if error
    """
    try:
        # Check if file was already processed
        file_path_str = str(path)
        mtime = path.stat().st_mtime

        if existing_data and file_path_str in existing_data:
            existing = existing_data[file_path_str]
            if existing.get("mtime", 0) >= mtime:
                logger.debug(f"Skipping unchanged file: {path}")
                return existing

        async with aiofiles.open(path, "r") as f:
            content = await f.read()

        return {
            "path": file_path_str,
            "content": content,
            "extension": path.suffix,
            "description": await generate_file_description(content, path),
            "mtime": mtime,
        }
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        return None


async def process_files(source_dir: Path) -> List[Dict[str, str]]:
    """Process source files in parallel.

    Args:
        source_dir: Directory containing source files

    Returns:
        List of processed file data
    """
    output_path = Path(".codescribe/descriptions/files.json")
    existing_data = {}

    # Load existing processed data if available
    if output_path.exists():
        try:
            existing_data = json.loads(output_path.read_text())
        except Exception as e:
            logger.warning(f"Could not load existing data: {e}")

    # Collect all source files
    files = list(source_dir.rglob("*"))
    files = [f for f in files if f.is_file() and not f.name.startswith(".")]

    if not files:
        raise ValueError(f"No files found in {source_dir}")

    # Process files concurrently
    tasks = [read_file(f, existing_data) for f in files]
    results = await asyncio.gather(*tasks)

    # Filter out failed reads
    processed = {r["path"]: r for r in results if r is not None}

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save processed data
    output_path.write_text(json.dumps(processed, indent=2))

    logger.info(f"Processed {len(processed)} files")
    return list(processed.values())
