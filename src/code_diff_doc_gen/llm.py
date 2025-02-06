"""LLM operations for code analysis and generation."""

import os
from typing import Any, Dict, List, Optional
import openai
from loguru import logger
from pathlib import Path

# Initialize OpenAI client
client = openai.AsyncOpenAI(
    base_url=os.getenv("TARGET_OPENAI_BASE_URL"),
    api_key=os.getenv("TARGET_OPENAI_API_KEY"),
)
model = os.getenv("TARGET_MODEL_NAME")

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


async def call_llm(system: str, user: str) -> str:
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )

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
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert code reviewer focusing on "
                    "design patterns, best practices, and code quality. Output only the bad/good code pairs, no other text.",
                },
                {
                    "role": "user",
                    "content": ANALYSIS_PROMPT.format(
                        original=original, generated=generated
                    ),
                },
            ],
        )

        analysis = response.choices[0].message.content
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
        messages = [
            {
                "role": "system",
                "content": system_prompt
                or "You are an expert software developer. "
                "Generate clean, efficient, and well-documented code. Output only the code, no other text.",
            },
            {
                "role": "user",
                "content": f"Generate code for the following description:\n\n{description}",
            },
        ]

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
        )

        return response.choices[0].message.content

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
        # Generate description
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert code analyst and task description writer.",
                },
                {
                    "role": "user",
                    "content": f"What 3 paragraphs max task description would result in exactly following code if this task was completed by a developer:\n\n{content}",
                },
            ],
        )

        return response.choices[0].message.content.strip()

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


async def deduplicate_generated_system_prompt(round_num: int) -> str:
    """Deduplicate the generated system prompt.

    Args:
        round_num: Current generation round number

    Returns:
        Deduplicated system prompt
    """
    try:
        prompt_file = Path(".codescribe") / "prompts" / f"system_{round_num}.md"
        if not prompt_file.exists():
            logger.warning(f"System prompt file not found for round {round_num}")
            return ""

        prompt = prompt_file.read_text()

        # Use LLM to deduplicate content while preserving meaning
        deduped_prompt = await call_llm(
            system="You are an expert at removing redundant and duplicate code examples.",
            user=f"Remove any duplicate or redundant code blocks from the provided text while maintaining all unique information.\n\n<input>\n{prompt}\n</input>",
        )

        return deduped_prompt

    except Exception as e:
        logger.exception(e)
        raise
