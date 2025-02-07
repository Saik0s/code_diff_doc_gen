# Code Diff Doc Gen

Code Diff Doc Gen is a tool for generating and analyzing code differences with LLM assistance. It automates the process of documenting code changes, generating code implementations from descriptions, and comparing original and generated code to highlight differences.

## Features

-   Automates code documentation and analysis using LLMs
-   Generates code implementations from natural language descriptions
-   Compares original and generated code, highlighting key differences
-   Provides a clear and easy-to-use CLI interface
-   Supports multiple programming languages
-   Uses a prompt improvement system to refine code generation

## Installation

1.  Install `uv`:

    ```bash
    pip install uv
    ```

2.  Clone the repository:

    ```bash
    git clone https://github.com/your-username/code-diff-doc-gen.git
    cd code-diff-doc-gen
    ```

3.  Install dependencies:

    ```bash
    uv sync
    ```

## Usage

1.  Set your OpenAI API key:

    ```bash
    export OPENAI_API_KEY=your-key-here
    ```

    You can also set the `OPENROUTER_API_KEY` and `OPENROUTER_BASE_URL` environment variables if you are using OpenRouter.

2.  Run the tool:

    ```bash
    python -m code_diff_doc_gen run ./src --round 1
    ```

    This command will process the source code in the `./src` directory, generate code implementations, analyze the changes, and generate system prompts for the next round of code generation.

## CLI Commands

-   `run`: Processes source code, generates code, analyzes changes, and generates system prompts.

    ```bash
    python -m code_diff_doc_gen run <source_dir> --round <round_num>
    ```

    -   `<source_dir>`: The directory containing the source code to process.
    -   `--round <round_num>`: The generation round number (default: 0).

    See [cline_docs/cli_commands.md](cline_docs/cli_commands.md) for more details.

## Output

The tool creates a `.codescribe` directory with the following structure:

-   `descriptions/`: Contains descriptions of the processed source files.
-   `generated/`: Contains the generated code implementations for each round.
-   `analysis/`: Contains diffs and analysis reports comparing original and generated code.
-   `prompts/`: Contains system prompts used for code generation.

## Development

1.  Clone the repository:

    ```bash
    git clone https://github.com/your-username/code-diff-doc-gen.git
    cd code-diff-doc-gen
    ```

2.  Install dependencies:

    ```bash
    uv sync
    ```

3.  Run tests:

    ```bash
    pytest
    ```

4.  Format code:

    ```bash
    black src tests
    ```

5.  Submit pull requests:

    -   Create a new branch for your changes.
    -   Make your changes and commit them with clear and concise messages.
    -   Submit a pull request to the main branch.

## Contributing

We welcome contributions to Code Diff Doc Gen! If you have any ideas or suggestions, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.

## Credits

-   This project was created by [Your Name].
-   Special thanks to the OpenAI team for providing the powerful language models used in this tool.
