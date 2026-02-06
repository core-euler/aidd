# RAG Standard

Retrieval-Augmented Generation — answering questions using own data.

## Pipeline

```
User Query → Query Embedding → Vector Search (Top-K) → Reranking → Context Assembly → LLM Generation → Response + Citations
```

## Document Processing

- Semantic chunking (by text structure: paragraphs, headings), not fixed-size
- Target chunk size: ~1000 chars (~250 tokens), overlap: ~200 chars
- Separator priority: `\n\n` → `\n` → `. ` → ` `
- Every chunk enriched with metadata: `document_id`, `source`, `language`, `topic`, `chunk_index`, `total_chunks`, `published_at`

## Vector Storage

- Store: **Qdrant**
- Distance metric: **Cosine**
- Embedding model: `text-embedding-3-small` (OpenAI) — 1536 dimensions
- Metadata stored in payload for filtered search

## Retrieval

- Hybrid search: vector similarity (weight 0.7) + keyword overlap (weight 0.3)
- Fetch 2x target top_k candidates, then rerank by combined score
- Metadata filtering (date, topic, source) passed to vector search

## LLM Generation

- All prompts are versioned: dataclass `PromptVersion` with fields `version`, `created_at`, `template`, `description`
- Temperature 0.2–0.3 for factual answers
- Prompt instruction: answer only from context, if no relevant info — say so
- Response includes citations/source references

## Context Management

- Token budget for context: max 3000 tokens
- Token estimation: `len(text) // 4`
- Chunks added by score until budget exhausted

## Caching

- Embeddings for frequent queries cached in Redis, TTL = 7 days
- Cache key: hash of text

## Observability

Every RAG request logged with fields:
- `query`, `chunks_retrieved`, `prompt_version`, `model`
- `input_tokens`, `output_tokens`, `total_tokens`, `cost_usd`
- `latency_ms`, `top_score`

## Required

- Version all prompts
- Log every AI request (version, tokens, cost)
- Retry with exponential backoff for API calls (3 attempts)
- Fallback response on API error
- Metadata on every chunk for filtering
- Citations/sources in responses

## Forbidden

- Magic strings instead of versioned prompts
- Fixed-size chunking ignoring text structure
- High temperature (> 0.5) for factual QA
- Ignoring token costs
- Trusting LLM output without source verification
