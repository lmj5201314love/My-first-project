# Refactor Prompt: Preprocess Only

Task:

Refactor only the preprocessing flow for this local manufacturing analytics project.

Constraints:

- read and follow `AGENTS.md`, `docs/project_scope.md`, `.env.example`, and `.gitignore`
- keep `data_preparation+.py` unchanged as the legacy reference
- do not change business formulas unless explicitly required
- do not touch warehouse import logic in `data_import.py`
- move logic gradually into `src/preprocess.py`
- keep outputs compatible with `manufacturing_data_processed.csv`

Expected outcome:

- `src/preprocess.py` contains clear functions for loading raw data, deriving fields, and saving processed output
- legacy and new outputs can be compared safely
- changes are small and easy for a beginner to follow
- default execution stays in dry-run mode unless an explicit output path is provided

Required report:

1. files changed
2. what changed in each file
3. commands run
4. result summary
5. risks / assumptions
6. next recommended step
