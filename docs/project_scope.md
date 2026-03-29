# Project Scope

## Goal

Refactor the current manufacturing analytics project into a modular, maintainable local codebase that can later support a clear manufacturing analytics presentation workflow.

## Current stage

- legacy raw, processed, and import scripts still exist as source references
- safe-first preprocess and warehouse entrypoints now exist under `src/`
- processed CSV contract tests and warehouse structure tests are in place
- first-pass MySQL schema and view definitions are documented under `sql/`
- README, data dictionary, run guide, and analysis report template are in place
- a minimal notebook / EDA skeleton now exists under `notebooks/`

## Immediate next milestones

1. complete the notebook `Dataset Overview` section with small, real outputs
2. expand equipment / line KPI analysis inside the notebook
3. expand shift and failure analysis inside the notebook
4. draft concise findings and limitations for project presentation
5. later consider BI-style outputs or resume-facing presentation material

## Success criteria

- safe-first entrypoints remain aligned with legacy outputs
- tests continue protecting current data and warehouse contracts
- SQL drafts stay aligned with current Python DataFrame structure
- notebook analysis follows the documented project questions and limitations
- the project becomes easier to explain, run, and present to others
