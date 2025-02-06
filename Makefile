test:
	uv run pytest

test-generate:
	rm -rf .codescribe
	uv run code-diff-doc-gen tests/data

install:
	uv sync
