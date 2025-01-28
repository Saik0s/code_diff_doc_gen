# Implementation Plan

## Core Structure
```
code_diff_doc_gen/
├── src/
│   └── code_diff_doc_gen/
│       ├── __init__.py
│       ├── cli.py          # CLI interface
│       ├── llm.py         # LLM operations
│       ├── parser.py      # Code parsing
│       ├── generator.py   # Doc generation
│       ├── state_manager.py # State persistence
│       └── scorer.py      # LLM Scoring
├── tests/
│   └── test_core.py       # Essential tests
├── pyproject.toml
└── README.md
```

## State JSON Structure
```json
{
  "input_path": "path/to/input/code",
  "current_stage": "split", // "input", "split", "describe", "regenerate", "document", "llm_score", "output"
  "intermediate_results": {
    "split_code": [
      // ... split code blocks ...
    ],
    "descriptions": [
      // ... descriptions ...
    ],
    "regenerated_code": [
      // ... regenerated code blocks ...
    ],
    "diffs": [
      // ... diffs ...
    ],
    "documentation": "...", // generated documentation string
    "llm_score": {
      "score": 7, // or "Good"
      "feedback": "Documentation is clear and mostly complete..."
    }
  },
  "config": {
    // ... configuration parameters (if any) ...
  }
}
```


## Implementation Steps

1. Core Setup (Day 1)
   - Basic CLI structure
   - File input handling
   - LLM connection
   - State management setup (state_manager.py)

2. Main Features (Day 2-4)
   - Code splitting
   - Description generation
   - Code regeneration
   - Doc generation
   - State persistence implementation (saving and loading state)
   - LLM Scoring implementation (scorer.py and integration)

3. Testing & Polish (Day 5)
   - Core functionality tests (including state persistence and LLM scoring)
   - Error handling
   - CLI improvements

## Testing Focus
- Core functionality
- Input/output validation
- LLM integration
- End-to-end flow
- State persistence (saving, loading, resuming)
- LLM Scoring (prompt, score interpretation, output)


## Timeline
- Day 1: Project setup, CLI, State Management Setup
- Day 2: Core pipeline (Split, Describe)
- Day 3: Code Regeneration, Documentation, State Persistence Implementation
- Day 4: LLM Scoring Implementation
- Day 5: Testing and polish
