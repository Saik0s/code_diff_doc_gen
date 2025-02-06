"""Compare original and generated code files."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List
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


async def _compare_single_file(
    original_path: Path,
    generated_path: Path,
    analysis_dir: Path,
) -> FileDiff:
    """Compare a single pair of files.

    Args:
        original_path: Path to original file
        generated_path: Path to generated file
        analysis_dir: Directory to store analysis files

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

        # Save analysis to individual file
        analysis_file = (
            analysis_dir / original_path.parent / f"{original_path.name}.analysis"
        )
        analysis_file.parent.mkdir(parents=True, exist_ok=True)
        analysis_file.write_text(analysis)

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

    desc_dir = Path(".codescribe/descriptions")
    if not desc_dir.exists():
        raise FileNotFoundError("No descriptions found. Run process first.")

    # Find all description files
    desc_files = list(desc_dir.rglob("*.desc"))
    if not desc_files:
        raise FileNotFoundError("No description files found")

    # Create analysis directory for this round
    analysis_dir = Path(".codescribe/analysis") / f"round_{round_num}"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    # Create tasks for all file comparisons
    tasks = [
        _compare_single_file(
            Path(desc_file.parent / desc_file.stem.replace(".desc", "")),
            generated_dir / desc_file.parent / desc_file.stem.replace(".desc", ""),
            analysis_dir,
        )
        for desc_file in desc_files
    ]

    # Run all comparisons concurrently
    results = await asyncio.gather(*tasks)

    for result in results:
        if result.error:
            logger.warning(result.error)
        else:
            logger.info(f"Analyzed: {result.original_path}")

    logger.info(f"Analysis completed for round {round_num}")
