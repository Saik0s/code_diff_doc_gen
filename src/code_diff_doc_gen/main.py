"""Code generation and analysis tool."""

import asyncio
from pathlib import Path
import typer
from loguru import logger

from .processor import process_files
from .generator import generate_code
from .diff import compare_files
from .llm import analyze_code_differences

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
            await generate_code(round_num)

            # Compare and analyze
            logger.info("Analyzing changes...")
            await compare_files(round_num)

            logger.info(f"Analysis saved")

        except Exception as e:
            logger.exception(e)
            raise typer.Exit(1)

    asyncio.run(main())


def main():
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()
