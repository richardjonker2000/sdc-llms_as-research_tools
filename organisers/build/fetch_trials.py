"""Build data/trials.csv from the ClinicalTrials.gov API v2 (public domain). Run once while preparing.

Picks ~30 completed interventional phase 2/3 studies across common conditions whose
eligibility sections are long (1,500-6,000 characters). registry_min_age / registry_max_age are
the structured ages the registry stores, kept so notebook 04 can check what the LLM extracted.
"""
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).resolve().parents[2] / "data" / "trials.csv"
CONDITIONS = ["type 2 diabetes", "depression", "breast cancer", "asthma", "hypertension", "stroke",
              "rheumatoid arthritis", "obesity", "COPD", "migraine", "heart failure", "psoriasis",
              "schizophrenia", "Alzheimer disease", "HIV"]
rows = []
for cond in CONDITIONS:
    r = requests.get("https://clinicaltrials.gov/api/v2/studies", timeout=60, params={
        "query.cond": cond, "filter.overallStatus": "COMPLETED", "pageSize": 50,
        "query.term": "AREA[StudyType]INTERVENTIONAL AND (AREA[Phase]PHASE2 OR AREA[Phase]PHASE3)",
        "fields": "NCTId,BriefTitle,LeadSponsorName,Phase,EligibilityCriteria,MinimumAge,MaximumAge"})
    r.raise_for_status()
    n = 0
    for s in r.json()["studies"]:
        p = s["protocolSection"]
        text = p.get("eligibilityModule", {}).get("eligibilityCriteria", "")
        if not 1500 <= len(text) <= 6000 or "exclusion" not in text.lower():
            continue
        rows.append({"nct_id": p["identificationModule"]["nctId"],
                     "title": p["identificationModule"]["briefTitle"],
                     "sponsor": p["sponsorCollaboratorsModule"]["leadSponsor"]["name"],
                     "phase": "/".join(p.get("designModule", {}).get("phases", [])),
                     "eligibility_text": text,
                     "registry_min_age": p["eligibilityModule"].get("minimumAge", ""),
                     "registry_max_age": p["eligibilityModule"].get("maximumAge", ""),
                     "condition_searched": cond})
        n += 1
        if n == 2:
            break
df = pd.DataFrame(rows).drop_duplicates("nct_id")
df.to_csv(OUT, index=False, encoding="utf-8")
print(len(df), "trials ->", OUT, "| median eligibility length:", int(df.eligibility_text.str.len().median()))
