"""LLM operations for code analysis and generation."""

import os
from typing import Any, Dict, List, Optional
import openai
from loguru import logger
from pathlib import Path
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput

# Initialize OpenAI client

client = openai.AsyncOpenAI()
reasoning_model = "openai/o3-mini"
large_output_model = "openai/o3-mini"

ANALYSIS_PROMPT = """
Review and compare the code differences below, highlighting API and library usage issues. Original code represents the correct implementation.

Original:
{original}

Generated:
{generated}

Provide code comparison blocks showing problematic vs correct patterns. Example format:

```
// Bad Code
function processUnknownData(x: any) {{
  // Anti-pattern
}}

// Good Code
function validateUserProfile(profile: UserProfile): ValidationResult {{
  // Type-safe implementation
}}
```

Focus on:
- API misuse
- Library integration errors
- Type safety issues
- Best practice violations

Show multiple examples if needed.
"""


async def call_llm(system: str, user: str, model: str = reasoning_model) -> str:
    system_role_name = "developer" if "o1" in model or "o3" in model else "system"
    for attempt in range(3):
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": system_role_name, "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.info(f"Response: {response if response else 'None'}")
            if attempt == 2:  # Last attempt
                logger.exception(e)
                raise
            logger.warning(f"Attempt {attempt + 1} failed, retrying...")


async def analyze_code_differences(original: str, generated: str) -> str:
    """Analyze differences between original and generated code using LLM.

    Args:
        original: Original code as a string
        generated: Generated code as a string

    Returns:
        Markdown formatted analysis of the code differences from LLM
    """
    try:
        system = (
            "You are an expert code reviewer focusing on "
            "design patterns, best practices, and code quality. Output only the bad/good code pairs, no other text."
        )
        user = ANALYSIS_PROMPT.format(original=original, generated=generated)

        analysis = await call_llm(system=system, user=user)
        return analysis

    except Exception as e:
        logger.exception(e)
        raise


async def generate_code_from_description(
    description: str, file_path: str, system_prompt: Optional[str] = None
) -> str:
    """Generate code from a description using the LLM.

    Args:
        description: Natural language description of the code
        file_path: Path to the file being generated
        system_prompt: Optional system prompt to guide generation

    Returns:
        Generated code as string
    """
    try:
        system = (
            system_prompt
            or "You are an expert software developer. "
            "Generate clean, efficient, and well-documented code. Output only the code, no other text."
        )
        user = f"Generate code for the following description:\n\n{description}"

        return await call_llm(system=system, user=user)

    except Exception as e:
        logger.exception(e)
        raise


def load_system_prompt(round_num: int) -> Optional[str]:
    """Load system prompt for the specified generation round.

    Args:
        round_num: Generation round number

    Returns:
        System prompt string if found, None otherwise
    """
    try:
        if round_num == 0:
            return "You are an expert developer that can generate prod ready code from description"

        prompt_file = Path(".codescribe") / "prompts" / f"system_{round_num}.md"
        return prompt_file.read_text()
    except Exception as e:
        logger.exception(e)
        raise


async def generate_file_description(content: str, file_path: Path) -> Optional[str]:
    """Generate description for a source file.

    Args:
        content: File content
        file_path: Path to the file

    Returns:
        Generated description or None if failed
    """
    try:
        system = "You are an expert code analyst and task description writer."
        user = f"What 3 paragraphs max task description would result in exactly following code if this task was completed by a developer:\n\n{content}"

        return (await call_llm(system=system, user=user)).strip()

    except Exception as e:
        logger.exception(e)
        raise


async def generate_system_prompt_from_analyses(round_num: int) -> str:
    """Generate a system prompt for the next round based on previous analyses.

    Args:
        round_num: Current generation round number

    Returns:
        System prompt incorporating learnings from analyses
    """
    try:
        analysis_dir = Path(".codescribe/analysis") / f"round_{round_num}"
        if not analysis_dir.exists():
            logger.warning(f"No analysis directory found for round {round_num}")
            return load_system_prompt(round_num) or ""

        # Collect all analysis files
        analysis_files = list(analysis_dir.rglob("*.analysis"))
        if not analysis_files:
            logger.warning(f"No analysis files found for round {round_num}")
            return load_system_prompt(round_num) or ""

        # Get previous prompt
        prev_prompt = load_system_prompt(round_num) or ""

        # Combine all analyses
        analyses = "\n\n".join(
            f"Analysis for {f.stem}:\n{f.read_text()}" for f in analysis_files
        )

        # Combine previous prompt with analyses
        next_prompt = f"{prev_prompt}\n\nAnalyses from round {round_num}:\n\n{analyses}"

        # Save the new prompt
        prompt_dir = Path(".codescribe") / "prompts"
        prompt_dir.mkdir(parents=True, exist_ok=True)
        prompt_file = prompt_dir / f"system_{round_num + 1}.md"
        prompt_file.write_text(next_prompt)

        return next_prompt

    except Exception as e:
        logger.exception(e)
        raise


async def deduplicate_generated_system_prompt(round_num: int):
    """Deduplicate system prompt using aider.

    Args:
        round_num: Current generation round number

    Raises:
        FileNotFoundError: If system prompt file not found
    """
    prompt_file = Path(".codescribe") / "prompts" / f"system_{round_num + 1}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"System prompt file not found for round {round_num}")

    # Initialize aider components
    model = Model("gpt-4-turbo")
    io = InputOutput(yes=True)  # Auto-confirm changes
    coder = Coder.create(main_model=model, fnames=[str(prompt_file)], io=io)

    # Run deduplication instruction
    await coder.run(
        """Review the content and deduplicate similar code examples by:
        1. Merging similar code blocks showing the same pattern into a single good/bad pair
        2. Keeping only unique patterns/approaches
        3. Ensuring the merged examples clearly demonstrate the key differences
        4. Maintaining all important context and explanations"""
    )

    # Move the result to deduped file
    deduped_file = prompt_file.with_name(f"system_{round_num + 1}.deduped.md")
    prompt_file.rename(deduped_file)
