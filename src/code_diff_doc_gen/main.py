"""Main CLI module for CodeScribe."""

import typer
import guidance
from pathlib import Path
from loguru import logger
from typing import Optional

from . import processor, generator, diff, utils

# Global model instance
lm: Optional[guidance.models.Model] = None

app = typer.Typer()


@app.command()
def init() -> None:
    """Initialize CodeScribe workspace and model."""
    global lm
    try:
        # Initialize workspace
        utils.init_workspace()

        # Initialize Guidance model
        logger.info("Initializing Guidance model")
        lm = guidance.llms.OpenAI("gpt-3.5-turbo")

        typer.echo("CodeScribe workspace and model initialized successfully")
    except Exception as e:
        typer.echo(f"Error initializing: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def process(
    directory: str = typer.Argument(..., help="Directory containing source files")
) -> None:
    """Process source files and create descriptions."""
    global lm
    try:
        utils.ensure_workspace_exists()

        # Ensure model is initialized
        if lm is None:
            raise RuntimeError("Model not initialized. Run 'init' first.")

        # Read source files
        files = processor.read_source_files(directory)
        typer.echo(f"Found {len(files)} source files")

        # Create descriptions using model
        descriptions = {
            filename: processor.create_description(content, lm)
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
    global lm
    try:
        utils.ensure_workspace_exists()

        # Ensure model is initialized
        if lm is None:
            raise RuntimeError("Model not initialized. Run 'init' first.")

        # Read descriptions
        desc_file = Path(".codescribe/descriptions.toml")
        if not desc_file.exists():
            raise FileNotFoundError("No descriptions found. Run 'process' first.")

        # Read system prompt
        prompt = generator.read_system_prompt(round_num)

        examples = []

        # Generate code for each description using model
        for filename, desc_data in processor.read_descriptions().items():
            # Generate code
            generated = generator.generate_code(lm, desc_data["description"], prompt)

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
