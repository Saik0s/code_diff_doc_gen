"""Tests for the code generator module."""

import pytest
from pathlib import Path
from code_diff_doc_gen import generator


def test_read_system_prompt(tmp_path: Path) -> None:
    """Test reading system prompt for a round."""
    # Create test prompt
    prompt_dir = tmp_path / ".codescribe" / "prompts"
    prompt_dir.mkdir(parents=True)

    prompt_content = "Test system prompt"
    prompt_file = prompt_dir / "system_1.md"
    prompt_file.write_text(prompt_content)

    # Test reading prompt
    with pytest.raises(FileNotFoundError):
        # Should fail in tmp_path without changing directory
        generator.read_system_prompt(1)

    # Change to temp directory for test
    import os

    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        content = generator.read_system_prompt(1)
        assert content == prompt_content

    finally:
        os.chdir(original_cwd)


def test_read_system_prompt_missing() -> None:
    """Test reading non-existent prompt."""
    with pytest.raises(FileNotFoundError):
        generator.read_system_prompt(999)


def test_generate_code() -> None:
    """Test code generation from description."""
    description = "A counter structure with increment method"
    prompt = "You are a Swift expert. Generate code based on description."

    code = generator.generate_code(description, prompt)
    assert isinstance(code, str)
    assert len(code) > 0


def test_save_generated_code(tmp_path: Path) -> None:
    """Test saving generated code."""
    code = "struct Test {}"
    round_num = 1
    filename = "test.swift"

    # Change to temp directory for test
    import os

    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Save generated code
        generator.save_generated_code(code, round_num, filename)

        # Verify file was created
        output_file = Path(f".codescribe/generated/round_{round_num}/{filename}")
        assert output_file.exists()
        assert output_file.read_text() == code

    finally:
        os.chdir(original_cwd)
