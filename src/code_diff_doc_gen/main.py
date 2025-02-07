"""Code generation and analysis tool."""

import dotenv

dotenv.load_dotenv()

import asyncio
from pathlib import Path
import typer
from loguru import logger

from .processor import process_files
from .generator import generate_code
from .diff import compare_files
from .llm import (
    analyze_code_differences,
    deduplicate_generated_system_prompt,
    generate_system_prompt_from_analyses,
)

app = typer.Typer()


async def ensure_workspace():
    """Create workspace directories."""
    workspace = Path(".codescribe")
    for subdir in ["descriptions", "generated", "analysis"]:
        (workspace / subdir).mkdir(parents=True, exist_ok=True)


@app.command()
def run(
    source_dir: Path = typer.Argument(..., help="Source code directory"),
    round_num: int = typer.Option(0, "--round", "-r", help="Generation round"),
):
    """Process source code and generate documentation."""

    async def main():
        await ensure_workspace()

        try:
            # Process files
            logger.info("Processing source files...")
            await process_files(source_dir)

            # Generate code
            logger.info("Generating code...")
            await generate_code(source_dir, round_num)

            # Compare and analyze
            logger.info("Analyzing changes...")
            await compare_files(source_dir, round_num)

            # Generate system prompt for next round
            logger.info("Generating system prompt for next round...")
            await generate_system_prompt_from_analyses(round_num)

            # Deduplicate system prompt
            logger.info("Deduplicating system prompt...")
            await deduplicate_generated_system_prompt(round_num)

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
