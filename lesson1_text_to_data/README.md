# Lesson 1 · What LLMs can do with text (11:30–12:30)

Two ways to turn text into data: **LLM coding** when you know what you are looking for, and **fast unsupervised methods** when you want to discover what is there. Every notebook shows its prompts and its code: nothing important is hidden in a helper.

Start with `00_setup.ipynb`: it should say **Connection OK**.

## In the session

| Time | Part | Notebook | What it shows | Cost with a live key* |
| --- | --- | --- | --- | --- |
| 11:30 | Intro | – | Classify vs discover | – |
| 11:35 | A · LLM coding | `01_codebook_extraction` | A codebook turns 100 patent abstracts into a validated table: the full prompt, validation and retry, the quote check, a figure | ¥0.13 (107 answers) |
| 11:53 | A · LLM coding | `02_agreement` | Do coders agree on 100 tasks? One model twice, and two models: percent agreement, Cohen's kappa by hand, weighted kappa, Fleiss' kappa, the disagreements | ¥0.08 (200 answers) |
| 12:08 | B · Unsupervised | `03_clustering` | 794 abstracts on AI and sustainability from OpenAlex (search query and API link included) grouped on the laptop CPU in under a second: TF-IDF and k-means written out, groups over time, how many groups, stability; one optional LLM call names the groups | ¥0.002 (1 answer) |
| 12:18 | B · Unsupervised | `04_literature_review` | From one research question to a map of the field: search, citation network, streams named by an LLM, chat with the literature | ¥0.02 (12 answers) |
| 12:28 | Wrap-up | – | – | – |

\* MiniMax M3.1 Flash at the official China price (¥1.00 per million tokens in, ¥0.10 if cached, ¥4.00 out; platform.minimax.cn, Nov 2026). The API reports the tokens; the notebooks multiply by the price. Every cell that gets answers prints its cost; at these rates **10,000 texts cost roughly ¥5–15** (about US$1–2). In the session everything replays from the saved answers, so it costs nothing.

## After the workshop

More notebooks we don't teach in the session are in `../additional_materials/`, starting with **A1 · your own data**.
