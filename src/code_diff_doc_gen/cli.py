# src/code_diff_doc_gen/cli.py
import typer
from typing import Optional
from . import state_manager

app = typer.Typer()
STATE_FILE = "code_diff_doc_gen_state.json"  # Define state file name


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
            print(f"Resuming from previous state loaded from '{STATE_FILE}'")
            state = loaded_state
        else:
            print(
                f"No valid state file found at '{STATE_FILE}'. Starting from initial state."
            )
            state = state_manager.create_initial_state()
    else:
        state = state_manager.create_initial_state()
        print("Starting with a new initial state.")

    state["input_path"] = input_path  # Update input path in state
    state["current_stage"] = "input"  # Set current stage

    # Placeholder for pipeline execution - will be implemented later
    print(f"Processing input path: {input_path}")
    print(f"Current state: {state}")  # Print current state for debugging

    state_manager.save_state(state, STATE_FILE)  # Save state after each run (for now)
    print(f"State saved to '{STATE_FILE}'")


if __name__ == "__main__":
    app()
