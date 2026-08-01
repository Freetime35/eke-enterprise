# EKE Enterprise

**Engineering legal knowledge from authoritative sources.**

EKE Enterprise is an open-source platform for transforming authoritative legal sources into a canonical, versioned, traceable, and queryable legal knowledge system.

The project is designed for legal professionals, regulatory analysts, banking and financial-services specialists, data engineers, and AI teams that need to work with European legal materials at scale.

> EKE Enterprise is not merely a document crawler. It is a legal knowledge engineering platform.

## Project status

EKE Enterprise is currently in its **foundation and domain-modeling phase**.

The repository is being built specification-first. The initial work focuses on:

- the canonical domain model;
- architecture decision records;
- domain value objects and aggregate roots;
- development and quality standards;
- repository structure and continuous integration.

No stable public API is available yet.

## Mission

EKE Enterprise transforms heterogeneous legal sources into a canonical, versioned, and queryable legal knowledge platform.

Its first major use case is the discovery, acquisition, normalization, and analysis of European Union legal resources relevant to banking, financial institutions, investment banking, prudential regulation, financial markets, payments, resolution, digital finance, and related domains.

## Vision

Build the reference open-source platform for legal knowledge engineering in Europe.

The long-term objective is to represent not only legal documents, but also:

- their identities and external identifiers;
- their versions and consolidated states;
- their physical and digital manifestations;
- their legal relationships;
- their internal structure;
- their provenance and evidentiary basis;
- their regulatory concepts, obligations, actors, and timelines;
- their relevance to business and compliance processes.

## Why EKE Enterprise?

Authoritative legal information is published through heterogeneous systems and formats:

- EUR-Lex;
- CELLAR;
- ELI;
- Official Journal publications;
- RDF;
- FORMEX and XML;
- HTML and XHTML;
- PDF;
- future connectors such as Curia, EBA, ECB, ESMA, and EIOPA.

These sources are valuable but difficult to use together consistently. Identifiers, formats, metadata models, legal versions, and relationships vary across systems.

EKE Enterprise provides a common domain model and processing architecture that turns these heterogeneous sources into a coherent legal knowledge system.

## Core principles

### Authority first

Canonical data must be derived from authoritative sources. Every material value must retain its source, retrieval context, and evidence.

### Specification first

Specifications precede implementation. Domain contracts, business rules, schemas, and architectural decisions are defined before infrastructure code.

### Resource first

The core domain is centered on the abstract `Resource` aggregate.

A `LegalResource` is a specialization of `Resource`. This allows the platform to support EUR-Lex resources today and additional legal or regulatory source systems later.

### CELEX first for EUR-Lex workflows

For EUR-Lex resources, CELEX remains the primary business-facing identifier.

Users, APIs, CLI commands, and legal workflows must be able to retrieve and navigate resources by CELEX, even when the platform also maintains an internal immutable resource identifier.

### Canonical domain model

All source-specific representations converge toward a technology-independent canonical model.

The domain model must not depend on SQLite, Neo4j, FastAPI, GraphQL, RDFLib, or any other infrastructure technology.

### Immutable raw data

Downloaded source artifacts are preserved as immutable evidence.

Normalization and enrichment create derived representations; they never rewrite the original source material.

### Traceability by design

Canonical values must be traceable to one or more source records.

Inferred values must preserve their method, evidence, confidence, and processing version.

### Version everything

Legal resources, source records, canonical values, parsers, schemas, and ingestion runs must be version-aware.

### Idempotent processing

Repeated processing of identical source material must produce equivalent canonical results.

### Enterprise quality

The project targets strict typing, automated tests, reproducible builds, documented public interfaces, architecture compliance, and continuous integration.

## Scope

The first functional scope focuses on English-language European Union legal resources relevant to banking and financial services, including:

- prudential regulation;
- capital requirements;
- liquidity and leverage;
- credit, market, counterparty, and operational risk;
- recovery and resolution;
- deposit protection;
- financial-market infrastructure;
- investment firms and market conduct;
- payments and electronic money;
- anti-money laundering and counter-terrorist financing;
- crypto-assets and digital finance;
- operational and digital resilience;
- supervisory reporting and disclosure;
- sustainable finance and ESG-related regulatory obligations.

The architecture is intentionally source-independent and extensible beyond this initial scope.

## Architecture overview

```text
Authoritative Legal Sources
          |
          v
+---------------------------+
| Discovery and Connectors  |
+---------------------------+
          |
          v
+---------------------------+
| Harvest and Object Store  |
+---------------------------+
          |
          v
+---------------------------+
| Format-Specific Parsers   |
| RDF | FORMEX | XML | HTML |
| PDF | XHTML | Other       |
+---------------------------+
          |
          v
+---------------------------+
| Canonical Domain Model    |
+---------------------------+
          |
    +-----+----------+----------------+
    |                |                |
    v                v                v
Relational Store  Knowledge Graph  Search / Vector
    |                |                |
    +----------------+----------------+
                     |
                     v
          REST | GraphQL | CLI | UI
                     |
                     v
              Local AI / RAG
```

## Domain architecture

The project follows Clean Architecture and Domain-Driven Design.

```text
domain
  ^
  |
application
  ^
  |
infrastructure
  ^
  |
interfaces
```

The dependency rule is strict:

