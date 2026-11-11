"""Build data/patents.csv (run once by the organiser while preparing; never during the workshop).

PLACEHOLDER SAMPLE until the organiser supplies their own patents.
Records are USPTO granted patents as processed by PatentsView (snapshot 2024-12-31), read through the
Hugging Face mirror `zalizedata/us-patents-citation-company-dataset` (config `patents`) via the
datasets-server API, because the PatentsView API and bulk files were unreachable in Nov 2026.

Selection: ~6,000 random US utility grants filed 2014-2023 -> 150 patents, about half AI-related
(CPC G06N or AI keywords in the abstract), preferring firms whose name is spelled in several ways
(for the name-normalisation demo) and including Chinese and Danish assignees where available.
"""
import random
import re
import time
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).resolve().parent.parent / "data" / "patents.csv"
API = "https://datasets-server.huggingface.co/rows"
DATASET = "zalizedata/us-patents-citation-company-dataset"
AI_TERMS = re.compile(r"machine learning|neural network|artificial intelligence|deep learning|"
                      r"reinforcement learning|natural language processing", re.I)


def page(offset: int) -> list[dict]:
    for wait in (5, 20, 60, None):
        r = requests.get(API, params={"dataset": DATASET, "config": "patents", "split": "train",
                                      "offset": offset, "length": 100}, timeout=120)
        if r.ok:
            return [x["row"] for x in r.json()["rows"]]
        if wait is None:
            print("  giving up on offset", offset, r.status_code)
            return []
        time.sleep(wait)


def main() -> None:
    rng = random.Random(7)
    rows = []
    for i, off in enumerate(sorted(rng.sample(range(7_000_000, 9_070_000, 100), 150))):
        rows += page(off)
        if i % 25 == 0:
            print(i, off, len(rows))
        time.sleep(0.5)
    pool = pd.DataFrame(rows)
    pool["filing_year"] = pd.to_numeric(pool["filing_year"], errors="coerce")
    pool = pool[(pool.patent_type == "utility") & pool.filing_year.between(2014, 2023)
                & (pool.abstract.str.len() > 300) & pool.first_assignee_name.notna()
                & (pool.first_assignee_name != "None")].drop_duplicates("abstract")
    pool["is_ai_sampling"] = pool.cpc_subclasses.str.contains("G06N", na=False) | pool.abstract.str.contains(AI_TERMS)
    print(len(pool), "candidate patents,", int(pool.is_ai_sampling.sum()), "AI-related")

    # firms whose raw name appears in several spellings: take one patent per spelling (up to 5 per firm)
    spellings = pool.groupby("first_assignee_group")["first_assignee_name"].nunique().sort_values(ascending=False)
    top = spellings[spellings > 1].index[:12]
    messy = (pool[pool.first_assignee_group.isin(top)].sample(frac=1, random_state=1)
             .drop_duplicates("first_assignee_name").groupby("first_assignee_group").head(5))
    special = pool[pool.assignee_country.isin(["CN", "DK"])]
    picked = pd.concat([messy, special.sample(min(25, len(special)), random_state=1)]).drop_duplicates("patent_id")
    print(len(messy), "patents from", messy.first_assignee_group.nunique(), "multi-spelling firms;",
          (pool.assignee_country == "DK").sum(), "Danish in pool")
    for flag, target in [(True, 70), (False, 80)]:
        have = (picked.is_ai_sampling == flag).sum()
        rest = pool[(pool.is_ai_sampling == flag) & ~pool.patent_id.isin(picked.patent_id)]
        picked = pd.concat([picked, rest.sample(max(0, min(target - have, len(rest))), random_state=1)])
    df = pd.DataFrame({
        "id": picked.publication_number, "title": picked.title, "abstract": picked.abstract,
        "year": picked.filing_year.astype(int), "assignee": picked.first_assignee_name,
        "country": picked.assignee_country, "cpc_subclass": picked.cpc_primary_subclass,
        "assignee_patentsview_harmonized": picked.first_assignee_group,
    }).sample(frac=1, random_state=3).reset_index(drop=True)
    df.to_csv(OUT, index=False, encoding="utf-8")
    print("wrote", OUT, len(df), "| AI-related (sampling flag):", int(picked.is_ai_sampling.sum()),
          "| countries:", df.country.value_counts().head(8).to_dict())


if __name__ == "__main__":
    main()
