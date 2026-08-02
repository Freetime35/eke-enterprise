# PR-085 — EUR-Lex Temporal Constraints and Deadlines

## Summary

PR-085 adds explicit, deterministic temporal constraints derived from
already-extracted compliance rules and rule qualifiers.

## Added model

- `EurLexTemporalConstraintKind`
- `EurLexTemporalRelation`
- `EurLexTemporalUnit`
- `EurLexTemporalConstraint`
- `EurLexTemporalConstraints`
- `normalize_temporal_constraints`

## Added extractor

`EurLexTemporalConstraintExtractor` recognizes explicit English temporal
expressions, including:

- relative offsets such as `within 30 days`;
- relative offsets with anchors such as `within five years of publication`;
- absolute deadlines such as `no later than 15 March 2027`;
- ISO dates such as `before 2028-01-01`;
- starts and ends introduced by `from`, `after` and `until`;
- durations introduced by `for`;
- quantified frequencies introduced by `every`;
- lexical frequencies such as `annually`, `monthly` and `quarterly`.

## Provenance

Each constraint retains:

- the source rule identifier;
- the source requirement identifier;
- the source document node;
- the source text;
- the source qualifier identifier when extraction came from a qualifier.

When the same temporal expression appears in both a rule and its qualifier,
qualifier provenance takes precedence so that the expression is not
duplicated.

## Deliberate limitations

PR-085 does not:

- calculate an absolute due date from an anchor;
- interpret business days or public holidays;
- process hours, minutes or time zones;
- infer implicit temporal conditions;
- model extensions or suspensions;
- resolve competing deadlines;
- structure non-temporal numeric thresholds;
- infer sanctions;
- use probabilistic NLP or LLM interpretation.

## Validation

The PR includes application tests for:

- model invariants;
- date parsing;
- numeric and written quantities;
- temporal units;
- relative anchors;
- durations and frequencies;
- qualifier provenance;
- deterministic identifiers;
- invalid rule/qualifier relationships.
