# PR-011 — ResourceType

## Objective

Introduce the canonical controlled vocabulary used to classify resources
by legal or documentary nature.

## Added

- `ResourceType`
- Public export from `eke.domain.resources`
- Stable string serialization
- Unit tests
- ADR-0006

## Supported values

- REGULATION
- DIRECTIVE
- DECISION
- RECOMMENDATION
- OPINION
- TREATY
- CASE_LAW
- NOTICE
- COMMUNICATION
- GUIDELINE
- REPORT
- PROPOSAL
- CORRIGENDUM
- OTHER

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): introduce ResourceType enumeration
```
