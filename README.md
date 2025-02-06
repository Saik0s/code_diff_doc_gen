# Code Diff Doc Gen

Generate and analyze code differences with LLM assistance.

## Features

- Process source files in parallel
- Generate code implementations
- Compare and analyze differences
- Simple state management
- Clear CLI interface

## Installation

```bash
rye sync
```

## Usage

Set your OpenAI API key:
```bash
export OPENAI_API_KEY=your-key-here
```

Run the complete process:
```bash
code-diff-doc-gen run ./src --round 1
```

Check status:
```bash
code-diff-doc-gen status
```

Reset failed steps:
```bash
code-diff-doc-gen reset
```

## Output

The tool creates a `.codescribe` directory with:
- `descriptions/` - Processed file descriptions
- `generated/` - Generated code implementations
- `analysis/` - Diffs and analysis reports

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black src tests
