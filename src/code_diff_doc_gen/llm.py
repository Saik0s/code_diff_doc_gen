"""LLM operations using Anthropic's API with instructor library."""

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar

import anthropic
import instructor
from loguru import logger

from .config import config, update_usage_stats
from .models import CodeAnalysisResult, FileDescription, GeneratedCode

# Initialize Anthropic with instructor
client = instructor.from_anthropic(
    anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY")), mode=instructor.Mode.ANTHROPIC_REASONING_TOOLS, beta=True
)

T = TypeVar("T")


async def call_anthropic_model(
    system_prompt: str, user_message: str, response_model: T, max_tokens: Optional[int] = None, thinking_budget: Optional[int] = None
) -> T:
    """Call Anthropic model with instructor and track usage.

    Args:
        system_prompt: System prompt to guide generation
        user_message: User message content
        response_model: Pydantic model for response validation
        max_tokens: Maximum tokens to generate (default: config value)
        thinking_budget: Thinking budget tokens (default: config value)

    Returns:
        Response parsed into the provided model type
    """
    max_tokens = max_tokens or config.max_tokens
    thinking_budget = thinking_budget or config.thinking_budget

    # Prepare message for the API call
    messages = [
        {"role": "user", "content": [{"type": "text", "text": user_message, "cache_control": {"type": "ephemeral"}}]},
    ]

    # Make the API call with timing
    start_time = time.time()
    response, completion = await client.messages.create_with_completion(
        model=config.model,
        system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
        messages=messages,
        response_model=response_model,
        max_tokens=max_tokens,
        thinking={"type": "enabled", "budget_tokens": thinking_budget},
        betas=["output-128k-2025-02-19"],
    )

    elapsed = time.time() - start_time
    logger.info(f"LLM call completed in {elapsed:.2f}s")

    # Update token usage statistics
    update_usage_stats(completion.usage)

    return response


async def analyze_code_differences(original: str, generated: str) -> CodeAnalysisResult:
    """Analyze differences between original and generated code.

    Args:
        original: Original code
        generated: Generated code

    Returns:
        Analysis with good/bad code pairs
    """
    system_prompt = """
    You are a code review specialist analyzing code quality.
    Focus only on identifying problematic patterns in generated code by contrasting with the original.
    Extract ONLY concrete code examples showing incorrect vs correct implementation.
    Provide no commentary, only the code pairs.
    """

    user_prompt = f"""
    Compare these two code implementations and identify up to 3 important differences where the generated code
    uses outdated APIs, incorrect patterns, or suboptimal practices.

    <generated>
    {generated}
    </generated>

    <original>
    {original}
    </original>

    Return only code pairs showing specific issues in the generated code and how they should be fixed
    based on the original implementation. If the generated code is correct, return an empty list.
    """

    return await call_anthropic_model(
        system_prompt=system_prompt,
        user_message=user_prompt,
        response_model=CodeAnalysisResult,
    )


async def generate_file_description(content: str, file_path: Path) -> FileDescription:
    """Generate description for a source file.

    Args:
        content: File content
        file_path: Path to the file

    Returns:
        Generated description
    """
    system_prompt = """
# Code to Task Description Converter

You are a task description generator that converts code snippets into clear development tasks. When presented with a code file, create a concise task description that would logically result in a developer writing that code.

## Instructions:

1. Identify the main purpose of the code file and its key features
2. List all technologies, frameworks, and libraries explicitly used
3. Create a brief, focused task description with:
   - A clear title describing what needs to be built
   - 4-6 bullet points covering core requirements
   - A separate section listing all technical requirements/technologies

## Output Format:

```
# Task: [Brief, Specific Title]

Core requirements:
1. [Requirement 1]
2. [Requirement 2]
...

Technical requirements:
- [Technology 1]
- [Technology 2]
...
```

Keep your response concise and focused only on what would be needed in a developer task assignment. Do not explain the code or how it works - focus only on what needs to be built.
    """

    user_prompt = content

    return await call_anthropic_model(
        system_prompt=system_prompt,
        user_message=user_prompt,
        response_model=FileDescription,
    )


