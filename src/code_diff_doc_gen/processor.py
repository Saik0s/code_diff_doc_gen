"""Process source files for code generation."""

import asyncio
from pathlib import Path
from typing import List, Dict
import aiofiles
from loguru import logger
import time

from code_diff_doc_gen.llm import generate_file_description


async def read_file(path: Path, descriptions_dir: Path) -> Dict[str, str]:
    """Read file content asynchronously and generate description.

    Args:
        path: Path to the file
        descriptions_dir: Directory to store descriptions

    Returns:
        Dict containing file info and description or None if error
    """
    try:
        file_path_str = str(path)
        mtime = path.stat().st_mtime

        # Create mirrored path for description
        relative_path = path.relative_to(
            path.parent.parent
        )  # Get path relative to project root
        desc_file = descriptions_dir / relative_path.parent / f"{path.name}.desc"

        # Check if description exists and is up to date
        if desc_file.exists() and desc_file.stat().st_mtime >= mtime:
            logger.debug(f"Skipping unchanged file: {path}")
            description = desc_file.read_text()
        else:
            async with aiofiles.open(path, "r") as f:
                content = await f.read()

            description = await generate_file_description(content, path)

            # Save description
            desc_file.parent.mkdir(parents=True, exist_ok=True)
            desc_file.write_text(description)

        return {
            "path": file_path_str,
            "extension": path.suffix,
            "description": description,
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
    descriptions_dir = Path(".codescribe/descriptions")
    descriptions_dir.mkdir(parents=True, exist_ok=True)

    # Collect all source files
    files = list(source_dir.rglob("*"))
    files = [f for f in files if f.is_file() and not f.name.startswith(".")]

    if not files:
        raise ValueError(f"No files found in {source_dir}")

    # Process files concurrently
    tasks = [read_file(f, descriptions_dir) for f in files]
    results = await asyncio.gather(*tasks)

    # Filter out failed reads
    processed = [r for r in results if r is not None]

    logger.info(f"Processed {len(processed)} files")
    return processed
