# src/code_diff_doc_gen/llm.py
import instructor
import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment
client = instructor.from_openai(
    openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
)


def split_code_with_llm(code: str) -> CodeSplitResult:
    """Splits code into smaller blocks using LLM."""
    prompt = f"""
        Please split the following code into logical blocks.

        Code:
        {code}
        """
    return client.chat.create(
        model="gpt-4o-preview",  # Choose an appropriate model
        messages=[{"role": "user", "content": prompt}],
        response_model=CodeSplitResult,
    )


def describe_code_block_with_llm(code_block: str) -> CodeDescription:
    """Generates a description for a code block using LLM."""
    prompt = f"""
        Please provide a concise description for the following code block.

        Code Block:
        {code_block}
        """
    return client.chat.create(
        model="gpt-4o-preview",  # Choose an appropriate model
        messages=[{"role": "user", "content": prompt}],
        response_model=CodeDescription,
    )


def regenerate_code_from_description_with_llm(description: str) -> CodeBlock:
    """Regenerates code from a description using LLM."""
    prompt = f"""
        Please regenerate the code based on the following description.

        Description:
        {description}
        """
    return client.chat.create(
        model="gpt-4o-preview",  # Choose an appropriate model
        messages=[{"role": "user", "content": prompt}],
        response_model=CodeBlock,
    )


def score_documentation_with_llm(documentation: str) -> DocumentationScore:
    """Scores documentation quality using LLM."""
    prompt = f"""
        Please score the quality of the following documentation and provide feedback.

        Documentation:
        {documentation}
        """
    return client.chat.create(
        model="gpt-4o-preview",  # Choose an appropriate model
        messages=[{"role": "user", "content": prompt}],
        response_model=DocumentationScore,
    )


from pydantic import BaseModel, Field


class DocumentationScore(BaseModel):
    score: int = Field(description="Score representing the quality of documentation")
    feedback: str = Field(description="Feedback on the documentation quality")


class CodeDescription(BaseModel):
    description: str = Field(description="Description of the code block")


class CodeBlock(BaseModel):
    code: str = Field(description="Code block")


class CodeSplitResult(BaseModel):  # Example for split_code_with_llm, adjust as needed
    code_blocks: list[CodeBlock] = Field(description="List of split code blocks")
