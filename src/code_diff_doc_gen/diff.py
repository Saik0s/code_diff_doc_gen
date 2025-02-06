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


async def compare_files(source_dir: Path, round_num: int) -> None:
    """Compare original and generated files in parallel and save results.

    Args:
        source_dir: Directory containing original source files
        round_num: Generation round number

    Raises:
        FileNotFoundError: If required directories/files don't exist
    """
    generated_dir = Path(f".codescribe/generated/round_{round_num}")
    if not generated_dir.exists():
        raise FileNotFoundError(f"No generated files found for round {round_num}")

    # Create analysis directory for this round
    analysis_dir = Path(".codescribe/analysis") / f"round_{round_num}"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    # Find all source files
    source_files = list(source_dir.rglob("*"))
    source_files = [
        f for f in source_files if f.is_file() and not f.name.startswith(".")
    ]

    if not source_files:
        raise FileNotFoundError(f"No source files found in {source_dir}")

    # Create tasks for all file comparisons
    tasks = [
        _compare_single_file(
            source_file,
            generated_dir / source_file.relative_to(source_dir),
            analysis_dir,
        )
        for source_file in source_files
    ]

    # Run all comparisons concurrently
    results = await asyncio.gather(*tasks)

    for result in results:
        if result.error:
            logger.warning(result.error)
        else:
            logger.info(f"Analyzed: {result.original_path}")

    logger.info(f"Analysis completed for round {round_num}")
