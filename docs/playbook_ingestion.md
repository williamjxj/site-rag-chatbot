## Ingestion Playbook

When adding a new content type/source:
1. Add loader under `src/ingest/sources/`.
2. Return raw text + metadata only.
3. Add normalization if needed in `src/ingest/normalize.py`.
4. Add heading-aware chunking where possible.
5. Ensure `text_hash` prevents re-embedding unchanged chunks.
6. Add at least 1 unit test (loader or chunker).
