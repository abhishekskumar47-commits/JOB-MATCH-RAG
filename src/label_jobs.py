"""
label_jobs.py

What this does, in plain terms:
1. Loads the 159 job postings you already indexed
2. Shows you one posting at a time: title, company, location, description
3. You type y (good match) or n (not a good match) and press Enter
4. Your answer is saved immediately to labels.json

You can stop anytime with Ctrl+C - your progress is saved, and running this
again will skip postings you've already labeled and continue from where you
left off.

Run this from the project's top-level folder:
    python src/label_jobs.py
"""

import json
import pickle
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
METADATA_PATH = PROJECT_ROOT / "job_metadata.pkl"
LABELS_PATH = PROJECT_ROOT / "labels.json"

def load_postings():
    with METADATA_PATH.open("rb") as file:
        return pickle.load(file)


def load_existing_labels():
    if LABELS_PATH.exists():
        with LABELS_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def save_labels(labels):
    with LABELS_PATH.open("w", encoding="utf-8") as file:
        json.dump(labels, file, indent=2)


def posting_id(posting, index):
    """A stable way to identify a posting even if list order changes."""
    return posting.get("url") or posting.get("redirect_url") or f"index_{index}"


def display_posting(posting):
    title = posting.get("title") or "(no title)"
    company_value = posting.get("company") or ""
    if isinstance(company_value, dict):
        company = company_value.get("display_name", "")
    else:
        company = company_value

    location_value = posting.get("location") or ""
    if isinstance(location_value, dict):
        location = location_value.get("display_name", "")
    else:
        location = location_value

    description = posting.get("description") or ""

    print("\n" + "=" * 70)
    print(f"Title:       {title}")
    print(f"Company:     {company}")
    print(f"Location:    {location}")
    print(f"Description: {description}")
    url = posting.get("url") or posting.get("redirect_url") or ""
    if url:
        print(f"Full posting: {url}")
    print("=" * 70)


def main():
    postings = load_postings()
    labels = load_existing_labels()

    already_done = len(labels)
    total = len(postings)
    print(f"Loaded {total} postings. {already_done} already labeled, {total - already_done} remaining.")
    print("For each job: type y (good match), n (not a good match), s (skip), or q (quit and save).\n")

    for index, posting in enumerate(postings):
        pid = posting_id(posting, index)

        if pid in labels:
            continue  # already labeled in a previous run

        display_posting(posting)
        answer = input("Good match? (y/n/s/q): ").strip().lower()

        if answer == "q":
            print("Stopping. Your progress is saved - run this again to continue.")
            break
        elif answer == "y":
            labels[pid] = 1
            save_labels(labels)
        elif answer == "n":
            labels[pid] = 0
            save_labels(labels)
        elif answer == "s":
            continue  # don't save anything, just move on without labeling this one
        else:
            print("Didn't understand that - type y, n, s, or q. Try this one again.")
            continue

    print(f"\nDone for now. Total labeled so far: {len(labels)} out of {total}.")


if __name__ == "__main__":
    main()


