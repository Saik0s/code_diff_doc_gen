# System Patterns

## Pipeline
```
[Input] -> [State Load] -> [Split] -> [State Save] -> [Describe] -> [State Save] -> [Regenerate] -> [State Save] -> [Document] -> [State Save] -> [LLM Score] -> [State Save] -> [Output]
```

## Components

### Input Handler
- File/directory reading
- Code preprocessing

### State Management
- Load application state from JSON file at startup.
- Save application state to JSON file after each pipeline stage.
- Handle state initialization if no state file exists.

### LLM Operations
- Code splitting (LLM1)
- Description generation (LLM1)
- Code regeneration (LLM2)
- LLM Scoring (LLM1) - Score the quality of generated documentation.

### Documentation
- Difference analysis
- Doc generation
- Incorporate LLM score into the final documentation output.

## Error Handling
- Input validation
- LLM error recovery
- Clear error messages
- State loading/saving error handling.