- `domain` depends only on the Python standard library;
- `application` depends on `domain`;
- `infrastructure` implements application ports;
- `interfaces` expose use cases through CLI, REST, GraphQL, and future user interfaces.

Infrastructure must not define the business model.

## Canonical resource model

At a high level, the platform represents:

```text
Resource
├── Internal identity
├── Business identifiers
├── Metadata
├── Lifecycle
├── Versions
├── Manifestations
├── Relationships
├── Structure
├── Provenance
├── Quality assessments
├── Timeline
└── Classifications
```

A legal resource may additionally expose:

```text
LegalResource
├── Legal nature
├── Legal basis
├── Recitals
├── Articles
├── Paragraphs
├── Points and subpoints
├── Annexes
├── Consolidated versions
├── Legal effects
├── Institutions
├── Concepts
└── Obligations
```

## Identifier policy

Every resource has:

1. an immutable internal identifier;
2. one or more external business identifiers.

Examples of external identifier schemes include:

- CELEX;
- ELI;
- CELLAR;
- ECLI;
- EBA document identifiers;
- ECB document identifiers;
- ESMA document identifiers;
- source-specific identifiers.

For EUR-Lex-facing workflows, CELEX is the primary business key.

## Repository direction

The target repository structure is:

```text
eke-enterprise/
├── .github/
├── docs/
│   ├── adr/
│   ├── architecture/
│   ├── domain/
│   ├── standards/
│   └── operations/
├── specs/
│   ├── domain/
│   ├── json-schema/
│   ├── openapi/
│   ├── graphql/
│   ├── sqlite/
│   └── ontology/
├── src/
│   └── eke/
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       ├── interfaces/
│       ├── generators/
│       └── ai/
├── tests/
├── scripts/
├── tools/
├── pyproject.toml
├── README.md
├── ROADMAP.md
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

## Technology direction

The domain layer targets Python 3.10 and uses only the Python standard library.

Planned infrastructure technologies include:

- Python 3.10;
- SQLite for local and operational storage;
- Neo4j for legal relationships and knowledge graphs;
- FastAPI for REST APIs;
- GraphQL for flexible graph-oriented queries;
- RDFLib for RDF processing;
- lxml for XML and FORMEX processing;
- Docker for reproducible deployment;
- GitHub Actions for continuous integration;
- local LLM and RAG technologies in later phases.

These choices are implementation details and must remain replaceable without changing the canonical domain model.

## Roadmap

### Phase 0 — Enterprise foundation

- repository standards;
- architecture baseline;
- canonical domain specification;
- ADR framework;
- CI and quality gates.

### Phase 1 — Domain core

- resource identifiers;
- business identifiers;
- provenance value objects;
- resource aggregate;
- legal-resource specialization;
- domain events and invariants.

### Phase 2 — Application core

- discovery use cases;
- ingestion orchestration;
- resource resolution;
- manifestation lifecycle;
- canonical validation.

### Phase 3 — Infrastructure

- object store;
- SQLite persistence;
- Neo4j persistence;
- source connectors;
- queue and scheduler;
- structured logging and metrics.

### Phase 4 — EUR-Lex and CELLAR

- CELEX discovery;
- metadata harvesting;
- manifestation resolution;
- relationship expansion;
- consolidated versions;
- RDF, FORMEX, XML, HTML, and PDF acquisition.

### Phase 5 — Knowledge services

- REST API;
- GraphQL API;
- legal-resource search;
- timeline exploration;
- relationship graph navigation;
- quality and coverage reporting.

### Phase 6 — Regulatory intelligence

- legal ontology;
- banking-domain taxonomy;
- obligation extraction;
- semantic chunking;
- embeddings;
- local RAG and LLM integration;
- explainable answers with source-level citations.

## Quality policy

The project aims to enforce:

- Python 3.10 compatibility;
- Ruff formatting and linting;
- strict static typing;
- automated unit and integration tests;
- full test coverage for the domain layer;
- documented public APIs;
- architecture decision records for structural changes;
- no merge without tests;
- no implementation without specification.

The governing rule is:

> No implementation without specification. No merge without tests. No architectural change without an ADR.

## Documentation language

All repository content must be written in English, including:

- source code;
- comments;
- docstrings;
- documentation;
- commit messages;
- issues;
- pull requests;
- architecture decisions;
- API specifications;
- test names and descriptions.

## Quick start

The software implementation is not yet available.

During the foundation phase, contributors should begin by reviewing:

1. `docs/domain/CanonicalDomainModel.md`;
2. architecture decision records under `docs/adr/`;
3. development standards under `docs/standards/`;
4. the project roadmap.

Installation instructions will be added when the first executable package is released.

## Contributing

Contributions will be welcome once the engineering baseline is published.

All contributions must:

- be written in English;
- conform to the canonical domain model;
- respect the Clean Architecture dependency rule;
- include tests;
- update documentation when public behavior changes;
- include an ADR when introducing a structural decision.

See `CONTRIBUTING.md` when available.

## Security

Please do not disclose security vulnerabilities through public issues.

A security policy and private reporting process will be documented in `SECURITY.md`.

## License

This repository is currently licensed under the MIT License.

See [`LICENSE`](LICENSE) for the complete license text.

## Maintainer

EKE Enterprise is initiated and maintained by [Freetime35](https://github.com/Freetime35).

---

**EKE Enterprise — engineering legal knowledge from authoritative sources.**
