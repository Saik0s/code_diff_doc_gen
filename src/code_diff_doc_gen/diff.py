"""Compare original and generated code files."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path
from typing import List, Dict
from loguru import logger
from .llm import analyze_code_differences
import asyncio


@dataclass
class FileDiff:
    """Represents differences between original and generated files."""

    original_path: Path
    generated_path: Path
    analysis: str
    error: str | None = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert Path objects to strings
        data["original_path"] = str(data["original_path"])
        data["generated_path"] = str(data["generated_path"])
        return data


async def _compare_single_file(
    original_path: Path,
    generated_path: Path,
) -> FileDiff:
    """Compare a single pair of files.

    Args:
        original_path: Path to original file
        generated_path: Path to generated file

    Returns:
        FileDiff containing analysis results
    """
    try:
        if not generated_path.exists():
            return FileDiff(
                original_path=original_path,
                generated_path=generated_path,
                analysis="",
                error=f"Generated file not found: {generated_path}",
            )

        original_content = original_path.read_text(encoding="utf-8")
        generated_content = generated_path.read_text(encoding="utf-8")

        analysis = await analyze_code_differences(original_content, generated_content)
        return FileDiff(
            original_path=original_path,
            generated_path=generated_path,
            analysis=analysis,
        )
    except Exception as e:
        logger.exception(e)
        raise


async def compare_files(round_num: int) -> None:
    """Compare original and generated files in parallel and save results.

    Args:
        round_num: Generation round number

    Raises:
        FileNotFoundError: If required directories/files don't exist
    """
    generated_dir = Path(f".codescribe/generated/round_{round_num}")
    if not generated_dir.exists():
        raise FileNotFoundError(f"No generated files found for round {round_num}")

    desc_file = Path(".codescribe/descriptions/files.json")
    if not desc_file.exists():
        raise FileNotFoundError("No descriptions found. Run process first.")

    descriptions = json.loads(desc_file.read_text(encoding="utf-8"))
    descriptions = list(descriptions.values())  # Convert dict to list

    # Create tasks for all file comparisons
    tasks = [
        _compare_single_file(Path(desc["path"]), generated_dir / desc["path"])
        for desc in descriptions
    ]

    # Run all comparisons concurrently
    results = await asyncio.gather(*tasks)

    for result in results:
        if result.error:
            logger.warning(result.error)
        else:
            logger.info(f"Analyzed: {result.original_path}")

    # Create output directory
    output_dir = Path(".codescribe/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare results with metadata
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "round": round_num,
        "results": [diff.to_dict() for diff in results],
    }

    # Save results to JSON file
    output_file = output_dir / f"analysis_round_{round_num}.json"
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    logger.info(f"Analysis saved to {output_file}")
