test:
	rm -rf .codescribe
	uv run pytest
	uv run code-diff-doc-gen init
	uv run code-diff-doc-gen process tests/data

install:
	uv sync
