# ADR-0060 — EUR-Lex Institutions Are Normalized from Source URIs

**Status:** Accepted

Responsible-agent URIs from EUR-Lex are normalized deterministically
into English institution records.

Known financial authorities map to existing canonical provenance
sources: ECB, EBA, ESMA, EIOPA and SRB. Their records are added as
`DERIVED` provenance while the original EUR-Lex acquisition provenance
remains unchanged.

Other recognized EU institutions remain available in transport-neutral
metadata. They are not forced into the generic `OTHER` source.

Unknown institutions preserve their URI and receive the `UNKNOWN` type.
No online registry lookup or translation is performed.
