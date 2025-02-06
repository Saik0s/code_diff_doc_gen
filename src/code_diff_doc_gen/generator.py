"""Generate code from descriptions."""

import asyncio
import json
from pathlib import Path
from typing import List, Dict
from loguru import logger

from .llm import generate_code_from_description, load_system_prompt


async def generate_file(desc_file: Path, round_num: int, prompt: str) -> Dict[str, str]:
    """Generate code for a single file.

    Args:
        desc_file: Path to the description file
        round_num: Generation round number
        prompt: System prompt for generation

    Returns:
        Dict containing file path, generated code (if any), and status
    """
    try:
        # Get original file path from description file
        file_path = desc_file.parent / desc_file.stem.replace(".desc", "")
        description = desc_file.read_text()

        output_path = Path(f".codescribe/generated/round_{round_num}/{file_path}")

        # Skip if file already exists
        if output_path.exists():
            logger.info(f"Skipping existing file: {file_path}")
            return {
                "path": str(file_path),
                "status": "skipped",
                "generated": output_path.read_text(),
            }

        implementation = await generate_code_from_description(
            description, str(file_path), prompt
        )

        # Save generated code
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(implementation)

        return {
            "path": str(file_path),
            "status": "generated",
            "generated": implementation,
        }
    except Exception as e:
        logger.exception(e)
        raise


async def generate_code(round_num: int) -> List[Dict[str, str]]:
    """Generate code for all descriptions in parallel.

    Args:
        round_num: Generation round number

    Returns:
        List of generated file data
    """
    # Find all description files
    desc_dir = Path(".codescribe/descriptions")
    if not desc_dir.exists():
        raise FileNotFoundError("No descriptions found. Run process first.")

    desc_files = list(desc_dir.rglob("*.desc"))
    if not desc_files:
        raise FileNotFoundError("No description files found")

    prompt = load_system_prompt(round_num)

    # Generate in parallel
    tasks = [generate_file(desc, round_num, prompt) for desc in desc_files]
    results = await asyncio.gather(*tasks)

    # Filter out failures
    generated = [r for r in results if r is not None]

    # Count genuinely generated files
    newly_generated = len([r for r in generated if r["status"] == "generated"])
    skipped = len([r for r in generated if r["status"] == "skipped"])

    # Save metadata
    meta = {
        "round": round_num,
        "total": len(desc_files),
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
