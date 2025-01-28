Product Overview:
A terminal app with a modern UI that generates documentation for updating language models' understanding of library versions.

How It Works:
	1. Source file selection: provide path to files or folder
	2. Code Splitting: LLM1 evaluates and splits code into meaningful pieces
	3. Description Generation: LLM1 generates descriptions for each code piece
	4. Code Regeneration: Target LLM2 regenerates code from descriptions
	5. Documentation Creation: LLM1 criticises differences and compiles that into documentation doc
	6. Validation Round: LLM2 generates code from descriptions again, but this time documentation is added to system prompt
	7. Final Check: LLM1 performs evaluation of the result and performs steps 5-7 again if needed until result is satisfying

Purpose:
A terminal-based solution for aligning LLM outputs with library versions through automated documentation and validation.

use `instructor` library for structured output

