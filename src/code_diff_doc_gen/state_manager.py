# src/code_diff_doc_gen/state_manager.py
import json
import time
import hashlib
import os
import fcntl
from typing import Optional, TypedDict, Any, Dict, Union, List
from pydantic import BaseModel
import threading

STATE_FILE_LOCK = "state.lock"

# Thread-safe lock for state operations
state_lock = threading.Lock()

class LLMScore(TypedDict):
    score: Optional[int]  # Or maybe a string like "Good", "Fair"
    feedback: Optional[str]

class IntermediateResults(TypedDict):
    split_code: Union[
        Dict[str, list], List[Any]
    ]  # Map of file paths to lists of code blocks or list of blocks
    descriptions: Union[
        Dict[str, list], List[Any]
    ]  # Map of file paths to lists of descriptions or list of descriptions
    regenerated_code: Union[
        Dict[str, list], List[Any]
    ]  # Map of file paths to lists of regenerated code or list of code
    diffs: Union[
        Dict[str, list], List[Any]
    ]  # Map of file paths to lists of diffs or list of diffs
    documentation: Union[
        Dict[str, str], Optional[str]
    ]  # Map of file paths to documentation or single doc string
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


def convert_to_dict_format(
    data: Union[List[Any], Dict[str, Any], None], current_file: str
) -> Dict[str, Any]:
    """Convert list format to dictionary format with file path as key."""
    if data is None:
        return {}
    if isinstance(data, list) and data:
        return {current_file: data}
    if isinstance(data, dict):
        return data
    return {}


def merge_states(old_state: Optional[AppState], new_state: AppState) -> AppState:
    """Merges old and new states, preserving historical data."""
    if not old_state:
        return new_state

    # Create a deep copy of the old state to avoid modifying it directly
    merged_state = {
        "input_path": new_state["input_path"],
        "current_stage": new_state["current_stage"],
        "config": new_state["config"],
        "intermediate_results": {
            "split_code": dict(old_state["intermediate_results"]["split_code"]),
            "descriptions": dict(old_state["intermediate_results"]["descriptions"]),
            "regenerated_code": dict(
                old_state["intermediate_results"]["regenerated_code"]
            ),
            "diffs": dict(old_state["intermediate_results"]["diffs"]),
            "documentation": (
                dict(old_state["intermediate_results"]["documentation"])
                if isinstance(old_state["intermediate_results"]["documentation"], dict)
                else {}
            ),
            "llm_score": new_state["intermediate_results"]["llm_score"],
        },
    }

    # Merge new state data
    for key in ["split_code", "descriptions", "regenerated_code", "diffs"]:
        if new_state["intermediate_results"][key]:
            merged_state["intermediate_results"][key].update(
                convert_to_dict_format(
                    new_state["intermediate_results"][key],
                    new_state.get("input_path", ""),
                )
            )

    # Handle documentation separately
    if new_state["intermediate_results"].get("documentation"):
        if isinstance(new_state["intermediate_results"]["documentation"], dict):
            merged_state["intermediate_results"]["documentation"].update(
                new_state["intermediate_results"]["documentation"]
            )
        else:
            doc_content = new_state["intermediate_results"]["documentation"]
            if doc_content and new_state.get("input_path"):
                merged_state["intermediate_results"]["documentation"][
                    new_state["input_path"]
                ] = doc_content

    return merged_state


def load_state(state_file: str) -> Optional[AppState]:
    """Loads application state from a JSON file."""
    with state_lock:
        try:
            if not os.path.exists(state_file):
                return None

            with open(state_file, "r") as f:
                fcntl.flock(f, fcntl.LOCK_EX)  # Exclusive lock for reading
                try:
                    content = f.read()
                    if not content:
                        return None

                    state_entries = json.loads(content)
                    if not state_entries:
                        return None

                    # Validate and return the latest valid state entry
                    for entry in reversed(state_entries):
                        if validate_state_entry(entry):
                            return entry["state"]

                    print(f"Warning: No valid state entries found in '{state_file}'")
                    return None
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)  # Release lock
        except Exception as e:
            print(f"Error loading state: {e}")
            return None

def save_state(state: AppState, state_file: str) -> None:
    """Saves application state to a JSON file with append-only and integrity checks."""
    with state_lock:
        try:
            state_entries = []
            current_id = 0
            temp_file = f"{state_file}.tmp"

            # Load existing state entries and merge with current state
            if os.path.exists(state_file):
                with open(state_file, "r") as f:
                    fcntl.flock(f, fcntl.LOCK_EX)
                    try:
                        content = f.read()
                        if content:
                            state_entries = json.loads(content)
                            if state_entries:
                                current_id = state_entries[-1].get("id", 0) + 1
                                # Merge with the latest valid state
                                for entry in reversed(state_entries):
                                    if validate_state_entry(entry):
                                        state = merge_states(entry["state"], state)
                                        break
                    finally:
                        fcntl.flock(f, fcntl.LOCK_UN)

            # Create new state entry
            new_state_entry = {
                "id": current_id,
                "timestamp": time.time(),
                "state": state,
            }
            new_state_entry["checksum"] = calculate_checksum(new_state_entry["state"])

            if not validate_state_entry(new_state_entry):
                raise ValueError("New state entry is invalid")

            # Add new entry
            state_entries.append(new_state_entry)

            # Atomic write using temporary file
            with open(temp_file, "w") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    json.dump(state_entries, f, indent=2, cls=PydanticJSONEncoder)
                    f.flush()
                    os.fsync(f.fileno())  # Ensure data is written to disk
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)

            # Atomic rename
            os.replace(temp_file, state_file)

        except Exception as e:
            print(f"Error saving state: {e}")
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            raise

def create_initial_state() -> AppState:
    """Creates an initial application state."""
    return {
        "input_path": None,
        "current_stage": "input",
        "intermediate_results": {
            "split_code": {},
            "descriptions": {},
            "regenerated_code": {},
            "diffs": {},
            "documentation": {},
            "llm_score": None,
        },
        "config": {},
    }


def calculate_checksum(state: AppState) -> str:
    """Calculates SHA256 checksum for the state."""
    state_json = json.dumps(state, sort_keys=True, cls=PydanticJSONEncoder).encode(
        "utf-8"
    )
    return hashlib.sha256(state_json).hexdigest()


def validate_state_entry(entry: Dict[str, Any]) -> bool:
    """Validates a state entry by checking checksum and required fields."""
    try:
        if not all(key in entry for key in ["id", "timestamp", "state", "checksum"]):
            return False
        if not isinstance(entry["id"], int) or not isinstance(
            entry["timestamp"], (int, float)
        ):
            return False

        calculated_checksum = calculate_checksum(entry["state"])
        return calculated_checksum == entry["checksum"]
    except Exception:
        return False
