"""
recheck_dead.py

Cross-references liveness_check.json against your original scraped data
(data/*.json) to pull out the full posting details for entries flagged
as dead, so you can re-read the content and confirm the label makes
sense on merit alone (not just because the page died later).
"""

import json
import glob

# Load liveness results
with open('liveness_check.json', 'r', encoding='utf-8') as f:
    liveness = json.load(f)

# Load all original scraped postings (adjust path/pattern if needed)
postings = {}
for filepath in glob.glob('data/*.json'):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Assumes each file is a list of posting dicts with a 'url' or 'redirect_url' field
        if isinstance(data, list):
            for p in data:
                url = p.get('redirect_url') or p.get('url')
                if url:
                    postings[url] = p
        elif isinstance(data, dict):
            url = data.get('redirect_url') or data.get('url')
            if url:
                postings[url] = data

# Find dead entries
dead_entries = [(u, r) for u, r in liveness.items() if r.get('dead')]

print(f"Total dead entries: {len(dead_entries)}\n")

for url, r in dead_entries:
    posting = postings.get(url)
    print("=" * 80)
    print(f"URL: {url}")
    print(f"Current label: {r['label']}")
    if posting:
        title = posting.get('title', 'N/A')
        company = posting.get('company', {}).get('display_name', 'N/A') if isinstance(posting.get('company'), dict) else posting.get('company', 'N/A')
        description = posting.get('description', 'N/A')
        print(f"Title: {title}")
        print(f"Company: {company}")
        print(f"Description (first 300 chars): {description[:300]}")
    else:
        print("!! Original posting data not found for this URL — check field names in your data/*.json")
    print()
