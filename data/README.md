# Data card

Everything the notebooks read ships in this folder. Nothing is downloaded during the workshop. The scripts in `tools/` show how each public file was built (run once, November 2026).

| File | Rows | Columns | Source | Licence | Status |
| --- | --- | --- | --- | --- | --- |
| `patents.csv` | 151 | `id, title, abstract, year, assignee, country, cpc_subclass, assignee_patentsview_harmonized` | USPTO granted patents as processed by PatentsView (snapshot 2024-12-31), via the Hugging Face mirror `zalizedata/us-patents-citation-company-dataset` | USPTO text: public domain. PatentsView: CC BY 4.0. HF compilation: CC BY-NC 4.0 (fine for this non-commercial workshop) | **Placeholder**: to be replaced by the organiser's own sample |
| `onet_tasks.csv` | 150 | `task_id, occupation_code, occupation_title, task` | O\*NET 31.0 Task Statements, 15 occupations × 10 tasks (core tasks first) | CC BY 4.0 | Final |
| `trials.csv` | 30 | `nct_id, title, sponsor, phase, eligibility_text, registry_min_age, registry_max_age, condition_searched` | ClinicalTrials.gov API v2: completed interventional phase 2/3 studies, 2 per condition for 15 conditions, eligibility text 1,500–6,000 characters | Public domain | Final |
| `interview_snippets.csv` | 15 | `id, speaker, language, text, note` | **Synthetic**, written for the workshop. All people and firms are fictional. 11 English, 4 Chinese | CC0 | Final |
| `onet_labels_claude.csv` | 100 | `task_id, label, note` | LLM-exposure labels (`high` / `medium` / `low`) for 40 tasks from `onet_tasks.csv` | CC0 | Labels by Claude, a second LLM annotator (not human) |
| `my_data_example.csv` | 10 | `id, text` | **Synthetic** example texts for notebook A1 | CC0 | Final |
| `openalex/<topic>.csv` (3 files) | ai_labour 1,152, green_innovation 1,220, china_innovation 1,129 | `id, doi, title, year, type, venue, cited_by_count, authors, institutions, countries, topic, subfield, field, abstract, references, found_via` | OpenAlex API: a seed paper plus its references, top citing works and a topic search | CC0 (OpenAlex). Abstracts belong to their publishers; use for analysis only | Samples for the bibliometrics add-on |

## Provenance: where each file came from

All public data was retrieved on **8 November 2026** with the scripts in `tools/`. Re-running a script gives the same selection only while its upstream source is unchanged; ClinicalTrials.gov in particular updates daily.

