# Repository Review Checklist

Use this checklist before committing or merging changes.

## Architecture

- [ ] The change conforms to the Canonical Domain Model.
- [ ] The domain layer has no infrastructure dependencies.
- [ ] Structural decisions are documented through an ADR.

## Code quality

- [ ] Public APIs are typed.
- [ ] Public classes and modules are documented in English.
- [ ] Value objects are immutable where appropriate.
- [ ] No generated or environment-specific files are tracked.

## Validation

- [ ] `python -m pytest`
- [ ] `python -m ruff check .`
- [ ] `python -m mypy`

## Git

- [ ] The commit has one clear responsibility.
- [ ] The commit message follows Conventional Commits.
- [ ] Documentation is updated when behavior changes.
