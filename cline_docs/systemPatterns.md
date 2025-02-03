# System Patterns

## Core Architecture

The CodeScribe system is structured around three main components with clear responsibilities:

### 1. File Processing System
- **Current State**: Basic implementation
- **Components**:
  - File reading (✓ Implemented)
  - Language detection (⚠️ Hardcoded to Swift)
  - Description generation (⚠️ Placeholder)
  - TOML storage (✓ Implemented)

### 2. Generation System
- **Current State**: Framework only
- **Components**:
  - System prompts (✓ Implemented)
  - Code generation (⚠️ Placeholder)
  - Output validation (⚠️ Not started)
  - Result storage (✓ Implemented)

### 3. Comparison System
- **Current State**: Basic implementation
- **Components**:
  - Diff generation (✓ Implemented)
  - Example formatting (✓ Implemented)
  - Prompt updates (✓ Implemented)
  - Quality tracking (⚠️ Not started)

## Data Flow

```
Source Files → Descriptions → Generated Code → Comparisons → Updated Prompts
    ↑                                                            |
    |----------------------------------------------------------|
                            (Next Round)
```

### Current Implementation

1. **Input Processing**
   ```python
   # Implemented
   - Read source files
   - Store in memory
   - Save descriptions

   # Needed
   - Language detection
   - AI description generation
   - Validation
   ```

2. **Code Generation**
   ```python
   # Implemented
   - Prompt management
   - Result storage
   - Round tracking

   # Needed
   - LLM integration
   - Code generation
   - Output validation
   ```

3. **Comparison Logic**
   ```python
   # Implemented
   - Basic diff generation
   - Example formatting
   - Prompt updates

   # Needed
   - Quality metrics
   - Improvement tracking
   - Advanced diff analysis
   ```

## File Structure

```
.codescribe/
  descriptions.toml       # ✓ Implemented
  prompts/               # ✓ Implemented
    system_0.md          # ✓ Base prompt
    system_N.md          # ✓ Round prompts
  generated/             # ✓ Implemented
    round_N/            # ✓ Round storage
```

## Implementation Details

### 1. File Processing
- Currently uses basic file I/O
- TOML for structured storage
- Needs AI integration for descriptions
- Requires language detection

### 2. Code Generation
- Basic prompt management
- Round-based storage
- Needs LLM integration
- Requires validation

### 3. Comparison System
- Uses Python's difflib
- Simple text comparison
- Example-based learning
- Needs quality metrics

## Testing Strategy

### Current Setup
- Basic directory structure
- Swift test files available
- No tests implemented

### Required Components
1. **Unit Tests**
   - File operations
   - TOML handling
   - Diff generation
   - Prompt management

2. **Integration Tests**
   - Full workflow
   - AI integration
   - Round management
   - Error handling

3. **Test Data**
   - Swift examples
   - Multiple languages
   - Edge cases
   - Error scenarios

## Future Considerations

### 1. Extensibility
- Language-specific processors
- Custom prompt templates
- Pluggable AI services
- Advanced diff algorithms

### 2. Improvements
- Multi-language support
- Better descriptions
- Quality metrics
- Performance optimization

### 3. Infrastructure
- Error recovery
- Progress tracking
- Validation rules
- Monitoring system
