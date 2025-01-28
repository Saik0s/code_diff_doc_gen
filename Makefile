test:
	uv run pytest

run-swift-test:
	rm -rf output.md state.json
	uv run code-diff-doc-gen tests/data --output-file output.md --state-file state.json

install:
	uv sync
