"""
check_liveness.py

Checks every posting URL in labels.json to see if it's still live or dead
(404 / expired / redirected to a generic search page). Writes the result
for ALL 159 postings to liveness_check.json, tagging each with:
    - label      : your original 0/1 label
    - status     : HTTP status code (or "error")
    - dead       : True/False guess based on status + page text
    - batch      : "first_93" or "later" (based on insertion order in labels.json)

This does NOT modify labels.json. It's a read-only diagnostic step so you
can decide, afterward, which entries to re-judge or drop.
"""

import json
import time
import requests

INPUT_FILE = "labels.json"
OUTPUT_FILE = "liveness_check.json"

# Phrases commonly shown on dead/expired job listing pages.
# Adjust this list once you've eyeballed a few real dead pages —
# different job boards word it differently.
DEAD_PHRASES = [
    "no longer available",
    "job has expired",
    "this job is no longer",
    "position has been filled",
    "listing not found",
    "page not found",
    "job not found",
]

def is_dead_response(resp: requests.Response) -> bool:
    if resp.status_code in (404, 410):
        return True
    if resp.status_code >= 400:
        return True
    text_lower = resp.text.lower()
    return any(phrase in text_lower for phrase in DEAD_PHRASES)


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        labels = json.load(f)

    items = list(labels.items())
    total = len(items)
    print(f"Loaded {total} labeled postings from {INPUT_FILE}")

    results = {}
    dead_count = 0

    for i, (url, label) in enumerate(items, start=1):
        batch = "first_93" if i <= 93 else "later"
        try:
            resp = requests.get(
                url,
                timeout=10,
                allow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            dead = is_dead_response(resp)
            results[url] = {
                "label": label,
                "status": resp.status_code,
                "dead": dead,
                "batch": batch,
            }
        except requests.RequestException as e:
            results[url] = {
                "label": label,
                "status": "error",
                "dead": True,
                "batch": batch,
                "error": str(e),
            }
            dead = True

        if dead:
            dead_count += 1

        print(f"[{i}/{total}] {'DEAD' if dead else 'live'}  (label={label})  {url}")

        time.sleep(0.5)  # be polite to the server, avoid rate limiting

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Summary
    dead_and_labeled_no = [
        u for u, r in results.items() if r["dead"] and r["label"] == 0
    ]
    dead_and_labeled_yes = [
        u for u, r in results.items() if r["dead"] and r["label"] == 1
    ]

    print("\n--- Summary ---")
    print(f"Total checked:            {total}")
    print(f"Total dead:               {dead_count}")
    print(f"Dead + labeled 0 (bad):   {len(dead_and_labeled_no)}  <- likely contaminated")
    print(f"Dead + labeled 1 (good):  {len(dead_and_labeled_yes)}  <- also worth reviewing")
    print(f"\nFull results written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

