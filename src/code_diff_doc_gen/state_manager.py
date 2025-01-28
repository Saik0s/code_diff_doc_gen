# src/code_diff_doc_gen/state_manager.py
import json
from typing import Optional, TypedDict, Any
from pydantic import BaseModel


class LLMScore(TypedDict):
    score: Optional[int]  # Or maybe a string like "Good", "Fair"
    feedback: Optional[str]


class IntermediateResults(TypedDict):
    split_code: Optional[list]  # List of code blocks (will refine type later)
    descriptions: Optional[list]  # List of descriptions (will refine type later)
    regenerated_code: Optional[list]  # List of regenerated code blocks
    diffs: Optional[list]  # List of diffs
    documentation: Optional[str]
    llm_score: Optional[LLMScore]


class AppState(TypedDict):
    input_path: Optional[str]
    current_stage: Optional[
        str
    ]  # "input", "split", "describe", "regenerate", "document", "llm_score", "output"
    intermediate_results: IntermediateResults
    config: dict  # Will define config later


class PydanticJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        return super().default(obj)


def load_state(state_file: str) -> Optional[AppState]:
    """Loads application state from a JSON file."""
    try:
        with open(state_file, "r") as f:
            state = json.load(f)
        return state  # type: ignore
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print(f"Warning: State file '{state_file}' is corrupted or invalid JSON.")
        return None


def save_state(state: AppState, state_file: str) -> None:
    """Saves application state to a JSON file."""
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2, cls=PydanticJSONEncoder)


def create_initial_state() -> AppState:
    """Creates an initial application state."""
    return {
        "input_path": None,
        "current_stage": "input",
        "intermediate_results": {
            "split_code": None,
            "descriptions": None,
            "regenerated_code": None,
            "diffs": None,
            "documentation": None,
            "llm_score": None,
        },
        "config": {},
    }
