"""Main CLI module for CodeScribe."""

import typer
from pathlib import Path
from loguru import logger
from typing import Optional

from . import processor, generator, diff, utils

app = typer.Typer()


@app.command()
def init() -> None:
    """Initialize CodeScribe workspace."""
    try:
        utils.init_workspace()
        typer.echo("CodeScribe workspace initialized successfully")
    except Exception as e:
        typer.echo(f"Error initializing workspace: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def process(
    directory: str = typer.Argument(..., help="Directory containing source files")
) -> None:
    """Process source files and create descriptions."""
    try:
        utils.ensure_workspace_exists()

        # Read source files
        files = processor.read_source_files(directory)
        typer.echo(f"Found {len(files)} source files")

        # Create descriptions
        descriptions = {
            filename: processor.create_description(content)
            for filename, content in files.items()
        }

        # Save descriptions
        processor.save_descriptions(descriptions)
        typer.echo("Descriptions created and saved successfully")

    except Exception as e:
        typer.echo(f"Error processing files: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def generate(
    round_num: int = typer.Argument(..., help="Generation round number")
) -> None:
    """Run generation round and create comparisons."""
    try:
        utils.ensure_workspace_exists()

        # Read descriptions
        desc_file = Path(".codescribe/descriptions.toml")
        if not desc_file.exists():
            raise FileNotFoundError("No descriptions found. Run 'process' first.")

        # Read system prompt
        prompt = generator.read_system_prompt(round_num)

        examples = []

        # Generate code for each description
        for filename, desc_data in processor.read_descriptions().items():
            # Generate code
            generated = generator.generate_code(desc_data["description"], prompt)

            # Save generated code
            generator.save_generated_code(generated, round_num, filename)

            # Create comparison example
            example = diff.format_example(desc_data["original"], generated)
            examples.append(example)

        # Update system prompt for next round
        diff.update_system_prompt(examples, round_num + 1)

        typer.echo(f"Round {round_num} completed successfully")

    except Exception as e:
        typer.echo(f"Error in generation round: {e}", err=True)
        raise typer.Exit(1)


def main() -> None:
    """Main CLI entry point."""
    app()
