# Test Strategy

## Core Tests
```python
# tests/test_core.py

def test_file_input():
    """Test file reading and validation"""

def test_code_splitting():
    """Test code block separation"""

def test_llm_integration():
    """Test LLM API interaction"""

def test_doc_generation():
    """Test documentation creation"""

def test_end_to_end():
    """Test complete pipeline"""
```

## Test Data
```
tests/data/
└── swift-composable-architecture-Examples-CaseStudies-SwiftUICaseStudies/ # Swift files for testing
```

## Swift File Tests
- **Objective**: To ensure the tool can correctly process and document Swift code.
- **Test Files**: Utilize the Swift files located in `tests/data/swift-composable-architecture-Examples-CaseStudies-SwiftUICaseStudies/`.
- **Test Scenarios**:
    1. **Basic Parsing**: Verify that the parser can handle Swift syntax and extract relevant code blocks (classes, functions, structs, etc.).
    2. **Documentation Generation**: Test if documentation can be generated for Swift code elements.
    3. **End-to-End Pipeline**: Ensure the entire pipeline (parsing -> LLM interaction -> documentation) works correctly for Swift files.
- **Test Structure**:
    ```python
    # tests/test_swift.py

    def test_swift_file_parsing():
        """Test parsing of swift files"""

    def test_swift_doc_generation():
        """Test documentation generation for swift files"""

    def test_swift_end_to_end():
        """Test complete pipeline for swift files"""
