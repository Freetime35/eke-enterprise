# ADR-0079 — Boolean Logic Preserves Explicit Source Structure

**Status:** Accepted

PR-084 parses explicit `not`, `and`, `or` operators and balanced nested
parentheses from PR-083 qualifier text.

Operator precedence is `NOT`, then `AND`, then `OR`. The tokenizer is
immutable and recognizes `NOT` only at the beginning of an operand.
Linguistic negation such as `is not established` therefore remains atomic.

The resulting tree is closed, acyclic, deterministic and linked to its
source qualifier. No simplification, De Morgan transformation,
contradiction detection, CNF/DNF conversion, implication inference or
LLM interpretation is performed.
