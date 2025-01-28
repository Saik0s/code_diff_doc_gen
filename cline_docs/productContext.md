# Product Context

## Purpose
Terminal app to generate documentation for aligning LLM code generation with library versions.

## Flow
1. Input: Get source code files
2. Split: Break code into pieces (LLM1)
3. Describe: Generate descriptions (LLM1)
4. Regenerate: Create code from descriptions (LLM2)
5. Document: Analyze differences, create docs
6. Validate: Test with docs in prompt
7. Iterate: Repeat 5-7 until satisfied

## Success Metrics
- Accurate code splitting
- Clear documentation
- Successful validation
- Fast execution
