## CLI Command: `run`

The `run` command is the main entry point for the code generation and analysis process. It orchestrates the entire workflow, from processing the source files to generating documentation and analyzing the differences between the original and generated code.

**Usage:**

```bash
python -m code_diff_doc_gen run <source_dir> [--round <round_num>]
```

**Arguments:**

*   `source_dir` (required): The path to the directory containing the source code files. This directory will be recursively searched for files.

**Options:**

*   `--round <round_num>` (optional):  Specifies the generation round number. Defaults to 0. This number is used to organize the output files in the `.codescribe` directory.

**Functionality:**

The `run` command performs the following steps:

1.  **Workspace Initialization:** Ensures that the necessary workspace directories (`.codescribe/descriptions`, `.codescribe/generated`, `.codescribe/analysis`) exist. If not, they are created.

2.  **File Processing:** Calls the `process_files` function (from `src/code_diff_doc_gen/processor.py`) to extract descriptions from the source code files in the specified `source_dir`. These descriptions are stored in the `.codescribe/descriptions` directory.

3.  **Code Generation:** Calls the `generate_code` function (from `src/code_diff_doc_gen/generator.py`) to generate code based on the extracted descriptions. The generated code is stored in the `.codescribe/generated/round_<round_num>` directory.

4.  **Difference Analysis:** Calls the `compare_files` function (from `src/code_diff_doc_gen/diff.py`) to compare the original source files with the generated code. The analysis of the differences is stored in the `.codescribe/analysis/round_<round_num>` directory.

5.  **System Prompt Generation:** Calls the `generate_system_prompt_from_analyses` function (from `src/code_diff_doc_gen/llm.py`) to create a system prompt for the next round of code generation, based on the analysis of the differences. This prompt is saved in the `.codescribe/prompts` directory.

6. **Error Handling:** Catches any exceptions that occur during the process and logs them using Loguru. If an exception occurs, the program exits with a non-zero exit code.

**Example:**

To process the source code in the `my_project` directory and perform the first round of generation (round 0), you would use the following command:

```bash
python -m code_diff_doc_gen run my_project
```

To perform the second round of generation (round 1), you would use:

```bash
python -m code_diff_doc_gen run my_project --round 1
```
