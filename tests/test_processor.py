"""Tests for the file processor module."""

import pytest
import os
from pathlib import Path
from unittest.mock import MagicMock
import guidance
from code_diff_doc_gen import processor


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
    # Create mock model
    mock_model = MagicMock()
    mock_result = MagicMock()
    mock_result.__getitem__.return_value = "Test description"
    mock_model.return_value = mock_result

    code = """
    struct Counter {
        var count: Int = 0

        mutating func increment() {
            count += 1
        }
    }
    """

    description = processor.create_description(code, mock_model)

    # Verify description
    assert isinstance(description, str)
    assert description == "Test description"

    # Verify model was called
    assert mock_model.called


def test_save_descriptions(tmp_path: Path) -> None:
    """Test saving descriptions to TOML file."""
    # Create test descriptions
    descriptions = {"test.swift": "A test description"}

    # Change to temp directory for test
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Save descriptions
        processor.save_descriptions(descriptions)

        # Verify file was created
        toml_file = Path(".codescribe/descriptions.toml")
        assert toml_file.exists()

        # Verify content
        content = toml_file.read_text()
        assert "test.swift" in content
        assert "A test description" in content

    finally:
        # Restore original directory
        os.chdir(original_cwd)
