# The prepared run, turn by turn

MiniMax M3.1 Flash, OpenCode, 22 Nov 2026. Each turn is a git tag in `demo_prepared.bundle`.

## t1-plan

```
t1-plan: /plan I study how AI changes work. I want to know whether AI patents more often automate human work or augment it, and whether that has changed over time. I have the patent data from the workshop (data/patents.csv), the LLM codes from notebook 01 for 100 of the patents (data/patent_codes.csv), and the codebook we used (data/codebook.py). I am not good at Python.


AGENT: I'll start by looking at the data with one script, then draft the plan.
  [bash] ls -la; ls -la data/ 2>/dev/null; ls -la analysis/ 2>/dev/null; ls -la outputs/ 2>/dev/null
  [bash] git log --oneline -10 2>/dev/null; git status --short 2>/dev/null
  [read] data/codebook.py
  [bash] head -3 data/patents.csv; echo "---"; head -3 data/patent_codes.csv; echo "---"; cat README.md; echo "---"; cat requirements.txt
  [bash] mkdir -p analysis outputs
  [write] analysis/s0_look.py
  [bash] .venv/bin/python analysis/s0_look.py 2>&1

AGENT: Data looks clean and complete. Now writing the plan.
  [write] PLAN.md
  [bash] git add PLAN.md analysis/s0_look.py && git commit -m "plan: automate vs augment in AI patents 2014-2023; one data-look script" && git log --

AGENT: **Plan drafted: "Automate or augment? AI patents, 2014–2023"** (`PLAN.md`, committed with the one look script `analysis/s0_look.py`).

What I found in the data:
- 151 US grants, 2014–2023, no missing values; 100 of them coded (random sample), all from the saved-answer cache, no errors.
- Among the coded 100: 40 are AI, 51 automates / 42 neither / 7 augments. **Among the 40 AI patents: 30 automates, only 5 augments, 5 neither.**
- Every "over time" comparison here will be thin: 5 augment labels across ten grant years, and only 4 coded patents in 2023.

What the plan does: build one clean dataset with checks (S1) → descriptive tables (S2) → main automate-vs-augment result with two periods and a Fisher test (S3) → robustness (S4) → optional human agreement check (S5) → a methods/results note (S6). Steps are one script and one output each.

Two things the data told me that I wrote into the plan as limits: the 151 are large-assignee grants, not a random sample of AI patents, so every number is a within-sample share; and "grant year" is not "invention year", so the time trend lags by roughly two years.

**Open decisions**

D1. Which sample is the main analysis? (a) AI patents only (n=40, drop "neither") — my recommendation, since your question is about AI patents; (b) all 100 with "neither" as a third category; (c) all 58 with a clear automate/augment label.

D2. How to measure "over time"? (a) two periods, 2014–2018 vs 2019–2023, plus a year-by-year figure — my recommendation; (b) year-by-year only, no test; (c) logistic regression on year.

D3. What population do the 151 patents represent? (a) all US grants by these assignees in a year window, (b) hand-picked around AI/tech areas, (c) unknown. This decides whether "40% of the sample is AI" is a fact about patents or an artefact of the selection — I need your answer before any number is interpreted.

Two more are parked in the plan: validating the LLM codes against your own hand coding (recommended, but it needs your time), and whether to code the remaining 51 patents (needs live LLM mode; I'd keep the random sample of 100).

Reply with your answers (/revise D1: ..., D2: ..., D3: ...), or /next to start step S1.

-- 8 model steps, tokens: {'in': 23834, 'out': 3948, 'reason': 5130, 'cache': 104768}
```

## t2-revise

