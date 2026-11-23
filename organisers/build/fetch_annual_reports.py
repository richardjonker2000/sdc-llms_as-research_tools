"""Build data/annual_reports.csv.gz: 12 annual reports (4 firms x 3 fiscal years) from SEC EDGAR, as plain text.

Run once by the organiser (needs internet and beautifulsoup4); never during the workshop.
US 10-K and foreign 20-F filings are public documents (SEC EDGAR, no licence restrictions).
Usage: python organisers/build/fetch_annual_reports.py
"""
import json
import re
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

OUT = Path(__file__).resolve().parents[2] / "data" / "annual_reports.csv.gz"
UA = {"User-Agent": "sdc-workshop-builder/1.0"}   # SEC asks for a descriptive client name
FIRMS = {"Pfizer": "0000078003", "Caterpillar": "0000018230", "Walmart": "0000104169", "Microsoft": "0000789019"}
YEARS = [2019, 2022, 2025]     # fiscal year = year of the report date; ChatGPT appeared in Nov 2022
FORMS = ("10-K", "20-F")


def get(url: str) -> requests.Response:
    time.sleep(0.2)            # SEC allows 10 requests a second
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return r


def filings(cik: str) -> list[dict]:
    """All annual reports of a firm: the 'recent' block plus the older files it points to."""
    sub = get(f"https://data.sec.gov/submissions/CIK{cik}.json").json()
    blocks = [sub["filings"]["recent"]] + [get(f"https://data.sec.gov/submissions/{f['name']}").json()
                                           for f in sub["filings"].get("files", [])]
    out = []
    for b in blocks:
        for form, rep, filed, acc, doc in zip(b["form"], b["reportDate"], b["filingDate"], b["accessionNumber"], b["primaryDocument"]):
            if form in FORMS and rep:
                out.append({"form": form, "report_date": rep, "filed": filed, "accession": acc, "doc": doc})
    return out


def to_text(html: str) -> str:
    """HTML filing -> text with one block (paragraph, heading, table row) per line."""
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style"]):
        t.decompose()
    for t in soup.find_all(style=re.compile(r"display:\s*none", re.I)):   # hidden XBRL header
        t.decompose()
    for t in soup.find_all(["p", "div", "tr", "li", "h1", "h2", "h3", "h4", "br"]):
        t.append("\n")
    text = soup.get_text(" ")
    lines = (re.sub(r"\s+", " ", ln).strip() for ln in text.split("\n"))
    return "\n".join(ln for ln in lines if ln)


def main() -> None:
    rows = []
    for firm, cik in FIRMS.items():
        fs = filings(cik)
        for year in YEARS:
            hit = next((f for f in fs if f["report_date"].startswith(str(year))), None)
            if hit is None:
                print(f"  {firm} {year}: no annual report found"); continue
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{hit['accession'].replace('-', '')}/{hit['doc']}"
            text = to_text(get(url).text)
            rows.append({"firm": firm, "fiscal_year": year, "form": hit["form"], "report_date": hit["report_date"],
                         "filed": hit["filed"], "url": url, "words": len(text.split()), "text": text})
            print(f"  {firm} {year} {hit['form']}: {rows[-1]['words']:,} words")
    pd.DataFrame(rows).to_csv(OUT, index=False, compression="gzip")
    print("wrote", OUT, f"({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
