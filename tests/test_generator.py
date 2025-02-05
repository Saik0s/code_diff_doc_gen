"""Tests for the code generator module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock
from code_diff_doc_gen import generator
from code_diff_doc_gen.llm import LLMClient


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
    # Create mock LLM client
    mock_client = MagicMock(spec=LLMClient)
    mock_client.complete.return_value = "struct Test {}"

    description = "A counter structure with increment method"
    prompt = "You are a Swift expert. Generate code based on description."

    code = generator.generate_code(mock_client, description, prompt)

    # Verify code generation
    assert isinstance(code, str)
    assert code == "struct Test {}"

    # Verify client was used correctly
    mock_client.complete.assert_called_once()
    args = mock_client.complete.call_args[0]
    messages = args[0]

    # Verify message structure
    assert len(messages) == 2
    assert messages[0].role == "system"
    assert messages[1].role == "user"
    assert "Swift expert" in messages[0].content
    assert description in messages[1].content


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
