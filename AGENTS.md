# Code Rules Repository Instructions

## Scope

This repository maintains reusable frontend, backend, miniapp, and cross-stack governance packages. It is not a business application.

## Sources of Truth

- Executable coding rules live in each stack package under `rules/shared/`.
- Codex routing lives in each package `rules/codex/AGENTS.md`; Cursor routing lives in `rules/cursor/`.
- Root `docs/` is the governance SSOT. `common-governance/docs/` is generated; never edit generated copies directly.
- For project initiation, architecture proposals, and pre-release reviews, use `docs/architect-engineering-checklist.md`; mandatory merge and release gates remain in `docs/definition-of-done.md`.
- Project-specific paths, scripts, technology choices, and adoption Level belong in the consuming repository's `AGENTS.md` and `99-project-local.mdc`.
- For existing-project adoption, keep target rules in the stack package and record current debt in a machine baseline; follow `docs/migration-baseline.md` rather than weakening shared rules.

## Change Closure

When changing a rule, update its routing, verification checklist, eval coverage where behavior changes, package VERSION, CHANGELOG, README/index, and release checklist. Do not add a rule that has no trigger or validation path.

Keep Level 0 limited to universal invariants. Scenario-specific or advanced controls belong in conditional routing and the maturity model.

## Validation

Run the nearest package validator and tests, then the governance suite:

```text
python web-front/rules/scripts/validate-rules-package.py
python web-backend/rules/scripts/validate-rules-package.py
python miniapp/rules/scripts/validate-rules-package.py
python -m unittest discover -s web-front/rules/scripts/tests -v
python -m unittest discover -s web-backend/rules/scripts/tests -v
python -m unittest discover -s miniapp/rules/scripts/tests -v
python -m unittest discover -s scripts/tests -v
python scripts/validate-repository.py
python scripts/generate-rule-catalog.py
python scripts/sync-common-governance.py
python common-governance/scripts/validate-package.py
git diff --check
```

Report skipped checks and residual risk. Passing validators proves package consistency, not business correctness.
