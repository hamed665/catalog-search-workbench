# CatalogLens

**Explainable BM25 product search with filters and offline evaluation.**

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-green)

Inspect why a product ranks, apply business filters and evaluate relevance without an external search service.

An original, runnable reference implementation by Hamed Minaei. Uses only the
Python standard library. No API key, paid account or network access is needed
for the included demos and tests. Version 0.1.0 focuses on the core engineering
contract rather than a hosted production service.

## Capabilities

- BM25 ranking with per-term score explanations
- Unicode NFKC normalization including Arabic token support
- Category, integer-price and stock filters
- Deterministic ranking with stable ID tie breaks
- Offline recall@k and MRR from explicit relevance judgments

## Quick start

```bash
git clone https://github.com/hamed665/catalog-search-workbench.git
cd catalog-search-workbench
python --version  # Python 3.11+
python -m cataloglens examples/products.json --query "dog brush"
python -m cataloglens examples/products.json --evaluate examples/judgments.json
python -m unittest discover -s tests -v
```

Optional library installation: `python -m pip install .`

## Use as a library

```python
import json
from cataloglens.core import Catalog
with open("examples/products.json") as f: catalog = Catalog(json.load(f))
print(catalog.search("brush", category="pets", in_stock=True))
```

## Data flow

Product JSON → token index → BM25 + filters → explained ranking → judged evaluation

See [cataloglens/core.py](cataloglens/core.py) for the implementation and [architecture notes](docs/architecture.md)
for transaction boundaries and deployment considerations.

## Verification

The test suite exercises behavioral guarantees, error paths and isolation.
SQLite projects also test competing connections with independent workers.
GitHub Actions runs the suite on Python 3.11, 3.12 and 3.13.
All fixtures are synthetic. Demo output is captured in
[examples/demo-output.txt](examples/demo-output.txt).

## Scope and limitations

Lexical retrieval only: no embeddings, generative responses, Arabic stemming or typo correction. The tiny synthetic fixture demonstrates mechanics, not real-world quality. Everything is in memory and scanning is linear in catalog size. Measure with representative judgments before claiming search improvements.

## Repository map

- `cataloglens/`: importable library and runnable CLI demo
- `tests/`: regression and invariant tests
- `examples/`: synthetic inputs and captured demo output
- `docs/`: design decisions and boundaries
- `.github/workflows/ci.yml`: repeatable verification

## License

MIT. See [LICENSE](LICENSE). Contributions: [CONTRIBUTING.md](CONTRIBUTING.md).
