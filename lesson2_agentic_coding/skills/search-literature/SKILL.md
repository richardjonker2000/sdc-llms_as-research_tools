---
name: search-literature
description: Search the scholarly literature with the free OpenAlex API and save the results as a table (title, year, venue, citations, abstract, DOI). Use when the researcher asks to find papers, build a literature sample, or check what has been published on a topic. Records the exact query and date so the search can be reported and repeated.
---

# Search the literature (OpenAlex)

Same data source as **lesson 1, notebooks 03 and 04**. A search is a sampling decision, so the query is the researcher's, and it is reported word for word.

## Ask first (method: the researcher decides)

1. **The query** (OpenAlex understands `AND`, `OR`, `"exact phrases"`). Propose one and show the first 10 titles before running the full search.
2. **Filters**: years, document types (articles only?), language, minimum citations.
3. **How many** papers, and how to pick them if there are more (most cited, most relevant, random).

## Steps (one script: `analysis/sN_search_<topic>.py`)

```python
import requests, pandas as pd, datetime
URL = "https://api.openalex.org/works"
params = {"search": QUERY, "filter": "type:article,from_publication_date:2010-01-01",
          "per-page": 200, "select": "id,doi,title,publication_year,primary_location,cited_by_count,abstract_inverted_index"}
# add "api_key": <key from config.env> if the researcher has one (free at openalex.org/settings/api);
# without a key everyone on the same network shares a small daily budget
def abstract(inv):                                       # OpenAlex stores abstracts as word -> positions
    if not inv: return ""
    pos = {p: w for w, ps in inv.items() for p in ps}
    return " ".join(pos[i] for i in sorted(pos))
```

Page with `cursor="*"` and `meta.next_cursor` until you have enough. Save `data/literature_<topic>.csv` and `data/literature_<topic>_query.txt` (query, filters, date, number of hits).

## Required in the report

- The exact query and filters, the date, total hits in OpenAlex, and how many were saved.
- How many have no abstract (OpenAlex lacks abstracts for some publishers).
- The 10 most cited titles, so the researcher can judge whether the query hit the right field.

## Never

- widen or narrow the query without asking ("to get better results");
- present the sample as "the literature": it is what this query found in OpenAlex;
- use a scraping workaround if the API refuses: stop and report.
