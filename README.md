## Job Match RAG: Personal AI Job-Matching System

## Motivation

I'm actively job hunting for entry-level AI/ML Engineer, Data Scientist, and Data
Analyst roles, primarily targeting Kochi, Technopark (Trivandrum), and select
opportunities in Bengaluru, Chennai, Hyderabad, and Dubai. Instead of manually
scanning job boards, I'm building a system that pulls live job postings, extracts
structured requirements from them with a fine-tuned LLM, retrieves the ones most
relevant to my resume using embeddings, and, as the core ML component, trains a
reranker to score genuine match quality between my profile and each posting.

This is a **personal tool**: built for my own job search and labeled/trained on my
own preferences. It is not a general multi-user product, and there is no plan to
generalize the matching to other people's resumes.

This project also serves as my ML project submission for my internship
requirements, and as a live portfolio piece I use in my own job search.

## What this system is (and isn't)

Strictly speaking this is not classic RAG, since there is no answer-generation
step. It is a **content-based recommendation system**: embedding-based retrieval
(FAISS, cosine similarity / k-NN) followed by a trained reranker. An LLM is used
for **structured extraction** from postings (see below), not for chatting or
generating answers.

## Architecture

```
Live Job APIs (Adzuna; Jooble / RemoteOK optional)
        │
        ▼
  Normalize & store postings (title, company, location, description)
        │
        ▼
  Fine-tuned LLM (LoRA) → extract structured skills/requirements JSON
        │
        ▼
  Embed postings (sentence-transformers) → vector store
        │
        ▼
  Embed profile (resume) → retrieve top-k relevant postings (cosine similarity)
        │
        ▼
  ML Reranker (trained classifier) → re-score retrieved postings
  Features: embedding similarity, skill overlap %, experience match, location match
        │
        ▼
  Supabase (Postgres + pgvector) backend  →  React Native (Expo) mobile app
```

The vector store is FAISS (`IndexFlatIP`) during development. At the backend stage
it moves to Supabase with the pgvector extension, so postings and embeddings live
in one combined database instead of a separate vector DB.

## What's trained vs. pretrained

- **Embedding model (sentence-transformers)**: pretrained, used as-is.
- **LLM extraction model (Phi-3-mini or Gemma-2B)**: **fine-tuned with LoRA** to
  turn raw job postings into structured skills/requirements JSON. The extracted
  fields feed the reranker's features (skill overlap, experience match).
- **Reranker/classifier**: **the core ML component.** Trained on labeled
  (profile, job-posting) pairs using engineered features. Leaning toward Logistic
  Regression given the small labeled dataset. Evaluated with precision@k before
  vs. after reranking.

## Current status (updated as I build)

- [x] Repo structure and README
- [x] Live data ingestion (Adzuna): 159 unique postings across Data Scientist /
      ML Engineer / AI Engineer / Data Analyst roles in 5 cities
- [x] Baseline retrieval (all-MiniLM-L6-v2 embeddings + FAISS), verified on
      top-10 results
- [x] Labeled dataset: all 159 postings labeled; liveness check run and mislabeled
      senior roles corrected. Final set: **32 good / 127 bad**
- [ ] Feature engineering + reranker training + evaluation (precision@k)  ← next
- [ ] LoRA fine-tuning of the extraction LLM (structured skills/requirements JSON)
- [ ] Supabase + pgvector backend
- [ ] React Native (Expo) app
- [ ] v2 idea: periodic retraining from implicit feedback (jobs clicked/applied
      vs. skipped) once the app exists

## Why this dataset/approach

Real job postings (not synthetic) via free-tier APIs, filtered to South Indian
cities relevant to my job search. Kept free-tier throughout the demonstration
phase; noted where this would need paid API tiers to scale to production volume.
Labels reflect my own preferences (for example, senior-level roles are marked as
bad matches), which is intentional for a personal tool.

## Tech stack

- Data: Adzuna API (free tier); Jooble and RemoteOK as optional extra sources
- Embeddings: sentence-transformers (`all-MiniLM-L6-v2`)
- Vector store: FAISS now, Supabase pgvector later
- Reranker: scikit-learn (Logistic Regression, gradient boosting as comparison)
- LLM fine-tuning: LoRA on Phi-3-mini or Gemma-2B
- Backend/database: Supabase (Postgres + pgvector)
- Frontend: React Native (Expo)
- Training/experimentation: Google Colab / Kaggle Notebooks (free GPU)

## Folder structure

```
job-match-rag/
├── src/           # data ingestion, embedding/indexing, retrieval, labeling and reranker code
├── experiments/   # notebooks: feature engineering, training, LoRA fine-tuning, eval
├── data/          # pulled job postings, labeled pairs (gitignored if large)
├── docs/          # architecture diagrams, eval writeups
├── profile.json   # my resume/profile used as the retrieval query
└── README.md
```

## Author

Abhishek, B.Tech AI & Data Science. Building this while applying for
entry-level AI/ML roles.
[LinkedIn](https://linkedin.com/in/abhishek-s-kumar-627821263) ·
[GitHub](https://github.com/abhishekskumar47-commits)

