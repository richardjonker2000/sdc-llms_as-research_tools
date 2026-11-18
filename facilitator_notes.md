# Facilitator notes: Session 1 (60 minutes, 09:45–10:45)

## Before the day

- [ ] Run `make_cache.py` with a live key (about 25 minutes, about 200 calls). Ollama must be running so notebook 03 is cached too. Then commit or copy `outputs_cached/`.
- [ ] Check `config.example.env` names the provider you'll use in Beijing (`minimax_cn`) and that the key works from China.
- [ ] Put the whole folder, including `outputs_cached/`, on USB sticks or a shared drive. Add the Python and Ollama installers, plus `tev1` model files copied from an existing machine (`~/.ollama/models` or `OLLAMA_MODELS`).
- [ ] Send the README a week ahead, asking participants to finish steps 1–3 and run `00_setup`.
- [ ] Replace the draft `data/gold_onet.csv` labels with real hand-coding, and swap in your own `data/patents.csv` if you have one.

## Timing plan

Demo first: participants watch, and follow along on their laptops only if they like. Everything below replays from `outputs_cached/`, so it runs with `DRY_RUN=1` if the network fails.

| Time | Block | Material | Notes |
| --- | --- | --- | --- |
| 09:45 | Welcome, the three blocks | intro slide | 3 min |
| 09:48 | Coding with a codebook | 01 | 20 min. Codebook, the prompt template (shown in full), raw vs validated, fake quotes, the figure. |
| 10:08 | Mapping a field | 08 | 7 min, cached only: one question, the streams, the map, one `ask_literature` answer with citations. Skip `suggest_questions` if short of time. |
| 10:15 | A coding agent | agent slide, then `agent_harness/DEMO.md` | 30 min, the second half of the hour. Uses notebook 01's codes as its data. |
| 10:45 | End | – | Coffee at 11:00; Roman's session at 11:15. |

Not in the session, for self-study: 00 (setup check), 02 (consistency), 03 (decision models, needs Ollama), 04, 05, 06, 07 and 09.

## The "wow" moments and what to say

1. **01, raw vs validated.** *"The model thinks in tags and markdown; we don't care. What we get is a typed record that either passes the codebook or gets sent back with the error."*
2. **01, fake quotes.** *"We asked for a verbatim quote, so we can check it mechanically. Every quote that isn't in the text is a row you shouldn't trust. This one line of code is a validity check most published LLM studies skip."*
3. **01, the figure.** *"Text to dataset to figure in a few minutes. With 30 patents it's a demo, but the pipeline is identical at 30,000."*
4. **02, disagreements.** *"Don't hide these rows; read them. They are usually ambiguous for humans too, and your rubric is the thing to fix."*
5. *(Self-study, not in the session.)* **03, speed and probabilities.** *"An 800 MB model on this laptop, no internet, no text: just probabilities."* About 3 decisions per second on the build laptop (CPU). Then the three bars: right on 10 of 14 when least sure, 10 of 13 in the middle, 13 of 13 when most sure (draft reference labels). *"Automate the confident part, hand-code the rest."* Mention the honest lesson in the notebook: on the three-level question the tiny model said "medium" to almost everything.
6. *(Self-study.)* **03, order effect.** On the build laptop `tev1` gave *identical* probabilities with the options swapped. *"Chat models are known to change their answer when you reorder options; this one doesn't. Worth testing on any model you use."* If some answers do flip on the day, point out that they are the low-confidence ones.
7. **04, registry check.** *"We never showed the model the registry's age field, so it's a free answer key."*
8. **05, firm names.** *"133 raw names became about 90 firms. We can check the result against PatentsView's hand-curated grouping."*

## Likely questions

- **Is this reproducible?** Not by default: models change and sampling is random. That's why everything is cached with the provider, model and prompt; archive the cache with your paper and report the model version and date.
- **Can I use confidential data?** Not with a cloud API unless your data agreement allows it. Local models (decision models, `PROVIDER=ollama`) keep data on your machine.
- **How many examples do I need to hand-code?** Enough to estimate accuracy per category, often 100–300. That's Session 2.
- **Which model is best?** It changes monthly. Validate on your own task rather than trusting leaderboards.
- **Temperature 0 isn't fully deterministic?** Correct: providers batch requests, so tiny differences remain. Caching freezes one answer.
- **What does it cost?** This whole session is about 200 calls. On paid tiers that's cents. 30,000 abstracts cost a few US dollars with a small model.
- **Why not one big prompt with all the documents?** You can't check it, it's unstable, and it hits length limits. Extract per document, then aggregate (04).
- **What's a decision model vs a chat model?** A chat model writes, a decision model chooses. Choosing is faster, gives probabilities, and runs on a laptop.
- **Can it code Chinese text?** Yes. Write the codebook in English or Chinese and keep the categories fixed. Test on a few rows first.

## If the Wi-Fi dies

1. Tell everyone to open `config.env`, set `DRY_RUN=1`, save, and **Kernel ▸ Restart Kernel**.
2. Everything already in `outputs_cached/` replays real answers instantly. Anything new (edited prompts, "Try it yourself" changes) gets clearly marked **fake** answers, so cells still run.
3. Decision models (03) keep working live, because they're local.
4. The chatbot track also needs internet, so if it's fully down, pair those participants with someone running cached notebooks.

## If the API is slow or rate-limited

- Lower `RPM` in `config.env` and restart the kernel. Rows that failed show in the `error` column. Re-running the cell replays every finished row from the cache and only calls the API for rows that failed because of the network or rate limits. Rows that failed validation replay the same failure, so fix the codebook or prompt instead.
- Demo from your own laptop with the cache and let participants follow along.
