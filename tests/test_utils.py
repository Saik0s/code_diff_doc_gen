"""Tests for the utilities module."""

import pytest
from pathlib import Path
from code_diff_doc_gen import utils


def test_init_workspace(tmp_path: Path) -> None:
    """Test workspace initialization."""
    # Change to temp directory for test
    import os

    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Initialize workspace
        utils.init_workspace()

        # Verify directory structure
        workspace = Path(".codescribe")
        assert workspace.exists()
        assert workspace.is_dir()

        # Check prompts directory
        prompts_dir = workspace / "prompts"
        assert prompts_dir.exists()
        assert prompts_dir.is_dir()

        # Check generated directory
        generated_dir = workspace / "generated"
        assert generated_dir.exists()
        assert generated_dir.is_dir()

        # Check base prompt
        base_prompt = prompts_dir / "system_0.md"
        assert base_prompt.exists()
        assert base_prompt.is_file()

        content = base_prompt.read_text()
        assert "You are an expert Swift developer" in content
        assert "guidelines" in content

    finally:
        os.chdir(original_cwd)


def test_ensure_workspace_exists(tmp_path: Path) -> None:
    """Test workspace existence check."""
    # Change to temp directory for test
    import os

    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Should raise error when workspace doesn't exist
        with pytest.raises(RuntimeError) as exc:
            utils.ensure_workspace_exists()
        assert "not initialized" in str(exc.value)

        # Create workspace
        utils.init_workspace()

        # Should not raise error when workspace exists
        utils.ensure_workspace_exists()

    finally:
        os.chdir(original_cwd)
