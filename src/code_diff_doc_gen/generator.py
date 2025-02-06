"""Generate code from descriptions."""

import asyncio
import json
from pathlib import Path
from typing import List, Dict
from loguru import logger

from .llm import generate_code_from_description, load_system_prompt


async def generate_file(
    source_file: Path,
    round_num: int,
    prompt: str,
    descriptions_dir: Path,
    source_dir: Path,
) -> Dict[str, str]:
    """Generate code for a single file.

    Args:
        source_file: Path to the original source file
        round_num: Generation round number
        prompt: System prompt for generation
        descriptions_dir: Directory where descriptions are stored
        source_dir: Base directory of source files

    Returns:
        Dict containing file path, generated code (if any), and status
    """
    # Compute corresponding description file path
    desc_file = (
        descriptions_dir
        / source_file.relative_to(source_dir).parent
        / f"{source_file.name}.desc"
    )

    if not desc_file.exists():
        raise FileNotFoundError(f"Description file not found: {desc_file}")

    # Determine output path in generated directory
    output_path = Path(
        f".codescribe/generated/round_{round_num}"
    ) / source_file.relative_to(source_dir)

    # Skip if generated file already exists
    if output_path.exists():
        logger.info(f"Skipping existing file: {source_file}")
        return {
            "path": str(source_file),
            "status": "skipped",
            "generated": output_path.read_text(),
        }

    description = desc_file.read_text()
    implementation = await generate_code_from_description(
        description, str(source_file), prompt
    )

    # Save generated code
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(implementation)

    return {
        "path": str(source_file),
        "status": "generated",
        "generated": implementation,
    }


async def generate_code(source_dir: Path, round_num: int) -> List[Dict[str, str]]:
    """Generate code for all source files in parallel.

    Args:
        source_dir: Directory containing original source files
        round_num: Generation round number

    Returns:
        List of generated file data
    """
    descriptions_dir = Path(".codescribe/descriptions")
    if not descriptions_dir.exists():
        raise FileNotFoundError("No descriptions found. Run process first.")

    # Get all source files
    source_files = list(source_dir.rglob("*"))
    source_files = [
        f for f in source_files if f.is_file() and not f.name.startswith(".")
    ]

    if not source_files:
        raise FileNotFoundError(f"No source files found in {source_dir}")

    prompt = load_system_prompt(round_num)

    tasks = [
        generate_file(f, round_num, prompt, descriptions_dir, source_dir)
        for f in source_files
    ]
    results = await asyncio.gather(*tasks)

    # Filter out failures (if any)
    generated = [r for r in results if r is not None]

    # Count genuinely generated files
    newly_generated = len([r for r in generated if r["status"] == "generated"])
    skipped = len([r for r in generated if r["status"] == "skipped"])

    meta = {
        "round": round_num,
        "total": len(source_files),
        "successful": len(generated),
        "newly_generated": newly_generated,
        "skipped": skipped,
    }
    meta_file = Path(f".codescribe/generated/round_{round_num}/metadata.json")
    meta_file.parent.mkdir(parents=True, exist_ok=True)
    meta_file.write_text(json.dumps(meta, indent=2))

    logger.info(
        f"Generated {newly_generated} new files, skipped {skipped} existing files"
    )
    return generated
