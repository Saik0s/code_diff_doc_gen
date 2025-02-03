test:
	uv run pytest

run-swift-test:
	rm -rf .codescribe
	uv run code-diff-doc-gen tests/data

install:
	uv sync
