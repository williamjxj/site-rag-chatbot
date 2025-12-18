## Retrieval Playbook

1. Embed query.
2. Retrieve top_k (vector) + optional keyword search.
3. Build context with size cap.
4. Answer strictly from context.
5. Return `answer` + `sources` (unique).
