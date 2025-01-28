# src/code_diff_doc_gen/generator.py
from typing import List, Any
from loguru import logger
from pathlib import Path


def format_code_block(code: str, language: str = "swift") -> str:
    """Format code with markdown code block syntax."""
    return f"```{language}\n{code}\n```"


def generate_section_header(title: str, level: int = 2) -> str:
    """Generate a markdown section header."""
    return f"{'#' * level} {title}\n\n"


def generate_documentation(
    code_blocks: List[Any],
    descriptions: List[Any],
    regenerated_code: List[Any],
    diffs: List[Any],
) -> str:
    """
    Generates documentation from code blocks, descriptions, regenerated code, and diffs.
    Returns formatted markdown documentation.
    """
    logger.info("Generating documentation")

    doc_parts = []

    # Title
    doc_parts.append("# Code Documentation\n\n")

    # Overview
    doc_parts.append(generate_section_header("Overview"))
    doc_parts.append(
        "This documentation provides an analysis of Swift code using The Composable Architecture (TCA) patterns.\n\n"
    )

    # Process each code block
    for i, (code_block, description, regenerated) in enumerate(
        zip(code_blocks, descriptions, regenerated_code), 1
    ):
        logger.debug(f"Processing block {i}")

        # Section header for each block
        doc_parts.append(generate_section_header(f"Code Block {i}", 3))

        # Original code
        doc_parts.append("**Original Code:**\n\n")
        doc_parts.append(format_code_block(code_block.code))
        doc_parts.append("\n")

        # Context and purpose
        if hasattr(code_block, "context") and code_block.context:
            doc_parts.append("**Context:**\n\n")
            doc_parts.append(f"{code_block.context}\n\n")

        # Description and analysis
        doc_parts.append("**Analysis:**\n\n")
        doc_parts.append(f"{description.description}\n\n")

        # Key components
        if hasattr(description, "key_components") and description.key_components:
            doc_parts.append("**Key Components:**\n\n")
            for component in description.key_components:
                doc_parts.append(f"- {component}\n")
            doc_parts.append("\n")

        # Dependencies
        if hasattr(description, "dependencies") and description.dependencies:
            doc_parts.append("**Dependencies:**\n\n")
            for dependency in description.dependencies:
                doc_parts.append(f"- {dependency}\n")
            doc_parts.append("\n")

        # Regenerated code
        doc_parts.append("**Regenerated Implementation:**\n\n")
        doc_parts.append(format_code_block(regenerated.code))
        doc_parts.append("\n")

        # Add separator between blocks
        if i < len(code_blocks):
            doc_parts.append("---\n\n")

    # If there are diffs, add them
    if diffs:
        doc_parts.append(generate_section_header("Code Differences"))
        for i, diff in enumerate(diffs, 1):
            doc_parts.append(f"### Diff {i}\n\n")
            doc_parts.append(format_code_block(str(diff), "diff"))
            doc_parts.append("\n")

    logger.info("Documentation generation completed")
    return "".join(doc_parts)
