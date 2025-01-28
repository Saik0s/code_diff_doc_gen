# tests/test_llm.py
from code_diff_doc_gen import llm


def test_score_documentation_with_llm():
    documentation = "This is a sample documentation."
    result = llm.score_documentation_with_llm(documentation)
    assert isinstance(result, llm.DocumentationScore)


def test_describe_code_block_with_llm():
    code_block = "def hello(): return 'hello'"
    result = llm.describe_code_block_with_llm(code_block)
    assert isinstance(result, llm.CodeDescription)


def test_split_code_with_llm():
    code = "def hello(): return 'hello'\\nclass World: pass"
    result = llm.split_code_with_llm(code)
    assert isinstance(result, llm.CodeSplitResult)


def test_regenerate_code_from_description_with_llm():
    description = "A function that returns hello"
    result = llm.regenerate_code_from_description_with_llm(description)
    assert isinstance(result, llm.CodeBlock)
