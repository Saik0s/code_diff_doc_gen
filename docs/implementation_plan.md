# Implementation Plan: Integrating `instructor` Library for Structured LLM Responses

**1. Project Setup and Dependencies**

*   **Goal**: Prepare the project environment by adding necessary dependencies.
*   **Steps**:
    *   Modify `pyproject.toml` to include `instructor`, `openai`, and `python-dotenv` as dependencies. This ensures that these libraries are available in our project.
    *   Create `.env.example` and `.env` files for environment variable management.
    *   Run `uv pip install` to update the project dependencies and install the newly added libraries.

    ```toml
    [tool.poetry.dependencies]
    python = "^3.11"
    openai = "^1.0" # or later
    instructor = "^0.2" # or later
    pydantic = "^2.0" # Ensure pydantic is compatible
    python-dotenv = "^1.0.0" # For environment variable management
    ```

    ```env
    # .env.example
    OPENAI_API_KEY=your-api-key-here
    ```

**2. Initialize `instructor` Client**

*   **Goal**: Set up the `instructor` client within `src/code_diff_doc_gen/llm.py` to wrap the OpenAI client.
*   **Steps**:
    *   In `src/code_diff_doc_gen/llm.py`, import `instructor`, `openai`, and `dotenv`.
    *   Load environment variables using `dotenv`.
    *   Initialize the `instructor` client using `instructor.from_openai(openai.OpenAI())`. This will enable the use of `response_model` in our LLM calls.

    ```python
    # src/code_diff_doc_gen/llm.py
    import instructor
    import openai
    from dotenv import load_dotenv
    import os

    # Load environment variables from .env file
    load_dotenv()

    # Initialize OpenAI client with API key from environment
    client = instructor.from_openai(openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
    ```

**3. Define Pydantic Models for LLM Responses**

*   **Goal**: Create Pydantic models to define the structure of responses for each LLM function.
*   **Steps**:
    *   For each function in `llm.py` (`split_code_with_llm`, `describe_code_block_with_llm`, `regenerate_code_from_description_with_llm`, `score_documentation_with_llm`), define a corresponding Pydantic model.
    *   These models will specify the fields and their types for the expected structured output. For example, for `score_documentation_with_llm`, we might define a model with `score` as an integer and `feedback` as a string, similar to the `Judgment` model in the example.

    ```python
    # src/code_diff_doc_gen/llm.py
    from pydantic import BaseModel, Field

    class DocumentationScore(BaseModel):
        score: int = Field(description="Score representing the quality of documentation")
        feedback: str = Field(description="Feedback on the documentation quality")

    class CodeDescription(BaseModel):
        description: str = Field(description="Description of the code block")

    class CodeBlock(BaseModel):
        code: str = Field(description="Code block")

    class CodeSplitResult(BaseModel): # Example for split_code_with_llm, adjust as needed
        code_blocks: list[CodeBlock] = Field(description="List of split code blocks")
    ```

**4. Update LLM Functions to Use `instructor` and Pydantic Models**

*   **Goal**: Modify the placeholder functions in `llm.py` to use the `instructor` client and the defined Pydantic models.
*   **Steps**:
    *   For each function, update the function definition to use `client.chat.create` with the `response_model` parameter set to the corresponding Pydantic model.
    *   Implement the actual LLM prompting and logic within each function to achieve the desired functionality (splitting code, describing code blocks, regenerating code, scoring documentation).
    *   Ensure that the return type annotation of each function matches the Pydantic model.

    ```python
    # src/code_diff_doc_gen/llm.py
    def score_documentation_with_llm(documentation: str) -> DocumentationScore:
        """Scores documentation quality using LLM and returns a structured DocumentationScore."""
        prompt = f"""
        Please score the quality of the following documentation and provide feedback.

        Documentation:
        {documentation}
        """
        return client.chat.create(
            model="gpt-4o-mini", # Choose an appropriate model
            messages=[{"role": "user", "content": prompt}],
            response_model=DocumentationScore,
        )

    def describe_code_block_with_llm(code_block: str) -> CodeDescription:
        """Generates a description for a code block using LLM and returns a structured CodeDescription."""
        prompt = f"""
        Please provide a concise description for the following code block.

        Code Block:
        {code_block}
        """
        return client.chat.create(
            model="gpt-4o-mini", # Choose an appropriate model
            messages=[{"role": "user", "content": prompt}],
            response_model=CodeDescription,
        )
    ```

**5. Testing and Validation**

*   **Goal**: Ensure that the integration works correctly and that the LLM functions return structured data as defined by the Pydantic models.
*   **Steps**:
    *   Write unit tests for each LLM function to validate that they return objects of the correct Pydantic model type and that the data within these objects is as expected.
    *   Run integration tests to ensure that the structured outputs from `llm.py` are correctly used in other parts of the `code_diff_doc_gen` system.
    *   Add tests to verify environment variables are properly loaded and handled.

**6. Documentation Update**

*   **Goal**: Document the changes made and the usage of the `instructor` library in the project documentation.
*   **Steps**:
    *   Update `cline_docs/systemPatterns.md` and `cline_docs/techContext.md` to reflect the use of `instructor` for LLM response structuring.
    *   Document the Pydantic models defined and their purpose.
    *   Explain how to use the updated LLM functions and how they return structured data.
    *   Include instructions for setting up environment variables using `.env` file.
