"""Create a FAISS index from the job postings saved in the data folder."""

import json
from pathlib import Path
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# This script is in src/, so its parent directory is the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INDEX_PATH = PROJECT_ROOT / "job_index.faiss"
METADATA_PATH = PROJECT_ROOT / "job_metadata.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"


def load_postings():
    """Read postings from each JSON file in the project's data folder."""
    postings = []
    json_files = sorted(DATA_DIR.glob("*.json"))

    for json_path in json_files:
        print(f"  Loading {json_path.name}...")
        with json_path.open("r", encoding="utf-8") as file:
            content = json.load(file)

        # The API may save a list directly or wrap the list in a results key.
        if isinstance(content, list):
            items = content
        elif isinstance(content, dict) and isinstance(content.get("results"), list):
            items = content["results"]
        else:
            # Also accept a single posting saved as a JSON object.
            items = [content]

        postings.extend(item for item in items if isinstance(item, dict))

    return postings


def posting_to_text(posting):
    """Combine the most useful posting fields into text for the embedding model."""
    title = posting.get("title") or ""
    description = posting.get("description") or ""
    company_value = posting.get("company") or ""

    # Adzuna commonly uses a company object; other sources may use plain text.
    if isinstance(company_value, dict):
        company = company_value.get("display_name") or ""
    else:
        company = company_value

    return f"{title}. {company}. {description}".strip()


def main():
    print(f"Loading job postings from {DATA_DIR}...")
    postings = load_postings()
    print(f"Found {len(postings)} job postings.")

    if not postings:
        print("No postings were found. Add JSON postings to the data folder first.")
        return

    texts = [posting_to_text(posting) for posting in postings]

    print(f"Loading embedding model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Embedding {len(texts)} job postings. This can take a little while...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    embeddings = np.asarray(embeddings, dtype="float32")

    # Inner product of normalized vectors is cosine similarity.
    print("Building the FAISS similarity index...")
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    print(f"Saving the FAISS index to {INDEX_PATH}...")
    faiss.write_index(index, str(INDEX_PATH))

    print(f"Saving the original postings to {METADATA_PATH}...")
    with METADATA_PATH.open("wb") as file:
        pickle.dump(postings, file)

    print(f"Done. Indexed {index.ntotal} postings.")


if __name__ == "__main__":
    main()