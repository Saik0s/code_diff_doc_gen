# src/code_diff_doc_gen/cli.py
import typer
from typing import Optional
from . import state_manager, parser, llm, generator
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

app = typer.Typer()
STATE_FILE = "code_diff_doc_gen_state.json"  # Define state file name
console = Console()  # Initialize rich console
logger.add(
    "app.log",
    rotation="500 MB",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)  # Basic loguru setup - will refine format later


@app.command()
def main(
    input_path: str,
    resume: Optional[bool] = typer.Option(
        False, "--resume", help="Resume from previous state if available"
    ),
):
    """
    Generates documentation for code changes.
    """
    if resume:
        loaded_state = state_manager.load_state(STATE_FILE)
        if loaded_state:
            console.print(
                f"Resuming from previous state loaded from '{STATE_FILE}'", style="info"
            )  # Rich console output
            logger.info(
                f"Resuming from previous state loaded from '{STATE_FILE}'"
            )  # Loguru logging
            state = loaded_state
        else:
            console.print(
                f"No valid state file found at '{STATE_FILE}'. Starting from initial state.",
                style="warning",
            )  # Rich console output
            logger.warning(
                f"No valid state file found at '{STATE_FILE}'. Starting from initial state."
            )  # Loguru logging
            state = state_manager.create_initial_state()
    else:
        state = state_manager.create_initial_state()
        console.print(
            "Starting with a new initial state.", style="info"
        )  # Rich console output
        logger.info("Starting with a new initial state.")  # Loguru logging

    state["input_path"] = input_path  # Update input path in state
    state["current_stage"] = "input"  # Set current stage

    console.print(
        f"Processing input path: [bold blue]{input_path}[/bold blue]"
    )  # Rich console output
    logger.info(f"Processing input path: {input_path}")  # Loguru logging

    # 1. Parse Code
    with Progress(
        SpinnerColumn(), TextColumn("[bold magenta]{task.description}")
    ) as progress:  # Rich progress context manager
        parse_task = progress.add_task("Parsing code...")  # Rich progress task
        logger.info("Parsing code...")  # Loguru logging
        code = parser.parse_code(input_path)
        progress.update(
            parse_task, description="Code parsed.", advance=100
        )  # Rich progress update
        logger.info("Code parsed.")  # Loguru logging

    # 2. Split Code
    with Progress(
        SpinnerColumn(), TextColumn("[bold magenta]{task.description}")
    ) as progress:  # Rich progress context manager
        split_task = progress.add_task("Splitting code...")  # Rich progress task
        logger.info("Splitting code...")  # Loguru logging
        split_code_result = llm.split_code_with_llm(code)
        state["intermediate_results"][
            "split_code"
        ] = (
            split_code_result.code_blocks
        )  # Assuming code_blocks is the correct attribute
        state["current_stage"] = "split"
        progress.update(
            split_task, description="Code split.", advance=100
        )  # Rich progress update
        logger.info("Code split.")  # Loguru logging

    # 3. Describe Code Blocks
    console.print(
        "Describing code blocks...", style="bold magenta"
    )  # Rich console output
    logger.info("Describing code blocks...")  # Loguru logging
    descriptions = []
    if state["intermediate_results"]["split_code"]:
        with Progress(
            SpinnerColumn(), TextColumn("[bold magenta]{task.description}")
        ) as progress:  # Rich progress context manager
            describe_task = progress.add_task(
                "Describing code blocks..."
            )  # Rich progress task
            logger.info("Describing code blocks...")  # Loguru logging
            for code_block in state["intermediate_results"]["split_code"]:
                description = llm.describe_code_block_with_llm(code_block.code)
                descriptions.append(
                    description
                )  # Assuming description is the correct attribute
                progress.update(
                    describe_task,
                    advance=100 / len(state["intermediate_results"]["split_code"]),
                    description=f"Described block {len(descriptions)}/{len(state['intermediate_results']['split_code'])}...",
                )  # Rich progress update for each block
            progress.update(
                describe_task, description="Code blocks described.", advance=100
            )  # Rich progress update for task completion
            logger.info("Code blocks described.")  # Loguru logging
        state["intermediate_results"]["descriptions"] = descriptions
        state["current_stage"] = "describe"

    state_manager.save_state(state, STATE_FILE)  # Save state after describe stage
    console.print(
        f"State saved to '{STATE_FILE}' after describe stage", style="bold green"
    )  # Rich console output
    logger.info(f"State saved to '{STATE_FILE}' after describe stage")  # Loguru logging

    # 4. Regenerate Code from Descriptions
    print(
        "Regenerating code from descriptions..."
    )  # Placeholder UI - will replace with rich
    regenerated_code_blocks = []
    if state["intermediate_results"]["descriptions"]:
        for description in state["intermediate_results"]["descriptions"]:
            regenerated_code = llm.regenerate_code_from_description_with_llm(
                description.description
            )  # Assuming description is the correct attribute
            regenerated_code_blocks.append(regenerated_code)
        state["intermediate_results"]["regenerated_code"] = regenerated_code_blocks
        state["current_stage"] = "regenerate"
    print(
        "Code regenerated from descriptions."
    )  # Placeholder UI - will replace with rich

    state_manager.save_state(state, STATE_FILE)  # Save state after regenerate stage
    print(f"State saved to '{STATE_FILE}' after regenerate stage")

    # 5. Generate Documentation
    print("Generating documentation...")  # Placeholder UI - will replace with rich
    if (
        state["intermediate_results"]["split_code"]
        and state["intermediate_results"]["descriptions"]
        and state["intermediate_results"]["regenerated_code"]
    ):
        documentation = generator.generate_documentation(
            state["intermediate_results"]["split_code"],
            state["intermediate_results"]["descriptions"],
            state["intermediate_results"]["regenerated_code"],
            state["intermediate_results"]["diffs"],  # Diffs are not implemented yet
        )
        state["intermediate_results"]["documentation"] = documentation
        state["current_stage"] = "document"
    print("Documentation generated.")  # Placeholder UI - will replace with rich

    state_manager.save_state(state, STATE_FILE)  # Save state after document stage
    print(f"State saved to '{STATE_FILE}' after documentation stage")

    # 6. Score Documentation with LLM
    print(
        "Scoring documentation with LLM..."
    )  # Placeholder UI - will replace with rich
    if state["intermediate_results"]["documentation"]:
        llm_score_result = llm.score_documentation_with_llm(
            state["intermediate_results"]["documentation"]
        )
        state["intermediate_results"]["llm_score"] = {
            "score": llm_score_result.score,
            "feedback": llm_score_result.feedback,
        }
        state["current_stage"] = "llm_score"
    print("Documentation scored.")  # Placeholder UI - will replace with rich

    state_manager.save_state(state, STATE_FILE)  # Save state after LLM score stage
    print(f"State saved to '{STATE_FILE}' after LLM score stage")

    # 7. Output Documentation (for now just print to console)
    print("\nFinal Documentation:\n")  # Placeholder UI - will replace with rich
    if state["intermediate_results"]["documentation"]:
        print(state["intermediate_results"]["documentation"])
        state["current_stage"] = "output"
    print(
        "\nDocumentation output completed."
    )  # Placeholder UI - will replace with rich

    state_manager.save_state(state, STATE_FILE)  # Save state after output stage
    print(f"State saved to '{STATE_FILE}' after output stage")


if __name__ == "__main__":
    app()