```
t2-revise: /revise D1: a, AI patents only, and report 'neither' next to it. D2: a, two periods plus the year-by-year figure. D3: c, unknown: it is one download from PatentsView made for the workshop, so every number is a share within this sample. And yes: code the remaining 51 patents with the same codebook (data/codebook.py), so all 151 are comparable. Make that the first step after building the dataset; I will switch live calls on for it.

  [read] PLAN.md
  [write] PLAN.md
  [bash] git add PLAN.md && git commit -m "plan: D1-D4 decided; add coding step for remaining 51 patents" && git log --oneline -3

AGENT: **What changed in PLAN.md**

- **D1 decided (a):** the main answer is about AI patents only, and the "neither" count is always printed next to the automate/augment shares — so no reader can be misled by a denominator that silently drops cases.
- **D2 decided (a):** two periods (2014–2018 vs 2019–2023) with a Fisher exact test, plus the year-by-year figure you asked for.
- **D3 decided (c):** the frame is one PatentsView download of unknown rule, so I rewrote the limits section: every number is a share within these 151 grants and nothing generalises beyond them. This is now the stated caveat in the plan, not a footnote.
- **New D4 decided (yes):** the remaining 51 patents get coded with the untouched codebook as step S2, right after the dataset is built. The script will stop if any row comes back as "fake", and I will report the LLM cost for that run.
- Steps renumbered (S1–S7) and the deliverables renamed to match: `outputs/s2_coding_log.txt` now holds the coding run's checks.

**Still open**

D5. The 151 will mix notebook 01's cached answers with new live ones. Should I re-code 10 of the already-coded 100 live and report how many labels match (~10 extra calls)? I recommend yes — it is the cheapest evidence that the two halves of the sample are comparable. (b) skip it and trust the cache is also fine.

D6. Validating the codes against your own hand coding is parked for the reliability step (S6) and still waits for your answer; I will raise it again before S6.

Reply with your answers (/revise D5: ..., D6: ...), or /next to start step S1.

-- 4 model steps, tokens: {'in': 6860, 'out': 2581, 'reason': 1986, 'cache': 108095}
```

## t3-next

```
t3-next: /next 


AGENT: Next step is S1: build the analysis dataset with the checks.
  [write] analysis/s1_dataset.py
  [bash] .venv/bin/python analysis/s1_dataset.py 2>&1
  [bash] ls -la outputs/; ls CLAIMS.md 2>&1; head -4 outputs/dataset_coded.csv
  [edit] PLAN.md
  [write] CLAIMS.md
  [bash] git add PLAN.md CLAIMS.md analysis/s1_dataset.py outputs/dataset_coded.csv outputs/s1_checks.txt && git commit -m "S1: build analysis datase

AGENT: **Step S1 done: build the analysis dataset**

What I did: joined the 100 notebook-01 codes onto all 151 patents, so every patent is on one row (code columns filled where a code exists, the other 51 marked "not coded yet"). The codebook file was read only, never changed.

Result: `outputs/dataset_coded.csv` has 151 rows (100 coded, 51 not yet coded) and `outputs/s1_checks.txt` has the full check log — 22 checks, 22 passed, 0 failed. Key confirmations: the 100 coded patents are exactly the random sample of 100 (so they were picked at random, not by hand), and the codes agree with the patent file on year, assignee, country and CPC subclass for all 100 rows.

How I checked it: 22 checks, each printed and logged. The coded rows all use valid codebook labels, none has a missing field, no empty evidence quote, no error flag, and all 100 came from the saved-answer cache. Evidence quotes are word-for-word in the abstract for 97 of 100; the 3 that are not are listed in the log (US10213080B2, US10707632B1, US11985491B2) — worth a glance, since a reworded quote usually means the model paraphrased.

Please check: open `outputs/s1_checks.txt` and skim the 3 non-verbatim quotes; open `outputs/dataset_coded.csv` and confirm the "coded" column shows True for 100 rows.

Decisions needed: none for this step. D5 (re-coding 10 cached patents live to test comparability) and D6 (your own hand coding) are still open, and D6 is not needed until the reliability step.

Next: S2 code the remaining 51 patents with the same codebook. It needs live calls on — flip `DRY_RUN` to live in `config.env` when you are ready, then reply /next and I will run it and report the cost.

-- 7 model steps, tokens: {'in': 39263, 'out': 3178, 'reason': 845, 'cache': 218368}
```

## t4-code

