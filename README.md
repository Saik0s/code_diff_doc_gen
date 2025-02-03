# CodeScribe

Create a python script that:
1. Takes source files as input
2. Creates descriptions explaining what each file does
3. Generates code from descriptions
4. Creates difference examples between original and generated code
5. Asks user if they want another generation attempt
6. Repeats with improved system prompt

## File Structure
```
.codescribe/
  descriptions.toml       # file descriptions
  prompts/
    system_0.md          # base prompt
    system_1.md          # base + round 1 examples
    system_2.md          # base + rounds 1-2 examples
  generated/
    round_1/            # first generation attempt
    round_2/            # second generation attempt
```

## System Prompt Format
Each `system_N.md` contains:
1. Base instruction: "You are an expert in the detected language and frameworks. Generate code from the provided description."
2. Code comparison blocks:
```
// Bad
{generated_code}

// Good
{original_code}
```

No additional text or explanations - just instruction and code blocks.

## Process
1. Create initial system prompt
2. Generate code from descriptions
3. Compare original vs generated
4. Show differences to user
5. If user wants another round:
   - Add difference blocks to system prompt
   - Generate new code
   - Repeat from step 3

Keep it simple - single script with core functions for each step.