### patents.csv
- **Retrieved from:** Hugging Face dataset [`zalizedata/us-patents-citation-company-dataset`](https://huggingface.co/datasets/zalizedata/us-patents-citation-company-dataset), config `patents`, split `train` (9,075,421 rows).
- **How:** the Hugging Face datasets-server API, `https://datasets-server.huggingface.co/rows`. 150 pages of 100 rows were read at random offsets between 7,000,000 and 9,070,000 (random seed 7).
- **Underlying source:** each row's `_source_url` field points to the PatentsView bulk data release on Zenodo, <https://zenodo.org/records/15783125> (PatentsView snapshot 2024-12-31). PatentsView processes USPTO grant data.
- **Selection:** US utility patents filed 2014–2023 with an abstract over 300 characters and a named assignee, about 3,650 candidates. The 150 were chosen as described under *Notes* below.
- **Column mapping:**
  - `id` ← `publication_number`
  - `year` ← `filing_year`
  - `assignee` ← `first_assignee_name`
  - `country` ← `assignee_country`
  - `cpc_subclass` ← `cpc_primary_subclass`
  - `assignee_patentsview_harmonized` ← `first_assignee_group`
- **Script:** `tools/fetch_patents.py`
- **Routes tried first that did not work (Nov 2026):**
  - The PatentsView API (`search.patentsview.org`) was unreachable.
  - The PatentsView bulk files on `s3.amazonaws.com/data.patentsview.org` returned 403.
  - `bulkdata.uspto.gov` has been retired.
  - The USPTO Open Data Portal API (`api.uspto.gov`) needs an API key.
  - Google Patents (`patents.google.com`) started returning 503 after a few dozen requests.
  - Hugging Face's `/filter` and `/search` endpoints returned internal errors.

### onet_tasks.csv
- **Retrieved from:** the O\*NET 31.0 database, *Task Statements* (CSV): <https://www.onetcenter.org/dl_files/database/db_31_0_csv/task_statements.csv> (18,838 tasks). The download page is <https://www.onetcenter.org/database.html>.
- **Selection:** 15 occupations, listed by O\*NET-SOC code in the script. For each, 10 tasks: rows shuffled with random seed 42, core tasks before supplemental.
- **Column mapping:**
  - `task_id` ← `Task ID`
  - `occupation_code` ← `O*NET-SOC Code`
  - `occupation_title` ← `Title`
  - `task` ← `Task`
- **Script:** `tools/build_onet.py path/to/task_statements.csv`

### trials.csv
- **Retrieved from:** the ClinicalTrials.gov API v2, <https://clinicaltrials.gov/api/v2/studies>.
- **Query:** one request per condition (15 conditions, listed in the script), with:
  - `query.cond=<condition>`
  - `filter.overallStatus=COMPLETED`
  - `query.term=AREA[StudyType]INTERVENTIONAL AND (AREA[Phase]PHASE2 OR AREA[Phase]PHASE3)`
  - `pageSize=50`
- **Selection:** the first 2 studies per condition whose eligibility criteria are 1,500–6,000 characters long and mention exclusions.
- **Fields used:** `NCTId, BriefTitle, LeadSponsorName, Phase, EligibilityCriteria, MinimumAge, MaximumAge`
- **Script:** `tools/fetch_trials.py`

### openalex/*.csv (bibliometrics session, draft)
- **Retrieved from:** the OpenAlex API, <https://api.openalex.org/works>, on 9 November 2026, using a free OpenAlex API key. The whole harvest used $0.03 of the free $1/day budget.
- **Topics and seed papers** (DOIs checked against OpenAlex). Queries use OpenAlex's boolean search on titles and abstracts:

| File | Papers | Seed paper | Search query |
| --- | --- | --- | --- |
| `ai_labour.csv` | 1,147 | Acemoglu & Restrepo, *Robots and Jobs* (JPE), 10.1086/705716 | `(automation OR "industrial robots" OR "artificial intelligence" OR "technological change") AND ("labor market" OR "labour market" OR employment OR wages OR jobs OR workers)` |
| `green_innovation.csv` | 1,220 | Acemoglu, Aghion, Bursztyn & Hemous, *The Environment and Directed Technical Change* (AER), 10.1257/aer.102.1.131 | `"green innovation" OR "environmental innovation" OR "eco-innovation" OR "clean technology" OR "green technology"` |
| `china_innovation.csv` | 1,129 | Wei, Xie & Zhang, *From "Made in China" to "Innovated in China"* (JEP), 10.1257/jep.31.1.49 | `(China OR Chinese) AND (innovation OR "R&D" OR patents) AND (firms OR enterprises)` |

- **Selection per topic** (four steps, code in `workshop/biblio.py`, `harvest`):
  1. **seed**: the seed paper above;
  2. **forward**: the seed's references, plus the 400 most-cited works that cite it;
  3. **topic search, balanced by period**: the 200 most relevant journal articles cited at least 5 times **before 2010**, in **2010–2017**, and **from 2018**. Without balancing, the post-2018 publication boom crowded out older work; without the citation floor, about 45% of hits were never cited and many were off-topic;
  4. **backward**: the 150 works most often cited (5+ times) by everything above, i.e. the classics. Notebook 04 shows these as *foundations* and leaves them out of the stream map, because generic methods classics (e.g. on survey bias or panel econometrics) would otherwise form fake "streams".
- **Columns:**
  - `found_via` says how a work entered the sample (it can be more than one route).
  - `abstract` is rebuilt from OpenAlex's word-position index. About 50–85% of works have one; publishers withhold some.
  - `references` lists the OpenAlex IDs of the works each paper cites, space-separated.
  - `countries` and `institutions` come from author affiliations.
- **Script:** `tools/fetch_openalex.py` (needs `OPENALEX_API_KEY` in `config.env`). Re-running gives somewhat different samples as OpenAlex updates. Data retrieved 9 November 2026.
- **Foundational works (notebook A4):** `<topic>_refs.csv` holds OpenAlex metadata for the 150 works each corpus cites most (co-citation analysis). It is fetched once by notebook A4 and then reused offline.
- **Embeddings (notebook A4):** AI meaning-vectors for each paper's title and abstract are cached in `outputs_cached/embeddings/<topic>__<model>.npz` (MiniMax `embo-01`, 1,536 dimensions, stored as 16-bit floats, about 3 MB per topic). Without them, or in dry-run mode, notebook A4 falls back to word-based LSA vectors.
- **Students' own research questions (notebook 04):** the LLM turns a research question into a search query, checks how many articles it finds per period, and refines it (up to 4 rounds). It then picks a seed paper from the 15 most-cited matches. Each sample is saved as `data/openalex/my_<query>.csv`. Hit counts and seed candidates are cached in `outputs_cached/openalex_counts.json` and `openalex_seeds.json`, so a question that has run once replays offline. The five example questions in `workshop/biblio.py` (`EXAMPLES`) are pre-run this way.

### interview_snippets.csv
- **Origin:** written for this workshop by Claude (an AI assistant) on 8 November 2026. These are **not real interviews**.
- All people and firms are invented. Two firm names were changed because they resembled real companies (Fjord Line, Huaxin). Cities are real places used only as settings.

### onet_labels_claude.csv
- **Origin:** labels assigned by Claude (Anthropic's LLM) using the three-level rubric in notebook 02, for 100 tasks from `onet_tasks.csv`: the first 40 (2–3 per occupation) coded on 8 November 2026 and re-checked on 22 November 2026 (one change: task 21514, medium to high); 60 more (4 per occupation, drawn at random) added on 22 November 2026. Notebooks A5 and A6 use the first 40.
- **Not** human-coded and **not** from O\*NET. Notebook 02 uses them as a second LLM annotator, to measure agreement between models.

### my_data_example.csv
- **Origin:** ten sentences written for this workshop by Claude (an AI assistant). Fictional; not quotes from any source.

## Notes per file

**patents.csv**
- `year` is the filing year (2014–2023). `country` is the first assignee's country (PatentsView). `cpc_subclass` is the primary CPC subclass (G06N = AI / machine learning).
- The sample was drawn from about 15,000 random US utility grants and then selected: 70 AI-related (CPC G06N or AI keywords in the abstract) and 81 others, with 12 large firm groups whose names appear in several spellings, plus extra Chinese assignees.
- `assignee` is the raw name as printed on the patent. `assignee_patentsview_harmonized` is PatentsView's parent-group name. Notebook A3 uses it to check the LLM's name clean-up. 133 raw names map to 89 groups.
- There are no `claims` because the mirror does not include claim text.
- Why not the PatentsView API? In November 2026 the API was unreachable and the old bulk-download links returned 403. The same PatentsView records were read from the Hugging Face mirror.

**onet_tasks.csv** includes these occupations: Customer Service Representatives; Bookkeeping, Accounting and Auditing Clerks; Accountants and Auditors; Paralegals; Writers and Authors; Interpreters and Translators; Software Developers; Market Research Analysts; Economists; General and Operations Managers; Retail Salespersons; Registered Nurses; Electricians; Heavy Truck Drivers; Restaurant Cooks.

**trials.csv**: `registry_min_age` / `registry_max_age` are the structured ages stored by the registry. Notebook A2 compares them with what the LLM extracts from the free text.

**onet_labels_claude.csv**: 17 high, 42 medium and 41 low. One LLM's judgement using the rubric in notebook 02; for human-model agreement, hand-code a sample yourself.

## Required attribution

> This workshop includes information from the O\*NET 31.0 Database by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license. O\*NET® is a trademark of USDOL/ETA. The workshop organisers have modified all or some of this information. USDOL/ETA has not approved, endorsed, or tested these modifications.

Patent data: USPTO via PatentsView (patentsview.org), CC BY 4.0. Clinical trial data: ClinicalTrials.gov, U.S. National Library of Medicine.
