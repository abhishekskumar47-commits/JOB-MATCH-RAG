# Job Match RAG — AI-Powered Job Matching System

## Motivation

I'm actively job hunting for entry-level AI/ML Engineer, Data Scientist, and Data
Analyst roles, primarily targeting Kochi, Technopark (Trivandrum), and select
opportunities in Bengaluru, Chennai, and Dubai. Instead of manually scanning job
boards, I'm building a system that pulls live job postings, retrieves the ones
most relevant to my resume using RAG, and — as the core ML component — trains a
reranker to score genuine match quality between my profile and each posting.

This project also serves as my ML + DL project submission for my internship
requirements, and as a live portfolio piece I use in my own job search.

## Architecture

```
Live Job APIs (Adzuna / Jooble / RemoteOK)
        │
        ▼
  Normalize & store postings (title, company, location, description, skills)
        │
        ▼
  Embed postings (sentence-transformers) → FAISS vector store
        │
        ▼
  Embed resume/query → Retrieve top-k relevant postings (RAG)
        │
        ▼
  ML Reranker (trained classifier) → re-score retrieved postings
  Features: embedding similarity, skill overlap %, experience match, location match
        │
        ▼
  LLM (Groq/Gemini/Ollama, pretrained — not fine-tuned) → natural-language
  explanation of match ("you match 8/10 requirements, missing: X, Y")
        │
        ▼
  FastAPI backend + Streamlit frontend
```

## What's trained vs. pretrained (important distinction)

- **LLM (generation)** — pretrained, used as-is. No training happens here.
- **Embedding model (sentence-transformers)** — pretrained, used as-is.
- **Reranker/classifier** — **this is the actual ML component.** Trained from
  scratch on labeled (query, job-posting) relevance pairs using engineered
  features. This is what satisfies the ML project requirement, evaluated with
  precision@k before vs. after reranking.

## Current status (updated as I build)

- [x] Repo structure and README
- [x] Live data ingestion (Adzuna API) — in progress
- [x] Baseline RAG retrieval (embeddings + FAISS)
- [x] Labeled dataset for reranker (manual + heuristic bootstrap)
- [ ] Reranker training + evaluation (precision@k)
- [ ] LLM explanation layer
- [ ] FastAPI + Streamlit deployment

## Why this dataset/approach

Real job postings (not synthetic) via free-tier APIs, filtered to South Indian
cities relevant to my job search. Kept free-tier throughout for the demonstration
phase; noted where this would need paid API tiers to scale to production volume.

## Tech stack

- Data: Adzuna API, Jooble API, RemoteOK API (all free tier)
- Embeddings: sentence-transformers (`all-MiniLM-L6-v2`)
- Vector store: FAISS
- Reranker: scikit-learn (logistic regression / gradient boosting)
- LLM: Groq (Llama) or local Ollama (Phi-3-mini / Llama-3.2-3B)
- Backend: FastAPI
- Frontend: Streamlit
- Training/experimentation: Google Colab / Kaggle Notebooks (free GPU)

## Folder structure

```
job-match-rag/
├── src/           # production code — API clients, RAG pipeline, FastAPI app
├── experiments/   # notebooks — data labeling, feature engineering, training, eval
├── data/          # pulled job postings, labeled pairs (gitignored if large)
├── docs/          # architecture diagrams, eval writeups
└── README.md
```

## Author

Abhishek — B.Tech AI & Data Science. Building this while applying for
entry-level AI/ML roles.
[LinkedIn](https://linkedin.com/in/abhishek-s-kumar-627821263) ·
[GitHub](https://github.com/abhishekskumar47-commits)
