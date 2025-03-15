"""Code generation and analysis tool."""

import asyncio
import os
from pathlib import Path
import sys
import typer
from loguru import logger

from .config import config
from .processor import process_files
from .generator import generate_code
from .diff import compare_files
from .llm import generate_system_prompt_from_analyses

app = typer.Typer()

# Remove default handler
logger.remove()

# Add a new handler with custom format
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{file}:{line} {function}</cyan> - <level>{message}</level>",
    level="INFO",
)


async def ensure_workspace(workspace_dir: Path):
    """Create workspace directories."""
    for subdir in ["descriptions", "generated", "analysis", "prompts"]:
        (workspace_dir / subdir).mkdir(parents=True, exist_ok=True)


@app.command()
def run(
    source_dir: Path = typer.Argument(..., help="Source code directory"),
    round_num: int = typer.Option(0, "--round", "-r", help="Generation round"),
    output_dir: Path = typer.Option(None, "--output", "-o", help="Output directory"),
):
    """Process source code, generate code, and analyze differences."""
    async def main():
        # Set workspace directory
        workspace_dir = output_dir or config.output_dir
        logger.info(f"Using workspace directory: {workspace_dir}")

        await ensure_workspace(workspace_dir)

        try:
            # Process files
            logger.info("Processing source files...")
            await process_files(source_dir, workspace_dir)

            # Generate code
            logger.info("Generating code...")
            await generate_code(source_dir, round_num, workspace_dir)

            # Compare and analyze
            logger.info("Analyzing differences...")
            await compare_files(source_dir, round_num, workspace_dir)

            # Generate system prompt for next round
            logger.info("Generating system prompt for next round...")
            await generate_system_prompt_from_analyses(round_num, workspace_dir)

            logger.info(f"Analysis and system prompt generation completed")

        except Exception as e:
            logger.exception(e)
            raise typer.Exit(1)

    asyncio.run(main())


def main():
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()
