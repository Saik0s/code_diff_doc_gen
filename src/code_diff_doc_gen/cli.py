# src/code_diff_doc_gen/cli.py
import typer
from typing import Optional
from pathlib import Path
from code_diff_doc_gen import state_manager, parser, llm, generator
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.theme import Theme
from loguru import logger

# Configure Rich theme
custom_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "red bold",
        "success": "green bold",
    }
)

app = typer.Typer()
console = Console(theme=custom_theme)

# Configure loguru
logger.add(
    "app.log",
    rotation="500 MB",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


@app.command()
def process_code(
    input_path: str = typer.Argument(..., help="Path to input code files"),
    output_file: str = typer.Option(
        "output.md", help="Path to output documentation file"
    ),
    state_file: str = typer.Option("state.json", help="Path to state file"),
    resume: Optional[bool] = typer.Option(
        False, "--resume", help="Resume from previous state if available"
    ),
    library_name: Optional[str] = typer.Option(
        None, "--library-name", help="Name of the library being documented"
    ),
):
    """
    Generates documentation for code changes.
    """
    try:
        if resume:
            loaded_state = state_manager.load_state(state_file)
            if loaded_state:
                console.print(
                    f"[info]Resuming from previous state loaded from '{state_file}'[/info]"
                )
                logger.info(f"Resuming from previous state loaded from '{state_file}'")
                state = loaded_state
            else:
                console.print(
                    f"[warning]No valid state file found at '{state_file}'. Starting from initial state.[/warning]"
                )
                logger.warning(
                    f"No valid state file found at '{state_file}'. Starting from initial state."
                )
                state = state_manager.create_initial_state()
        else:
            state = state_manager.create_initial_state()
            console.print("[info]Starting with a new initial state.[/info]")
            logger.info("Starting with a new initial state.")

        state["input_path"] = input_path
        state["output_file"] = output_file
        state["current_stage"] = "input"
        state["library_name"] = library_name

        console.print(f"Processing input path: [bold blue]{input_path}[/bold blue]")
        logger.info(f"Processing input path: {input_path}")

        # 1. Parse Code
        with Progress(
            SpinnerColumn(), TextColumn("[bold magenta]{task.description}")
        ) as progress:
            parse_task = progress.add_task("Parsing code files...")
            logger.info("Parsing code files...")
            parsed_files = parser.parse_code(input_path)
            progress.update(
                parse_task,
                description=f"Parsed {len(parsed_files)} files.",
                advance=100,
            )
            logger.info(f"Parsed {len(parsed_files)} files.")

        # Process each file
        all_descriptions = []
        all_regenerated_code = []

        for file_path, code in parsed_files.items():
            console.print(f"\nProcessing file: [bold blue]{file_path}[/bold blue]")
            logger.info(f"Processing file: {file_path}")

            # 2. Split Code
            with Progress(
                SpinnerColumn(), TextColumn("[bold magenta]{task.description}")
            ) as progress:
                split_task = progress.add_task("Splitting code...")
                logger.info("Splitting code...")
                split_code_result = llm.split_code_with_llm(code, library_name)
                state["intermediate_results"][
                    "split_code"
                ] = split_code_result.code_blocks
                state["current_stage"] = "split"
                progress.update(split_task, description="Code split.", advance=100)
                logger.info("Code split.")

            # 3. Describe Code Blocks
            console.print("[bold magenta]Describing code blocks...[/bold magenta]")
            logger.info("Describing code blocks...")
            descriptions = []
            if state["intermediate_results"]["split_code"]:
                with Progress(
                    SpinnerColumn(), TextColumn("[bold magenta]{task.description}")
                ) as progress:
                    describe_task = progress.add_task("Describing code blocks...")
                    for code_block in state["intermediate_results"]["split_code"]:
                        description = llm.describe_code_block_with_llm(
                            code_block.code, library_name
                        )
                        descriptions.append(description)
                        progress.update(
                            describe_task,
                            advance=100
                            / len(state["intermediate_results"]["split_code"]),
                            description=f"Described block {len(descriptions)}/{len(state['intermediate_results']['split_code'])}...",
                        )
                    progress.update(
                        describe_task, description="Code blocks described.", advance=100
                    )
                    logger.info("Code blocks described.")
                all_descriptions.extend(descriptions)

            # 4. Regenerate Code from Descriptions
            console.print(
                "[bold magenta]Regenerating code from descriptions...[/bold magenta]"
            )
            logger.info("Regenerating code from descriptions...")
            regenerated_code_blocks = []
            with Progress(
                SpinnerColumn(), TextColumn("[bold magenta]{task.description}")
            ) as progress:
                regenerate_task = progress.add_task("Regenerating code...")
                for description in descriptions:
                    regenerated_code = llm.regenerate_code_from_description_with_llm(
                        description.description, library_name
                    )
                    regenerated_code_blocks.append(regenerated_code)
                    progress.update(
                        regenerate_task,
                        advance=100 / len(descriptions),
                        description=f"Regenerated block {len(regenerated_code_blocks)}/{len(descriptions)}...",
                    )
                progress.update(
                    regenerate_task, description="Code regenerated.", advance=100
                )
                logger.info("Code regenerated.")
                all_regenerated_code.extend(regenerated_code_blocks)

            state_manager.save_state(state, state_file)
            logger.info(
                f"State saved to '{state_file}' after processing file {file_path}"
            )

        # Update state with all processed files
        state["intermediate_results"]["descriptions"] = all_descriptions
        state["intermediate_results"]["regenerated_code"] = all_regenerated_code
        state["current_stage"] = "regenerate"

        # 5. Generate Documentation
        console.print("[bold magenta]Generating documentation...[/bold magenta]")
        logger.info("Generating documentation...")
        with Progress(
            SpinnerColumn(), TextColumn("[bold magenta]{task.description}")
        ) as progress:
            doc_task = progress.add_task("Generating documentation...")
            documentation = generator.generate_documentation(
                state["intermediate_results"]["split_code"],
                state["intermediate_results"]["descriptions"],
                state["intermediate_results"]["regenerated_code"],
                state["intermediate_results"].get("diffs", []),
            )
            state["intermediate_results"]["documentation"] = documentation
            state["current_stage"] = "document"
            progress.update(
                doc_task, description="Documentation generated.", advance=100
            )
            logger.info("Documentation generated.")

        # 6. Score Documentation with LLM
        console.print("[bold magenta]Scoring documentation with LLM...[/bold magenta]")
        logger.info("Scoring documentation with LLM...")
        with Progress(
            SpinnerColumn(), TextColumn("[bold magenta]{task.description}")
        ) as progress:
            score_task = progress.add_task("Scoring documentation...")
            llm_score_result = llm.score_documentation_with_llm(documentation)
            state["intermediate_results"]["llm_score"] = {
                "score": llm_score_result.score,
                "feedback": llm_score_result.feedback,
                "improvement_suggestions": llm_score_result.improvement_suggestions,
            }
            state["current_stage"] = "llm_score"
            progress.update(
                score_task, description="Documentation scored.", advance=100
            )
            logger.info("Documentation scored.")

        # Save final state
        state_manager.save_state(state, state_file)
        logger.info(f"Final state saved to '{state_file}'")

        # Write documentation to output file
        output_path = Path(output_file)
        output_path.write_text(documentation)
        console.print(f"\nDocumentation written to: [success]{output_file}[/success]")
        logger.info(f"Documentation written to: {output_file}")

        # Display score and feedback
        console.print("\n[bold cyan]Documentation Score:[/bold cyan]")
        console.print(f"Score: {llm_score_result.score}/10")
        console.print("\n[bold cyan]Feedback:[/bold cyan]")
        console.print(llm_score_result.feedback)
        console.print("\n[bold cyan]Improvement Suggestions:[/bold cyan]")
        for suggestion in llm_score_result.improvement_suggestions:
            console.print(f"• {suggestion}")

    except Exception as e:
        logger.exception("An error occurred during execution")
        console.print(f"[error]Error: {str(e)}[/error]")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
