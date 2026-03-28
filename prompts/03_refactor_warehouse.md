# Refactor Prompt: Warehouse Import Only

Task:

Refactor only the warehouse import flow for this local manufacturing analytics project.

Constraints:

- read and follow `AGENTS.md`, `docs/project_scope.md`, `.env.example`, and `.gitignore`
- keep `data_import.py` unchanged as the legacy reference unless explicitly asked otherwise
- do not change preprocessing business logic
- move logic gradually into `src/warehouse.py`
- prepare for safer credential handling and safer import execution

Priority goals:

- remove reliance on hard-coded secrets in new code
- make destructive actions opt-in in new code
- preserve compatibility with the current processed CSV contract

Expected outcome:

- `src/warehouse.py` contains modular placeholders or migrated helpers for connection setup, dimension building, fact building, and import orchestration
- warehouse safety risks are reduced in the new path without rewriting the whole repo

Required report:

1. files changed
2. what changed in each file
3. commands run
4. result summary
5. risks / assumptions
6. next recommended step
