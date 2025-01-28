# src/code_diff_doc_gen/llm.py
import instructor
import openai
from dotenv import load_dotenv
import os
from loguru import logger
from typing import List, Optional
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI clients with API keys from environment
eval_client = instructor.patch(
    openai.OpenAI(
        api_key=os.getenv("EVAL_OPENAI_API_KEY"),
        base_url=os.getenv("EVAL_OPENAI_BASE_URL", "https://api.openai.com/v1"),
    ),
    mode=instructor.Mode.JSON,
)

target_client = instructor.patch(
    openai.OpenAI(
        api_key=os.getenv("TARGET_OPENAI_API_KEY"),
        base_url=os.getenv("TARGET_OPENAI_BASE_URL", "https://api.openai.com/v1"),
    ),
    mode=instructor.Mode.JSON,
)


class CodeBlock(BaseModel):
    code: str = Field(description="Code block")
    language: str = Field(
        description="Programming language of the code block", default="swift"
    )
    context: str = Field(
        description="Additional context about the code block's purpose", default=""
    )


class CodeSplitResult(BaseModel):
    code_blocks: List[CodeBlock] = Field(description="List of split code blocks")


class CodeDescription(BaseModel):
    description: str = Field(description="Description of the code block")
    key_components: List[str] = Field(
        description="List of key components and patterns used in the code"
    )
    dependencies: List[str] = Field(
        description="List of external dependencies and frameworks used",
        default_factory=list,
    )


class DocumentationScore(BaseModel):
    score: int = Field(
        description="Score representing the quality of documentation (1-10)"
    )
    feedback: str = Field(description="Detailed feedback on the documentation quality")
    improvement_suggestions: List[str] = Field(
        description="List of specific suggestions for improvement"
    )


def split_code_with_llm(code: str) -> CodeSplitResult:
    """Splits code into smaller blocks using LLM."""
    prompt = f"""
    Please split the following Swift code into logical blocks. Each block should be a complete,
    self-contained unit that represents a specific functionality or concept.

    For each block, identify:
    1. The code itself
    2. The context/purpose of the block
    3. Any key dependencies or frameworks used

    Return the result as a JSON object with a 'code_blocks' array, where each block has:
    - code: The actual code snippet
    - language: "swift"
    - context: A brief description of the block's purpose

    Code:
    {code}
    """
    logger.debug("Splitting code with LLM")
    try:
        response = eval_client.chat.completions.create(
            model=os.getenv("EVAL_MODEL_NAME", "gpt-4-turbo-preview"),
            response_model=CodeSplitResult,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Swift code analysis assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=4000,
        )
        return response
    except Exception as e:
        logger.error(f"Error splitting code: {str(e)}")
        # Return a single block as fallback
        return CodeSplitResult(
            code_blocks=[CodeBlock(code=code, context="Full file content")]
        )


def describe_code_block_with_llm(code_block: str) -> CodeDescription:
    """Generates a description for a code block using LLM."""
    prompt = f"""
    Please analyze the following Swift code block and provide:
    1. A clear, concise description of its functionality
    2. Key components and patterns used (e.g., SwiftUI views, Combine publishers, TCA reducers)
    3. External dependencies and frameworks used

    Return the result as a JSON object with:
    - description: A detailed explanation of the code
    - key_components: Array of key components and patterns
    - dependencies: Array of external dependencies

    Code Block:
    {code_block}
    """
    logger.debug("Describing code block with LLM")
    try:
        response = eval_client.chat.completions.create(
            model=os.getenv("EVAL_MODEL_NAME", "gpt-4-turbo-preview"),
            response_model=CodeDescription,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Swift code documentation expert.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2000,
        )
        return response
    except Exception as e:
        logger.error(f"Error describing code block: {str(e)}")
        return CodeDescription(
            description="Error generating description",
            key_components=["Error occurred"],
            dependencies=[],
        )


def regenerate_code_from_description_with_llm(description: str) -> CodeBlock:
    """Regenerates code from a description using LLM."""
    prompt = f"""
    Please regenerate Swift code based on the following description.
    Focus on following Swift and SwiftUI best practices and patterns.
    Ensure the code is idiomatic Swift and follows the style of The Composable Architecture if relevant.

    Return the result as a JSON object with:
    - code: The generated Swift code
    - language: "swift"
    - context: Brief explanation of what the code does

    Description:
    {description}
    """
    logger.debug("Regenerating code from description with LLM")
    try:
        response = target_client.chat.completions.create(
            model=os.getenv("TARGET_MODEL_NAME", "gpt-4-turbo-preview"),
            response_model=CodeBlock,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Swift code generation expert.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2000,
        )
        return response
    except Exception as e:
        logger.error(f"Error regenerating code: {str(e)}")
        return CodeBlock(
            code="// Error generating code",
            context="Error occurred during code generation",
        )


def score_documentation_with_llm(documentation: str) -> DocumentationScore:
    """Scores documentation quality using LLM."""
    prompt = f"""
    Please evaluate the quality of the following documentation for Swift code.
    Consider:
    1. Clarity and completeness of explanations
    2. Coverage of key Swift and SwiftUI concepts
    3. Usefulness for understanding The Composable Architecture patterns
    4. Technical accuracy and precision

    Return the result as a JSON object with:
    - score: A number from 1 to 10
    - feedback: Detailed explanation of the score
    - improvement_suggestions: Array of specific suggestions

    Documentation:
    {documentation}
    """
    logger.debug("Scoring documentation with LLM")
    try:
        response = eval_client.chat.completions.create(
            model=os.getenv("EVAL_MODEL_NAME", "gpt-4-turbo-preview"),
            response_model=DocumentationScore,
            messages=[
                {
                    "role": "system",
                    "content": "You are a documentation quality assessment expert.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2000,
        )
        return response
    except Exception as e:
        logger.error(f"Error scoring documentation: {str(e)}")
        return DocumentationScore(
            score=0,
            feedback="Error occurred during scoring",
            improvement_suggestions=["Unable to score documentation due to an error"],
        )