```
t4-code: /next I have switched live calls on (DRY_RUN=0).

  [skill] code-texts
  [bash] .venv/bin/python -c " import inspect from workshop import extract_many, quote_check, usage_table, cost, CFG print('CFG keys:', list(CFG.keys

AGENT: Live mode confirmed (`dry_run = False`). Writing the S2 coding script.
  [write] analysis/s2_code_remaining.py
  [bash] .venv/bin/python analysis/s2_code_remaining.py 2>&1

AGENT: Coding run finished. Adding a verification of the saved file (combined counts for all 151):
  [write] analysis/s2_check_totals.py
  [bash] .venv/bin/python analysis/s2_check_totals.py 2>&1
  [edit] PLAN.md
  [edit] PLAN.md
  [edit] CLAIMS.md
  [bash] git add PLAN.md CLAIMS.md analysis/s2_code_remaining.py analysis/s2_check_totals.py outputs/codes_all151.csv outputs/s2_coding_log.txt && gi

AGENT: **Step S2 done: code the remaining 51 patents**

What I did: ran the untouched codebook (`data/codebook.py`) over the 51 patents notebook 01 had not coded — first a 3-row test to read the answers, then the full run — and merged them with the 100 cached rows into one file of all 151 codes.

Result: `outputs/codes_all151.csv` has 151 unique rows (100 from notebook 01's cache, 51 new). Log in `outputs/s2_coding_log.txt`. All 151 together: 58 AI patents; 77 automates, 62 neither, 12 augments. Among the 58 AI patents: **43 automates, 8 neither, 7 augments**.

How I checked it: 0 failed rows, 0 fake answers (48 rows were fresh live calls, 3 replayed from the workshop's saved-answer cache), no error flag anywhere, the 100 old rows are unchanged field for field, and 50 of 51 new evidence quotes are word for word in the abstract (the one exception, US9937658B2, is kept in the data and listed in the log). As a comparability check, the label mix of the new 51 matches the old 100 closely: automates 51.0% vs 51.0%, neither 42.0% vs 39.2%, augments 7.0% vs 9.8%. Cost of the run: 0.0697 CNY (about 0.0015 per live text, so roughly 15 for 10,000 texts).

Please check: open `outputs/s2_coding_log.txt` and read the "value counts" section for the 51 new rows; open `outputs/codes_all151.csv` and skim a few of the new rows against their abstracts. One thing to note: the grant years are lopsided for AI patents — 0 in 2014, then 2, 3, 3, 4 in 2015–2018, and 7, 9, 15, 11, 4 in 2019–2023 — so the two-period comparison will be 12 AI patents against 46.

Decisions needed: D5 is still open (re-code 10 of the cached 100 live to test whether today's model reproduces notebook 01's labels, ~10 extra calls). Given that the new 51 and the old 100 came out with near-identical label mixes, my recommendation is to skip it, but it is your call — and D6 (hand coding) is still parked for the reliability step.

Next: S3 descriptive tables on all 151. Reply /next to continue, or tell me what to change.

-- 11 model steps, tokens: {'in': 17125, 'out': 4970, 'reason': 3756, 'cache': 520704}
```

## t5-latex

```
t5-latex: /extra Make a LaTeX table for my paper: of the 151 coded patents, how many were labelled automates / augments / neither, split by whether the LLM flagged them as AI. Counts and row percentages.


AGENT: Extra job: a LaTeX table. Writing the script that computes the numbers and writes the file.
  [write] analysis/x_automation_table.py
  [bash] .venv/bin/python analysis/x_automation_table.py 2>&1

AGENT: Two fixes needed: the tabular column spec (`lrrr` = 4 columns, but rows have 5) and the escape warnings.
  [edit] analysis/x_automation_table.py
  [edit] analysis/x_automation_table.py
  [bash] .venv/bin/python analysis/x_automation_table.py 2>&1 | tail -30
  [edit] CLAIMS.md
  [bash] git add analysis/x_automation_table.py outputs/extras/automation_by_ai.tex CLAIMS.md && git commit -m "extra: LaTeX table of labels by AI fl

AGENT: **What:** a `booktabs` LaTeX table of the 151 coded patents split by the LLM's AI flag — AI (n=58): 43 automates (74.1%), 7 augments (12.1%), 8 neither (13.8%); not AI (n=93): 34 automates (36.6%), 5 augments (5.4%), 54 neither (58.1%); total row 77 / 12 / 62, N = 151, with a caption, label `tab:automation-by-ai` and a source note.

**File:** `outputs/extras/automation_by_ai.tex` (generated by `analysis/x_automation_table.py`, so no number is typed by hand; paste it into Overleaf with `\usepackage{booktabs}`).

**How checked:** the script asserts that row counts and column counts each add to 151, that each row's percentages sum to 100, that no label falls outside the codebook, and that the .tex file contains the three booktabs rules, a caption, the label and N = 151; all checks passed on the run.

-- 8 model steps, tokens: {'in': 6929, 'out': 3036, 'reason': 1441, 'cache': 459776}
```

## t6-cluster

