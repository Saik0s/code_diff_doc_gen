import json
import os
import pytest
import threading
import time
from code_diff_doc_gen.state_manager import (
    create_initial_state,
    load_state,
    save_state,
    merge_states,
    AppState,
)


@pytest.fixture
def temp_state_file(tmp_path):
    return str(tmp_path / "test_state.json")


def test_create_initial_state():
    state = create_initial_state()
    assert state["current_stage"] == "input"
    assert state["input_path"] is None
    assert state["intermediate_results"]["split_code"] == {}
    assert state["intermediate_results"]["descriptions"] == {}
    assert state["intermediate_results"]["regenerated_code"] == {}
    assert state["intermediate_results"]["diffs"] == {}
    assert state["intermediate_results"]["documentation"] == {}
    assert state["intermediate_results"]["llm_score"] is None


def test_save_and_load_state(temp_state_file):
    initial_state = create_initial_state()
    save_state(initial_state, temp_state_file)

    loaded_state = load_state(temp_state_file)
    assert loaded_state is not None
    assert loaded_state["current_stage"] == initial_state["current_stage"]
    assert loaded_state["intermediate_results"] == initial_state["intermediate_results"]


def test_merge_states_with_new_data():
    # Create old state with some existing data
    old_state: AppState = create_initial_state()
    old_state["input_path"] = "file1.py"
    old_state["intermediate_results"]["split_code"] = {
        "file1.py": ["def old_func():", "    pass"]
    }

    # Create new state with different data
    new_state: AppState = create_initial_state()
    new_state["input_path"] = "file2.py"
    new_state["intermediate_results"]["split_code"] = {
        "file2.py": ["def new_func():", "    return True"]
    }

    # Merge states
    merged_state = merge_states(old_state, new_state)

    # Verify both old and new data are preserved
    assert "file1.py" in merged_state["intermediate_results"]["split_code"]
    assert "file2.py" in merged_state["intermediate_results"]["split_code"]
    assert merged_state["intermediate_results"]["split_code"]["file1.py"] == [
        "def old_func():",
        "    pass",
    ]
    assert merged_state["intermediate_results"]["split_code"]["file2.py"] == [
        "def new_func():",
        "    return True",
    ]


def test_merge_states_with_overlapping_data():
    # Create old state with existing data
    old_state: AppState = create_initial_state()
    old_state["input_path"] = "file1.py"
    old_state["intermediate_results"]["descriptions"] = {
        "file1.py": ["Old description"]
    }

    # Create new state with updated data for same file
    new_state: AppState = create_initial_state()
    new_state["input_path"] = "file1.py"
    new_state["intermediate_results"]["descriptions"] = {
        "file1.py": ["New description"]
    }

    # Merge states
    merged_state = merge_states(old_state, new_state)

    # Verify new data takes precedence
    assert merged_state["intermediate_results"]["descriptions"]["file1.py"] == [
        "New description"
    ]


def test_persistent_state_accumulation(temp_state_file):
    # First save
    state1: AppState = create_initial_state()
    state1["input_path"] = "file1.py"
    state1["intermediate_results"]["split_code"] = {
        "file1.py": ["def func1():", "    pass"]
    }
    save_state(state1, temp_state_file)

    # Second save with new data
    state2: AppState = create_initial_state()
    state2["input_path"] = "file2.py"
    state2["intermediate_results"]["split_code"] = {
        "file2.py": ["def func2():", "    return True"]
    }
    save_state(state2, temp_state_file)

    # Load final state
    final_state = load_state(temp_state_file)
    assert final_state is not None

    # Verify both sets of data are present
    assert "file1.py" in final_state["intermediate_results"]["split_code"]
    assert "file2.py" in final_state["intermediate_results"]["split_code"]


def test_load_state_nonexistent_file(temp_state_file):
    assert load_state(temp_state_file) is None


def test_load_state_corrupted_file(temp_state_file):
    # Write invalid JSON
    with open(temp_state_file, "w") as f:
        f.write("invalid json content")

    assert load_state(temp_state_file) is None


def test_merge_states_with_none_old_state():
    new_state = create_initial_state()
    merged_state = merge_states(None, new_state)
    assert merged_state == new_state


def test_merge_states_updates_non_historical_fields():
    old_state: AppState = create_initial_state()
    old_state["current_stage"] = "split"
    old_state["config"] = {"old_config": True}

    new_state: AppState = create_initial_state()
    new_state["current_stage"] = "describe"
    new_state["config"] = {"new_config": True}

    merged_state = merge_states(old_state, new_state)

    assert merged_state["current_stage"] == "describe"
    assert merged_state["config"] == {"new_config": True}


def test_concurrent_access(temp_state_file):
    def worker(worker_id):
        for i in range(10):
            state = create_initial_state()
            state["current_stage"] = f"worker_{worker_id}_stage_{i}"
            state["input_path"] = f"file_{worker_id}_{i}.py"
            state["intermediate_results"]["split_code"] = {
                f"file_{worker_id}_{i}.py": [f"def func_{worker_id}_{i}():", "    pass"]
            }
            save_state(state, temp_state_file)
            time.sleep(0.01)  # Small delay to increase chance of concurrent access

    # Create multiple threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)

    # Start all threads
    for t in threads:
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    # Verify state file integrity
    final_state = load_state(temp_state_file)
    assert final_state is not None
    assert final_state["current_stage"].startswith("worker_")
