"""Process source files for code generation."""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import aiofiles
from loguru import logger
from tqdm.asyncio import tqdm

from .config import config
from .llm import generate_file_description


async def read_file(path: Path, descriptions_dir: Path, source_dir: Path) -> Dict[str, str]:
    """Read file content and generate description.

    Args:
        path: Path to the file
        descriptions_dir: Directory to store descriptions
        source_dir: Base directory of source files

    Returns:
        Dict containing file info and description
    """
    try:
        file_path_str = str(path)
        mtime = path.stat().st_mtime

        # Create mirrored path for description
        relative_path = path.relative_to(source_dir)
        desc_file = descriptions_dir / relative_path.parent / f"{path.name}.desc"

        # Check if description exists and is up to date
        if desc_file.exists() and desc_file.stat().st_mtime >= mtime:
            description = desc_file.read_text()
            logger.debug(f"Using existing description for: {path}")
        else:
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                content = await f.read()

            result = await generate_file_description(content, path)
            description = result.description

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
        logger.error(f"Error processing {path}: {e}")
        return None


async def process_files(source_dir: Path, output_dir: Optional[Path] = None) -> List[Dict[str, str]]:
    """Process source files in parallel.

    Args:
        source_dir: Directory containing source files
        output_dir: Custom output directory (default: config.output_dir)

    Returns:
        List of processed file data
    """
    workspace_dir = output_dir or config.output_dir
    descriptions_dir = workspace_dir / "descriptions"
    descriptions_dir.mkdir(parents=True, exist_ok=True)

    # Collect all source files
    files = list(source_dir.rglob("*"))
    files = [f for f in files if f.is_file() and not f.name.startswith(".")]

    if not files:
        raise ValueError(f"No files found in {source_dir}")

    logger.info(f"Processing {len(files)} files...")

    # Process files with progress bar
    tasks = [read_file(f, descriptions_dir, source_dir) for f in files]
    results = await tqdm.gather(*tasks, desc="Generating descriptions")

    # Filter out failures
    processed = [r for r in results if r is not None]

    logger.info(f"Successfully processed {len(processed)} of {len(files)} files")
    return processed
