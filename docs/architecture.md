# Design notes — CatalogLens

## Contract

Inspect why a product ranks, apply business filters and evaluate relevance without an external search service.

## Execution path

Product JSON → token index → BM25 + filters → explained ranking → judged evaluation

## Design choices

1. BM25 ranking with per-term score explanations.
2. Unicode NFKC normalization including Arabic token support.
3. Category, integer-price and stock filters.
4. Deterministic ranking with stable ID tie breaks.
5. Offline recall@k and MRR from explicit relevance judgments.

## Integration boundary

Lexical retrieval only: no embeddings, generative responses, Arabic stemming or typo correction. The tiny synthetic fixture demonstrates mechanics, not real-world quality. Everything is in memory and scanning is linear in catalog size. Measure with representative judgments before claiming search improvements.

## Failure handling

Validation errors are explicit exceptions. SQLite mutations use bound SQL
parameters; multi-step mutations commit together or roll back. Library results
are data structures suitable for an adapter layer. No network calls or secrets
are embedded in the examples.

## Before deployment

Choose an authenticated adapter, add structured operational logging without raw
customer data, define backup and retention requirements, and test realistic
workloads. The local tests establish specific invariants; they do not establish
production throughput, external integration compatibility or service availability.
