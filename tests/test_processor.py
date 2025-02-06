"""Tests for the file processor module."""

import pytest
import os
import json
from pathlib import Path
from unittest.mock import MagicMock
from code_diff_doc_gen import processor
from code_diff_doc_gen.llm import LLMClient


def test_read_source_files(tmp_path: Path) -> None:
    """Test reading source files from directory."""
    # Create test files
    test_dir = tmp_path / "test_files"
    test_dir.mkdir()

    test_file = test_dir / "test.swift"
    test_file.write_text("struct Test {}")

    # Test reading files
    files = processor.read_source_files(str(test_dir))

    assert len(files) == 1
    assert "test.swift" in files
    assert files["test.swift"] == "struct Test {}"


def test_read_source_files_empty_dir(tmp_path: Path) -> None:
    """Test reading from empty directory."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    files = processor.read_source_files(str(empty_dir))
    assert len(files) == 0


def test_read_source_files_missing_dir() -> None:
    """Test reading from non-existent directory."""
    with pytest.raises(FileNotFoundError):
        processor.read_source_files("nonexistent")


def test_create_description() -> None:
    """Test creating description from code."""
    # Create mock LLM client
    mock_client = MagicMock(spec=LLMClient)
    mock_client.complete.return_value = "Test description"

    code = """
    struct Counter {
        var count: Int = 0

        mutating func increment() {
            count += 1
        }
    }
    """

    description = processor.create_description(code, mock_client)

    # Verify description
    assert isinstance(description, str)
    assert description == "Test description"

    # Verify client was used correctly
    mock_client.complete.assert_called_once()
    args = mock_client.complete.call_args[0]
    messages = args[0]

    # Verify message structure
    assert len(messages) == 1
    assert messages[0].role == "user"
    assert "struct Counter" in messages[0].content


def test_save_descriptions(tmp_path: Path) -> None:
    """Test saving descriptions to JSON file."""
    # Create test data
    descriptions = {"test.swift": "A test description"}
    source_files = {"test.swift": "struct Test {}"}

    # Change to temp directory for test
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Save descriptions
        processor.save_descriptions(descriptions, source_files)

        # Verify file was created
        json_file = Path(".codescribe/descriptions/files.json")
        assert json_file.exists()

        # Verify content
        content = json.loads(json_file.read_text())
        assert "test.swift" in content
        assert content["test.swift"]["description"] == "A test description"

    finally:
        # Restore original directory
        os.chdir(original_cwd)


def test_read_descriptions(tmp_path: Path) -> None:
    """Test reading descriptions from JSON file."""
    # Create test data
    descriptions = {"test.swift": "A test description"}
    source_files = {"test.swift": "struct Test {}"}

    # Change to temp directory for test
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Save descriptions first
        processor.save_descriptions(descriptions, source_files)

        # Read descriptions
        read_data = processor.read_descriptions()

        # Verify content
        assert len(read_data) == 1
        assert "test.swift" in read_data
        assert read_data["test.swift"]["path"] == "test.swift"
        assert read_data["test.swift"]["language"] == "swift"
        assert read_data["test.swift"]["description"] == "A test description"
        assert read_data["test.swift"]["original"] == "struct Test {}"

    finally:
        # Restore original directory
        os.chdir(original_cwd)


def test_read_descriptions_missing_file() -> None:
    """Test reading from non-existent descriptions file."""
    with pytest.raises(FileNotFoundError):
        processor.read_descriptions()
