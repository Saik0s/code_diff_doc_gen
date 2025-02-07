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

client = openai.AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"), base_url=os.getenv("OPENROUTER_BASE_URL")
)
model_name = "anthropic/claude-3.5-sonnet:beta"

ANALYSIS_PROMPT = """
Review and compare the code differences below identifying specific issues in the incorrect code.
Provide paired examples of legacy and modern code implementations, highlighting improvements in coding practices and dependency management.

<legacy>
{generated}
</legacy>

<modern>
{original}
</modern>

Provide code comparison blocks showing bad vs good code. Example format:

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

## Focus Areas:
- Deprecated library usage
- Outdated language syntax
- Only critical issues should be highlighted

## Evaluation Criteria
- Relevance: Examples must address common legacy patterns
- Clarity: Code pairs must be directly comparable
- Accuracy: Modern alternatives must follow current best practices
"""


async def call_llm(system: str, user: str, model: str = model_name) -> str:
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
        system = "You are a senior code review specialist analyzing patterns, standards and implementation quality. Evaluate submissions by contrasting problematic and improved code examples only. Skip commentary and peripheral text."
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
        user = f"What 1 paragraph task description would result in exactly following code if this task was completed by a developer? Don't go into technical details, just describe the functionality and libraries used.\n\n<code>\n{content}\n</code>"

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
    deduped_file = prompt_file.with_name(f"system_{round_num + 1}.deduped.md")
    deduped_file.write_text(prompt_file.read_text())

    # Initialize aider components
    model = Model("sonnet")
    io = InputOutput(yes=True)
    coder = Coder.create(
        main_model=model, fnames=[str(deduped_file)], io=io, use_git=False
    )

    # Run deduplication
    coder.run(
        """\
Generate optimized version that:
- Eliminates duplicate or low-value code blocks by consolidating similar patterns.
- Focuses solely on high-impact paired examples (bad code first, good code second).

Output format: Only minimal paired code blocks separated by two blank lines, self-documenting and consistently formatted.

Execute immediately.
"""
    )
