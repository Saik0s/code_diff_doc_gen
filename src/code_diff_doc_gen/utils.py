"""Shared utilities for CodeScribe.

Common functionality used across modules.
"""

from pathlib import Path
from loguru import logger
from typing import Optional


def init_workspace() -> None:
    """Initialize .codescribe directory structure.

    Creates:
    - .codescribe/
      - descriptions.toml
      - prompts/
        - system_0.md
      - generated/

    Raises:
        IOError: If directories can't be created
    """
    workspace = Path(".codescribe")

    try:
        # Create main directory
        workspace.mkdir(exist_ok=True)
        logger.info("Created .codescribe directory")

        # Create prompts directory
        prompts_dir = workspace / "prompts"
        prompts_dir.mkdir(exist_ok=True)

        # Create generated directory
        generated_dir = workspace / "generated"
        generated_dir.mkdir(exist_ok=True)

        # Create initial system prompt if it doesn't exist
        base_prompt = prompts_dir / "system_0.md"
        if not base_prompt.exists():
            base_prompt.write_text(
                """You are an expert Swift developer.

Your task is to implement Swift code based on descriptions.

Follow these guidelines:
1. Use SwiftUI best practices
2. Implement clean, maintainable code
3. Follow Swift style guidelines
4. Include proper error handling
5. Add clear documentation

# Examples will be added here during generation rounds
"""
            )
            logger.info("Created initial system prompt")

        logger.info("Workspace initialized successfully")

    except IOError as e:
        logger.error(f"Error initializing workspace: {e}")
        raise


def ensure_workspace_exists() -> None:
    """Ensure .codescribe workspace exists.

    Raises:
        RuntimeError: If workspace doesn't exist
    """
    if not Path(".codescribe").exists():
        raise RuntimeError("Workspace not initialized. Run 'codescribe init' first.")
