# tests/test_llm.py
from code_diff_doc_gen import llm

SAMPLE_SWIFT_CODE = """
import ComposableArchitecture
import SwiftUI

@Reducer
struct Counter {
  @ObservableState
  struct State: Equatable {
    var count = 0
  }

  enum Action {
    case decrementButtonTapped
    case incrementButtonTapped
  }

  var body: some Reducer<State, Action> {
    Reduce { state, action in
      switch action {
      case .decrementButtonTapped:
        state.count -= 1
        return .none
      case .incrementButtonTapped:
        state.count += 1
        return .none
      }
    }
  }
}
"""


def test_split_code_with_llm():
    result = llm.split_code_with_llm(SAMPLE_SWIFT_CODE)
    assert isinstance(result, llm.CodeSplitResult)
    assert len(result.code_blocks) > 0
    for block in result.code_blocks:
        # Verify blocks are at least 10 lines
        assert len(block.code.strip().split("\n")) >= 10
        assert block.language == "swift"
        assert block.context != ""


def test_split_code_with_llm_and_library():
    result = llm.split_code_with_llm(SAMPLE_SWIFT_CODE, "ComposableArchitecture")
    assert isinstance(result, llm.CodeSplitResult)
    assert len(result.code_blocks) > 0
    for block in result.code_blocks:
        # Verify blocks mention library
        assert "ComposableArchitecture" in block.context
        assert len(block.code.strip().split("\n")) >= 10


def test_describe_code_block_with_llm():
    code_block = SAMPLE_SWIFT_CODE
    result = llm.describe_code_block_with_llm(code_block)
    assert isinstance(result, llm.CodeDescription)
    assert len(result.description) > 0
    assert len(result.key_components) > 0
    assert len(result.dependencies) > 0
    assert "SwiftUI" in result.dependencies


def test_describe_code_block_with_llm_and_library():
    code_block = SAMPLE_SWIFT_CODE
    result = llm.describe_code_block_with_llm(code_block, "ComposableArchitecture")
    assert isinstance(result, llm.CodeDescription)
    assert "ComposableArchitecture" in result.description
    assert "ComposableArchitecture" in result.dependencies
    assert any("Reducer" in comp for comp in result.key_components)


def test_score_documentation_with_llm():
    documentation = """
    This Counter example demonstrates the core concepts of The Composable Architecture:
    - State management using @ObservableState
    - Action handling with Reducer
    - SwiftUI integration with Store
    """
    result = llm.score_documentation_with_llm(documentation)
    assert isinstance(result, llm.DocumentationScore)
    assert result.score > 0
    assert len(result.feedback) > 0
    assert len(result.improvement_suggestions) > 0


def test_regenerate_code_from_description_with_llm():
    description = """
    A Counter reducer using The Composable Architecture that manages an integer count state.
    It handles increment and decrement actions using a Reducer, and integrates with SwiftUI
    through the Store pattern.
    """
    result = llm.regenerate_code_from_description_with_llm(
        description, "ComposableArchitecture"
    )
    assert isinstance(result, llm.CodeBlock)
    assert len(result.code.strip().split("\n")) >= 10
    assert "ComposableArchitecture" in result.code
