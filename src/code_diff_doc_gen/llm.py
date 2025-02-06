"""LLM operations for code analysis and generation."""

from typing import Any, Dict, List, Optional
import openai
from loguru import logger
from pathlib import Path

# Initialize OpenAI client
client = openai.AsyncOpenAI()

ANALYSIS_PROMPT = """
Review and compare the code differences below, highlighting API and library usage issues. Original code represents the correct implementation.

Original:
{original}

Generated:
{generated}

Provide code comparison blocks showing problematic vs correct patterns. Example format:

// Bad Code
function processUnknownData(x: any) {{
  // Anti-pattern
}}

// Good Code
function validateUserProfile(profile: UserProfile): ValidationResult {{
  // Type-safe implementation
}}

Focus on:
- API misuse
- Library integration errors
- Type safety issues
- Best practice violations

Show multiple examples if needed.
"""


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
            model="o3-mini",
            messages=[
                {
                    "role": "developer",
                    "content": "You are an expert code reviewer focusing on "
                    "design patterns, best practices, and code quality.",
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
                "role": "developer",
                "content": system_prompt
                or "You are an expert software developer. "
                "Generate clean, efficient, and well-documented code.",
            },
            {
                "role": "user",
                "content": f"Generate code for the following description:\n\n{description}",
            },
        ]

        response = await client.chat.completions.create(
            model="o3-mini",
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
        # System prompt for description generation
        system_prompt = """You are an expert code analyst. Create a detailed description of the code that includes:
1. Overall purpose and functionality
2. Key components and their relationships
3. Important algorithms or patterns used
4. External dependencies and requirements
5. Any notable implementation details

Focus on being precise and technical while maintaining clarity."""

        # Generate description
        response = await client.chat.completions.create(
            model="o3-mini",
            messages=[
                {
                    "role": "developer",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": f"Analyze and describe this code:\n\n{content}",
                },
            ],
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.exception(e)
        raise
