# Lesson 1 · What LLMs can do with text (11:30–12:30)

Start with `00_setup.ipynb`: it should say **Connection OK**. Then:

| Notebook | What it shows | In the session |
| --- | --- | --- |
| `01_codebook_extraction` | **Supervised:** a codebook turns patent abstracts into a validated table; the quote check | yes |
| `02_classification_consistency` | **Is it right?** Agreement with hand coding; reading the disagreements | yes |
| `03_decision_models` | A small local model that answers with probabilities (needs Ollama) | demo only |
| `08_bibliometrics` | **Unsupervised:** from one research question to a map of a field | yes |
| `04_long_text_extract_then_aggregate` | Long documents: extract per document, then aggregate | take home |
| `05_rewriting` | Cleaning and standardising text (firm names) | take home |
| `06_bonus_patent_task_match` | Matching patents to occupational tasks | take home |
| `07_your_data` | The same pipeline on your own CSV | take home |
| `09_bibliometrics_lenses` | More views on the field map | take home |

Every answer is saved in `../outputs_cached/`, so the notebooks replay offline. No internet? Set `DRY_RUN=1` in `../config.env` and restart the kernel.

`prompts_chatbot_track.md` is the same lesson for any chatbot, without code.