```
t6-cluster: /extra Group the 151 patent abstracts into themes by their words, with the cluster-texts skill. Use k = 5 and the standard stop words; no LLM naming. I want to see whether the AI patents fall into particular themes.

  [skill] cluster-texts
  [write] analysis/x_cluster_themes.py
  [bash] .venv/bin/python analysis/x_cluster_themes.py 2>&1

AGENT: The codes file has no abstract column — merging the abstracts from `data/patents.csv`:
  [edit] analysis/x_cluster_themes.py
  [edit] analysis/x_cluster_themes.py
  [bash] .venv/bin/python analysis/x_cluster_themes.py 2>&1
  [edit] analysis/x_cluster_themes.py
  [bash] .venv/bin/python analysis/x_cluster_themes.py 2>&1

AGENT: Two fixes: the "typical texts" list printed every text in the group, and the random baseline needs the same measure to compare with.
  [edit] analysis/x_cluster_themes.py
  [edit] analysis/x_cluster_themes.py
  [edit] analysis/x_cluster_themes.py
  [bash] .venv/bin/python analysis/x_cluster_themes.py 2>&1 | tail -75
  [bash] ls -la outputs/extras/; .venv/bin/python -c " import pandas as pd g = pd.read_csv('outputs/extras/themes_groups.csv') print(g.shape, g['grou
  [edit] CLAIMS.md
  [bash] git add analysis/x_cluster_themes.py outputs/extras/themes_groups.csv outputs/extras/themes_report.txt outputs/extras/themes_ai_by_group.png

AGENT: **What:** 151 abstracts grouped by their words (TF-IDF + k-means, k = 5, standard stop words, no LLM naming, 233-word vocabulary, fit 0.357). The AI patents concentrate sharply in one group: G2 ("user, set, image, training, model…", n = 41) is 80.5% AI and holds 33 of the 58 AI patents; G5 ("surface, water, connected, opening, body…", n = 18) is 0% AI; G1 26.7% AI, G4 40.9%, G3 16.0%.

**Files:** `outputs/extras/themes_report.txt` (sizes, top words, 3 typical texts each, stability), `outputs/extras/themes_groups.csv` (group per patent, with the AI flag and label), `outputs/extras/themes_ai_by_group.png` (AI share per group against the 38% overall).

**How checked:** the script asserts 151 coded patents merged with their abstracts, prints group sizes, per-group cohesion and the AI counts, and reruns the clustering with 20 further seeds — the groups are **not stable** (share of pairs staying together 0.217, against 0.220 for random groups of the same sizes), so treat them as a rough reading map only; several top words ("one", "least", "present", "when", "plurality") are patent boilerplate, and adding those to the stop words or trying other k values is your call as a follow-up.

-- 16 model steps, tokens: {'in': 21597, 'out': 5544, 'reason': 5214, 'cache': 1126400}
```

## t7-diagram

```
t7-diagram: /extra Make a diagram of what we did, for a slide: from the 151 patents, to notebook 01's 100 codes plus the 51 new ones with the same codebook, to the table and the themes. Put the real counts on the boxes.


AGENT: Extra job: an SVG diagram. Writing a script that pulls the real counts from the saved files and emits the SVG.
  [write] analysis/x_process_diagram.py
  [bash] .venv/bin/python analysis/x_process_diagram.py 2>&1
  [edit] analysis/x_process_diagram.py
  [edit] analysis/x_process_diagram.py
  [bash] .venv/bin/python analysis/x_process_diagram.py 2>&1 && echo "--- SVG ---" && cat outputs/extras/process_diagram.svg
  [bash] .venv/bin/python -c " import xml.etree.ElementTree as ET t = ET.parse('outputs/extras/process_diagram.svg') r = t.getroot() print('valid XML
  [edit] CLAIMS.md
  [bash] git add analysis/x_process_diagram.py outputs/extras/process_diagram.svg CLAIMS.md && git commit -m "extra: pipeline diagram (SVG) with real

AGENT: **What:** a slide diagram of the pipeline in three columns — inputs (151 abstracts from `data/patents.csv`; 100 notebook 01 codes from `data/patent_codes.csv`), coding (unchanged `data/codebook.py` → 51 new codes: 48 live + 3 from cache, 0 failed → merged 151 codes: 58 AI / 93 not AI, 77 automates / 62 neither / 12 augments), and outputs (the table: AI n=58 → 43/7/8, not AI n=93 → 34/5/54; the themes: AI share G2 80.5%, G4 40.9%, G1 26.7%, G3 16.0%, G5 0%, stability 0.217 vs 0.220 random).

**File:** `outputs/extras/process_diagram.svg` (1280×720, hand-written SVG from `analysis/x_process_diagram.py`; open it in a browser or drop it straight into your slide software — no external tools used).

**How checked:** every number on a box is read from the saved files by the script rather than typed, the script asserts each text line fits its box and each box fits its lines, and the finished file was re-read as valid XML (7 boxes + background, 53 text elements, 6 arrows); each box names the file and step it stands for, with a footnote that the groups are a reading map and all counts are within-sample shares.

-- 9 model steps, tokens: {'in': 14309, 'out': 4284, 'reason': 5412, 'cache': 787968}
```
