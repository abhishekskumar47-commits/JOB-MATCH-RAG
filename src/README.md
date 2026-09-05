# src/

Production code lives here as proper Python modules (not notebooks):
- `data_ingest.py` — Adzuna/Jooble/RemoteOK API clients, normalization
- `rag_pipeline.py` — embedding + FAISS retrieval
- `reranker.py` — inference wrapper for the trained reranker
- `llm_explain.py` — LLM call for match explanation
- `api.py` — FastAPI app tying it all together
