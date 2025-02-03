"""Tests for the diff generator module."""

import pytest
from pathlib import Path
from code_diff_doc_gen import diff


def test_compare_code() -> None:
    """Test code comparison."""
    original = """
    struct Counter {
        var count: Int = 0

        mutating func increment() {
            count += 1
        }
    }
    """

    generated = """
    struct Counter {
        var count: Int = 0

        func increment() {
            count += 1
        }
    }
    """

    result = diff.compare_code(original, generated)
    assert isinstance(result, str)
    assert "mutating" in result  # Key difference
    assert "-" in result  # Should contain diff markers
    assert "+" in result


def test_format_example() -> None:
    """Test example formatting."""
    original = "struct Test {}"
    generated = "class Test {}"

    result = diff.format_example(original, generated)
    assert isinstance(result, str)
    assert "Bad (Generated)" in result
    assert "Good (Original)" in result
    assert "struct Test" in result
    assert "class Test" in result
    assert "Key Differences:" in result


def test_update_system_prompt(tmp_path: Path) -> None:
    """Test system prompt updating."""
    # Create base prompt
    prompt_dir = tmp_path / ".codescribe" / "prompts"
    prompt_dir.mkdir(parents=True)

    base_content = "You are a Swift expert."
    base_file = prompt_dir / "system_0.md"
    base_file.write_text(base_content)

    examples = ["Example 1:\nBad vs Good", "Example 2:\nBad vs Good"]

    # Change to temp directory for test
    import os

    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Update prompt
        diff.update_system_prompt(examples, 1)

        # Verify new prompt
        new_file = prompt_dir / "system_1.md"
        assert new_file.exists()

        content = new_file.read_text()
        assert base_content in content
        assert "Examples" in content
        assert "Example 1" in content
        assert "Example 2" in content

    finally:
        os.chdir(original_cwd)


def test_update_system_prompt_missing_base() -> None:
    """Test updating prompt without base prompt."""
    with pytest.raises(FileNotFoundError):
        diff.update_system_prompt(["example"], 1)
