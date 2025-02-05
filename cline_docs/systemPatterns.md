# System Patterns

## Structure
```
.codescribe/
  descriptions.toml       # file descriptions
  prompts/               # system prompts
    system_0.md          # base prompt
    system_N.md          # with examples
  generated/             # output code
    round_N/            # by round
```

## Components
1. **File Processor**
   - Read source files
   - Create descriptions with Guidance
   - Store in TOML

2. **Generator**
   - Read descriptions
   - Use system prompt
   - Generate code with Guidance
   - Store output

3. **Diff Creator**
   - Compare code
   - Format examples
   - Update prompts

## Flow
```
Files -> Descriptions (Guidance) -> Generated Code (Guidance) -> Diffs -> New Prompt -> Repeat
```

## Guidance Usage
- Use Guidance for controlled generation
- Constrain outputs with regex/selects
- Automatic prompt improvement
- Simple error handling
