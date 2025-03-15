"""Compare original and generated code files."""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from loguru import logger
from tqdm.asyncio import tqdm

from .llm import analyze_code_differences


@dataclass
class FileDiff:
    """Represents differences between original and generated files."""
    
    original_path: Path
    generated_path: Path
    analysis: str
    error: Optional[str] = None
    skipped: bool = False


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

        # Check if analysis can be skipped
        analysis_file = (
            analysis_dir / original_path.parent / f"{original_path.name}.analysis"
        )
        
        if analysis_file.exists():
            analysis_mtime = analysis_file.stat().st_mtime
            original_mtime = original_path.stat().st_mtime
            generated_mtime = generated_path.stat().st_mtime

            if analysis_mtime > original_mtime and analysis_mtime > generated_mtime:
                analysis = analysis_file.read_text()
                return FileDiff(
                    original_path=original_path,
                    generated_path=generated_path,
                    analysis=analysis,
                    skipped=True,
                )

        # Read file contents
        original_content = original_path.read_text(encoding="utf-8")
        generated_content = generated_path.read_text(encoding="utf-8")

        # Generate analysis
        result = await analyze_code_differences(original_content, generated_content)
        
        # Format analysis as markdown code blocks
        analysis = ""
        for pair in result.pairs:
            analysis += f"```\n// Bad Code\n{pair.bad_code}\n```\n\n```\n// Good Code\n{pair.good_code}\n```\n\n"

        # Save analysis to file
        analysis_file.parent.mkdir(parents=True, exist_ok=True)
        analysis_file.write_text(analysis)

        return FileDiff(
            original_path=original_path,
            generated_path=generated_path,
            analysis=analysis,
        )
    except Exception as e:
        logger.error(f"Error comparing {original_path}: {e}")
        return FileDiff(
            original_path=original_path,
            generated_path=generated_path,
            analysis="",
            error=str(e),
        )


async def compare_files(source_dir: Path, round_num: int, output_dir: Optional[Path] = None) -> None:
    """Compare original and generated files in parallel and save results.
    
    Args:
        source_dir: Directory containing original source files
        round_num: Generation round number
        output_dir: Custom output directory (default: config.output_dir)
        
    Raises:
        FileNotFoundError: If required directories/files don't exist
    """
    workspace_dir = output_dir or config.output_dir
    generated_dir = workspace_dir / "generated" / f"round_{round_num}"
    
    if not generated_dir.exists():
        raise FileNotFoundError(f"No generated files found for round {round_num}")

    # Create analysis directory for this round
    analysis_dir = workspace_dir / "analysis" / f"round_{round_num}"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    # Find all source files
    source_files = list(source_dir.rglob("*"))
    source_files = [
        f for f in source_files if f.is_file() and not f.name.startswith(".")
    ]

    if not source_files:
        raise FileNotFoundError(f"No source files found in {source_dir}")

    logger.info(f"Comparing {len(source_files)} files...")
    
    # Create tasks for file comparisons with progress bar
    tasks = [
        _compare_single_file(
            source_file,
            generated_dir / source_file.relative_to(source_dir),
            analysis_dir,
        )
        for source_file in source_files
    ]
    
    # Run all comparisons concurrently with progress reporting
    results = await tqdm.gather(*tasks, desc="Analyzing differences")

    # Count results by status
    skipped = len([r for r in results if r.skipped])
    analyzed = len([r for r in results if not r.skipped and not r.error])
    errors = len([r for r in results if r.error])

    logger.info(
        f"Analysis completed: {analyzed} analyzed, {skipped} skipped, {errors} errors"
    )