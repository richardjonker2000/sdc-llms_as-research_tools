"""Build data/openalex/<topic>.csv: a seed paper plus its neighbourhood, from OpenAlex.

Run once while preparing (needs OPENALEX_API_KEY in config.env; costs well under $0.10 of the free $1/day):
    python organisers/build/fetch_openalex.py [topic ...]   (no topic: all)

Per topic (see workshop/biblio.py, harvest, shared with notebook 04): the seed paper and its references,
the 400 most-cited works citing it, a topic search balanced by period (200 relevant articles cited 5+ times
before 2010, in 2010-2017 and from 2018), and the 150 classics most often cited by all of these.
"""
import sys

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from workshop.biblio import DATA, SOCIAL_SCIENCES, _pages, clean_query, flatten, harvest  # noqa: E402
from workshop.llm import load_config  # noqa: E402

TOPICS = {  # name: (seed DOI, search query; OpenAlex accepts AND, OR and "quoted phrases")
    "ai_labour": ("10.1086/705716",
                  '(automation OR "industrial robots" OR "artificial intelligence" OR "technological change") AND '
                  '("labor market" OR "labour market" OR employment OR wages OR jobs OR workers)'),
    "green_innovation": ("10.1257/aer.102.1.131",
                         '"green innovation" OR "environmental innovation" OR "eco-innovation" OR "clean technology" OR "green technology"'),
    "china_innovation": ("10.1257/jep.31.1.49",
                         '(China OR Chinese) AND (innovation OR "R&D" OR patents) AND (firms OR enterprises)'),
}

# Notebook 03: one plain search, no seed and no classics, so the sample is easy to explain and to redo.
SEARCHES = {  # name: (search query, filter, how many)
    "ai_sustainability": ('("artificial intelligence" OR "machine learning" OR "deep learning") AND (sustainability OR '
                          'sustainable OR "green transition" OR "energy transition" OR "carbon emissions" OR '
                          '"climate change" OR "circular economy" OR "green innovation")',
                          f"type:article,language:en,from_publication_date:2015-01-01,cited_by_count:>4,{SOCIAL_SCIENCES}", 1000),
}


def search(query: str, filters: str, n: int) -> pd.DataFrame:
    """The n most relevant works for a title-and-abstract search (OpenAlex sorts by relevance)."""
    works = _pages({"filter": f"title_and_abstract.search:{clean_query(query)},{filters}"}, n)
    return pd.DataFrame([flatten(w) | {"found_via": "search"} for w in works])


if __name__ == "__main__":
    load_config()
    DATA.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or [*TOPICS, *SEARCHES]:              # e.g. python organisers/build/fetch_openalex.py ai_sustainability
        if name in SEARCHES:
            df = search(*SEARCHES[name])
        else:
            doi, query = TOPICS[name]
            df = harvest(query, seed_doi=doi)
        df.to_csv(DATA / f"{name}.csv", index=False, encoding="utf-8")
        print(f"{name}: {len(df)} works")
