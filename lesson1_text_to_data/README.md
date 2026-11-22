# Lesson 1 · What LLMs can do with text (11:30–12:30)

Two ways to turn text into data: **LLM coding** when you know what you are looking for, and **fast unsupervised methods** when you want to discover what is there. Every notebook shows its prompts and its code: nothing important is hidden in a helper.

Start with `00_setup.ipynb`: it should say **Connection OK**.

## In the session

| Time | Part | Notebook | What it shows | Cost with a live key* |
| --- | --- | --- | --- | --- |
| 11:30 | Intro | – | Classify vs discover | – |
| 11:35 | A · LLM coding | `01_codebook_extraction` | A codebook turns 30 patent abstracts into a validated table: the full prompt, validation and retry, the quote check, a figure | $0.007 (32 answers) |
| 11:53 | A · LLM coding | `02_agreement` | Do coders agree? One model twice, and two models: percent agreement, Cohen's kappa by hand, weighted kappa, Fleiss' kappa, the disagreements | $0.008 (80 answers) |
| 12:08 | B · Unsupervised | `03_clustering` | 814 abstracts grouped on the laptop CPU in under a second: TF-IDF and k-means written out, groups over time, how many groups, stability; one optional LLM call names the groups | $0.0003 (1 answer) |
| 12:18 | B · Unsupervised | `04_literature_review` | From one research question to a map of the field: search, citation network, streams named by an LLM, chat with the literature | $0.003 (12 answers) |
| 12:28 | Wrap-up | – | – | – |

\* MiniMax M3.1 Flash at its list price (US$0.15 per million tokens in, $0.60 out, Nov 2026). Each notebook prints its own cost; at these rates **10,000 texts cost roughly $1–3**. In the session everything replays from the saved answers, so it costs nothing.

## Take home

| Notebook | What it shows |
| --- | --- |
| `05_long_documents` | Long documents: extract per document, then aggregate, checked against the registry |
| `06_rewriting` | Cleaning firm names, translating, anonymising |
| `07_your_data` | The same pipeline on your own CSV, with a cost estimate for your dataset |
| `08_patent_task_match` | Which work tasks could an AI patent perform? |
| `09_literature_lenses` | More views on the field map from notebook 04 |
| `10_decision_models` | A small local model that answers with probabilities (needs Ollama) |

No internet? Set `DRY_RUN=1` in `../config.env` and restart the kernel: saved answers replay, anything new gets clearly marked fake answers.

`prompts_chatbot_track.md` is the same lesson for any chatbot, without code.
