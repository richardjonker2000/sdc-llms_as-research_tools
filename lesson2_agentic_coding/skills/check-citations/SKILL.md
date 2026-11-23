---
name: check-citations
description: Check the references of a paper - every \cite key exists in the .bib file, every .bib entry is cited, DOIs resolve, and titles and years match the real publication (via OpenAlex or Crossref). Use before submitting, after an LLM helped write text, or when the researcher asks to check, clean or verify references.
---

# Check that every reference is real and used

LLMs invent references that look right. This check is mechanical, so it must be run, not judged.

## Ask first

1. **Which files**: the `.tex` file(s) and the `.bib` file.
2. Whether entries may be **corrected** (in a new `.bib` file) or only reported.

## Steps (one script: `analysis/check_citations.py`)

```python
import re, requests
tex = open("paper/main.tex", encoding="utf-8").read()
cited = set(k.strip() for g in re.findall(r"\\(?:cite|citet|citep|parencite|textcite)\w*\{([^}]*)\}", tex) for k in g.split(","))
bib = open("paper/refs.bib", encoding="utf-8").read()
entries = dict(re.findall(r"@\w+\{([^,]+),(.*?)\n\}", bib, flags=re.S))
# for each entry with a DOI: https://api.openalex.org/works/doi:<DOI>  -> compare title (case-insensitive) and year
# without a DOI: search by title, https://api.openalex.org/works?search=<title>, and report the best match
```

## Required in the report (`outputs/citation_check.md`)

| Problem | List |
| --- | --- |
| Cited but not in the `.bib` | keys |
| In the `.bib` but never cited | keys |
| DOI does not resolve | keys and DOIs |
| Title or year differs from OpenAlex | key, ours vs found |
| **Not found at all** | key, title: possibly invented, the researcher must check by hand |

## Never

- "fix" a reference that was not found by replacing it with a similar real paper;
- delete uncited entries without asking;
- report a reference as verified when the lookup failed (network, rate limit): say "not checked".
