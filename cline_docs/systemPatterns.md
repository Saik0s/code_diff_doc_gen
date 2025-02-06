# System Patterns

## Architecture
```
Files -> Descriptions (OpenAI) -> Generated Code (OpenAI) -> Diffs -> New Prompt -> Repeat
```

## Components

1. **LLM Client (llm.py)**
   - OpenAI API wrapper
   - Message handling
   - Error management
   - Configuration

2. **File Processor (processor.py)**
   - Read source files
   - Create descriptions with OpenAI
   - Store in TOML format
   - Handle file operations

3. **Code Generator (generator.py)**
   - Read descriptions
   - Use system prompts
   - Generate code with OpenAI
   - Store generated code

4. **Diff Creator (diff.py)**
   - Compare original vs generated
   - Format examples
   - Update system prompts
   - Track improvements

## Directory Structure
```
.codescribe/
  descriptions.toml       # File descriptions
  prompts/               # System prompts
    system_0.md          # Base prompt
    system_N.md          # With examples
  generated/             # Output code
    round_N/            # By round
```

## Workflow
1. **Initialization**
   - Set up workspace
   - Configure OpenAI client
   - Verify environment

2. **Processing**
   - Read source files
   - Generate descriptions
   - Store in TOML

3. **Generation**
   - Read descriptions
   - Apply system prompt
   - Generate code
   - Save output

4. **Comparison**
   - Create diffs
   - Format examples
   - Update prompts
   - Track progress

## OpenAI Usage
- Use GPT-4 for consistency
- Zero temperature for deterministic output
- Structured prompts for control
- Error handling and retries
- Token limit management

## Best Practices
- Type hints everywhere
- Proper error handling
- Structured logging
- Clean code organization
- Test coverage
- Documentation