async def generate_code_from_description(description: str, file_path: str, system_prompt: Optional[str] = None) -> GeneratedCode:
    """Generate code from a description.

    Args:
        description: Natural language description of the code
        file_path: Path to the file being generated
        system_prompt: Optional system prompt to guide generation

    Returns:
        Generated code
    """
    default_prompt = """
# Task to Code Implementation Generator

You are an expert code implementation generator. Your job is to transform task descriptions into high-quality, production-ready code implementations. You should generate code that accurately fulfills all requirements specified in the task description.

## Instructions:

1. Analyze the task description thoroughly, paying close attention to:
   - Core functional requirements
   - Technical requirements (frameworks, libraries, patterns)
   - Any specified patterns or architectural approaches

2. Generate a complete implementation that:
   - Fulfills all stated requirements
   - Follows modern best practices for the specified technologies
   - Uses appropriate design patterns and architecture
   - Includes proper error handling and edge cases
   - Has a clean, maintainable structure

3. When specific technologies or frameworks are mentioned:
   - Use the exact APIs, patterns, and conventions of those technologies
   - Implement features using the idiomatic approaches for those frameworks
   - Include appropriate imports/dependencies

4. For SwiftUI or other UI frameworks:
   - Create a complete component implementation
   - Include all necessary view structures and state management
   - Implement proper UI interactions and navigation

## Response Format:

Begin with a brief overview of your implementation approach (1-2 sentences). Then provide the complete code implementation.

```[language]
// Complete code implementation here
```

If needed, you can include brief comments within the code to explain non-obvious implementation decisions.

## Important Guidelines:

- Generate complete, functional code that could be directly used in a project
- Follow the conventions and best practices of the specified language and frameworks
- Implement ALL requirements mentioned in the task description
- Do not omit code or use placeholders like "// Implementation here"
- Do not provide explanations outside of the code unless absolutely necessary
- If mock/sample data is needed, create appropriate examples
- Assume the existence of any dependencies mentioned in the task description
"""

    system_prompt = system_prompt or default_prompt

    user_prompt = f"""
    Generate code for:

    {description}

    The code should be for a file at: {file_path}
    Output only the implementation with no additional explanation.
    """

    return await call_anthropic_model(
        system_prompt=system_prompt,
        user_message=user_prompt,
        response_model=GeneratedCode,
    )


def load_system_prompt(round_num: int, workspace_dir: Path) -> Optional[str]:
    """Load system prompt for the specified generation round.

    Args:
        round_num: Generation round number
        workspace_dir: Path to workspace directory

    Returns:
        System prompt string if found, None otherwise
    """
    if round_num == 0:
        return "You are an expert developer that can generate prod ready code from description"

    prompt_file = workspace_dir / "prompts" / f"system_{round_num}.md"
    return prompt_file.read_text() if prompt_file.exists() else None


async def generate_system_prompt_from_analyses(round_num: int, workspace_dir: Path) -> str:
    """Generate a system prompt for the next round based on previous analyses.

    Args:
        round_num: Current generation round number
        workspace_dir: Path to workspace directory

    Returns:
        System prompt incorporating learnings from analyses
    """
    analysis_dir = workspace_dir / "analysis" / f"round_{round_num}"
    if not analysis_dir.exists():
        logger.warning(f"No analysis directory found for round {round_num}")
        return load_system_prompt(round_num, workspace_dir) or ""

    # Collect all analysis files
    analysis_files = list(analysis_dir.rglob("*.analysis"))
    if not analysis_files:
        logger.warning(f"No analysis files found for round {round_num}")
        return load_system_prompt(round_num, workspace_dir) or ""

    # Get previous prompt
    prev_prompt = load_system_prompt(round_num, workspace_dir) or ""

    # Combine all analyses
    analyses = "\n\n".join(f.read_text() for f in analysis_files)

    # Combine previous prompt with analyses
    next_prompt = f"{prev_prompt}\n\n# Examples from round {round_num}:\n\n{analyses}"

    # Save the new prompt
    prompt_dir = workspace_dir / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = prompt_dir / f"system_{round_num + 1}.md"
    prompt_file.write_text(next_prompt)

    return next_prompt
