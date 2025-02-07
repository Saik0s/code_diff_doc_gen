"""LLM operations for code analysis and generation."""

import os
from typing import Any, Dict, List, Optional
import openai
from loguru import logger
from pathlib import Path

# Initialize OpenAI client
client = openai.AsyncOpenAI()
reasoning_model = "aion-labs/aion-1.0"
large_output_model = "mistralai/codestral-2501"

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
    for attempt in range(3):
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            break
        except Exception as e:
            if attempt == 2:  # Last attempt
                raise
            logger.warning(f"Attempt {attempt + 1} failed, retrying...")

    return response.choices[0].message.content


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
    prompt_file = Path(".codescribe") / "prompts" / f"system_{round_num + 1}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"System prompt file not found for round {round_num}")

    prompt = prompt_file.read_text()

    deduped_prompt = await call_llm(
        system="""You're a code analysis tool focused on removing highly similar code examples while preserving distinct ones.
Your task is to:
1. Compare code blocks within the text
2. Remove only code blocks (both 'bad' and 'good' pairs) that are extremely similar in structure and functionality keeping only one of them
3. Preserve code blocks that demonstrate unique refactoring approaches or distinct differences
4. Output the complete and cleaned text without any additional commentary, do not wrap the text in <text> tags""",
        user=f"Process this file and remove only highly similar/repetitive good/bad code blocks pairs:\n\n<text>\n{prompt}\n</text>",
        model=large_output_model,
    )

    new_prompt_file = prompt_file.with_name(f"system_{round_num + 1}.deduped.md")
    new_prompt_file.write_text(deduped_prompt)
