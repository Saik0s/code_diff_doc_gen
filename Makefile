test:
	rm -rf .codescribe
	uv run pytest
	uv run code-diff-doc-gen tests/data

install:
	uv sync
