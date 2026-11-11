"""Build data/openalex/<topic>.csv: a seed paper plus its neighbourhood, from OpenAlex.

Run once while preparing (needs OPENALEX_API_KEY in config.env; costs well under $0.10 of the free $1/day):
    python tools/fetch_openalex.py

Per topic (see workshop/biblio.py, harvest, shared with notebook 08): the seed paper and its references,
the 400 most-cited works citing it, a topic search balanced by period (200 relevant articles cited 5+ times
before 2010, in 2010-2017 and from 2018), and the 150 classics most often cited by all of these.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from workshop.biblio import DATA, harvest  # noqa: E402
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

if __name__ == "__main__":
    load_config()
    DATA.mkdir(parents=True, exist_ok=True)
    for name, (doi, query) in TOPICS.items():
        df = harvest(query, seed_doi=doi)
        df.to_csv(DATA / f"{name}.csv", index=False, encoding="utf-8")
        print(f"{name}: {len(df)} works")
