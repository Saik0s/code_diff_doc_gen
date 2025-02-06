"""Generate code from descriptions."""

import asyncio
import json
from pathlib import Path
from typing import List, Dict
from loguru import logger

from .llm import generate_code_from_description, load_system_prompt


async def generate_file(
    description: Dict[str, str], round_num: int, prompt: str
) -> Dict[str, str]:
    """Generate code for a single file.

    Returns:
        Dict containing file path, generated code (if any), and status
    """
    try:
        output_path = Path(
            f".codescribe/generated/round_{round_num}/{description['path']}"
        )

        # Skip if file already exists
        if output_path.exists():
            logger.info(f"Skipping existing file: {description['path']}")
            return {
                "path": description["path"],
                "status": "skipped",
                "generated": output_path.read_text(),
            }

        implementation = await generate_code_from_description(
            description["description"], description["path"], prompt
        )

        # Save generated code
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(implementation)

        return {
            "path": description["path"],
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
    # Load descriptions
    desc_file = Path(".codescribe/descriptions/files.json")
    if not desc_file.exists():
        raise FileNotFoundError("No descriptions found. Run process first.")

    descriptions = json.loads(desc_file.read_text())
    descriptions = list(descriptions.values())  # Convert dict to list

    prompt = load_system_prompt(round_num)
    # Generate in parallel
    tasks = [generate_file(desc, round_num, prompt) for desc in descriptions]
    results = await asyncio.gather(*tasks)

    # Filter out failures
    generated = [r for r in results if r is not None]

    # Count genuinely generated files
    newly_generated = len([r for r in generated if r["status"] == "generated"])
    skipped = len([r for r in generated if r["status"] == "skipped"])

    # Save metadata
    meta = {
        "round": round_num,
        "total": len(descriptions),
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
