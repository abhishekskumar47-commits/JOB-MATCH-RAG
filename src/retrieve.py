"""Find job postings whose meaning is closest to the saved profile."""

import json
from pathlib import Path
import pickle

import faiss
from sentence_transformers import SentenceTransformer


# Resolve project files from this script, not from the shell's current folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROFILE_PATH = PROJECT_ROOT / "profile.json"
INDEX_PATH = PROJECT_ROOT / "job_index.faiss"
METADATA_PATH = PROJECT_ROOT / "job_metadata.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"
RESULT_LIMIT = 10


def profile_to_text(profile):
    """Combine the profile fields used as the job-search query."""
    profile_parts = []
    for field in ("target_roles", "skills", "experience_summary"):
        values = profile.get(field) or []
        profile_parts.extend(str(value) for value in values)

    resume_text = profile.get("resume_text") or ""
    profile_parts.append(str(resume_text))
    return ". ".join(part for part in profile_parts if part.strip())


def display_value(value):
    """Convert plain-text or display-name objects into readable text."""
    if isinstance(value, dict):
        value = value.get("display_name") or ""
    return str(value or "Unknown")


def main():
    print(f"Loading profile from {PROFILE_PATH}...")
    with PROFILE_PATH.open("r", encoding="utf-8") as file:
        profile = json.load(file)
    query_text = profile_to_text(profile)

    print(f"Loading embedding model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    print("Embedding your profile...")
    query_embedding = model.encode(
        [query_text],
        normalize_embeddings=True,
    )

    print(f"Loading FAISS index from {INDEX_PATH}...")
    index = faiss.read_index(str(INDEX_PATH))
    with METADATA_PATH.open("rb") as file:
        postings = pickle.load(file)

    if index.ntotal == 0:
        print("The FAISS index is empty. Run src/embed_and_index.py first.")
        return

    result_count = min(RESULT_LIMIT, index.ntotal)
    print(f"Searching for the top {result_count} matching jobs...\n")
    scores, posting_indexes = index.search(query_embedding, result_count)

    for rank, (score, posting_index) in enumerate(
        zip(scores[0], posting_indexes[0]),
        start=1,
    ):
        if posting_index < 0 or posting_index >= len(postings):
            continue

        posting = postings[posting_index]
        title = posting.get("title") or "Unknown"
        company = display_value(posting.get("company"))
        location = display_value(posting.get("location"))
        url = posting.get("url") or posting.get("redirect_url") or "Unknown"

        print(f"{rank}. {title} at {company} (similarity: {score:.4f})")
        print(f"   Location: {location}")
        print(f"   URL: {url}\n")


if __name__ == "__main__":
    main()