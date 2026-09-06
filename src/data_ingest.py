"""
data_ingest.py

Pulls live job postings from the Adzuna API for target roles and South Indian
cities, normalizes them into a consistent schema, and saves them as JSON.

Usage:
    python src/data_ingest.py

Requires a .env file in the project root with:
    ADZUNA_APP_ID=your_app_id
    ADZUNA_APP_KEY=your_app_key
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"

ROLES = ["data scientist", "machine learning engineer", "AI engineer", "data analyst"]
CITIES = ["kochi", "trivandrum", "bangalore", "chennai", "hyderabad"]

RESULTS_PER_QUERY = 10
DATA_DIR = Path(__file__).parent.parent / "data"


def fetch_jobs(role: str, city: str) -> list[dict]:
    if not APP_ID or not APP_KEY:
        raise RuntimeError(
            "Missing ADZUNA_APP_ID / ADZUNA_APP_KEY. Check your .env file."
        )

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": role,
        "where": city,
        "results_per_page": RESULTS_PER_QUERY,
        "content-type": "application/json",
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] {role} in {city}: {e}")
        return []

    data = response.json()
    results = data.get("results", [])

    normalized = []
    for job in results:
        normalized.append({
            "title": job.get("title", "").strip(),
            "company": job.get("company", {}).get("display_name", "Unknown"),
            "location": job.get("location", {}).get("display_name", city),
            "description": job.get("description", "").strip(),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "url": job.get("redirect_url", ""),
            "posted_date": job.get("created", ""),
            "query_role": role,
            "query_city": city,
            "source": "adzuna",
        })

    return normalized


def main():
    all_jobs = []
    seen_urls = set()

    print("Starting job data ingestion...\n")

    for role in ROLES:
        for city in CITIES:
            print(f"Fetching: '{role}' in '{city}'...")
            jobs = fetch_jobs(role, city)

            new_jobs = [j for j in jobs if j["url"] not in seen_urls]
            for j in new_jobs:
                seen_urls.add(j["url"])

            all_jobs.extend(new_jobs)
            print(f"  -> {len(jobs)} results, {len(new_jobs)} new")

            time.sleep(1)

    DATA_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = DATA_DIR / f"job_postings_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Saved {len(all_jobs)} unique postings to {output_path}")


if __name__ == "__main__":
    main() 


