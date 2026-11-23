# From text to dataset: LLMs as research tools

SDC workshop *New Tools, Old Questions* · Wed 25 Nov 2026 · Sino-Danish Center, UCAS Yanqihu Campus

Two hands-on lessons. No coding experience needed.

| | Lesson | Folder |
| --- | --- | --- |
| 11:30–12:30 | **1 · What LLMs can do with text:** coding with a codebook, checking agreement, mapping a field | `lesson1_text_to_data/` |
| 14:00–15:00 | **2 · Agentic coding:** a coding agent, and skill files that turn your notebook into instructions | `lesson2_agentic_coding/` |

```
lesson1_text_to_data/     the lesson 1 notebooks (start with 00_setup)
lesson2_agentic_coding/   the agent project, its skills, and a template for your own skill
additional_materials/     more notebooks for after the workshop, starting with A1 · your own data
data/                     all datasets (sources and licences in data/README.md)
workshop/                 the small helper module the notebooks use
outputs/                  your results
organisers/               not needed by participants
```

## Install (on your own laptop)

On the workshop's Jupyter server everything is ready: open `lesson1_text_to_data/00_setup.ipynb`.

On your own laptop you need **Python 3.10–3.12**. In a terminal, in this folder:

| | Windows | macOS / Linux |
| --- | --- | --- |
| Create environment | `python -m venv .venv` | `python3 -m venv .venv` |
| Activate it | `.venv\Scripts\activate` | `source .venv/bin/activate` |
| Install packages | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| Start Jupyter | `jupyter lab` | `jupyter lab` |

In mainland China add `-i https://pypi.tuna.tsinghua.edu.cn/simple` to the `pip install` line.

## Settings: `config.env`

Copy `config.example.env` to `config.env` and fill in two lines:

```
PROVIDER=minimax_cn     # in China; gemini works outside China
API_KEY=your-key-here
```

Other providers: `deepseek`, `qwen`, `modelscope` (free daily quota; set `MODEL=` for these three), `minimax_intl`, `ollama`. Your key stays in `config.env` and never appears in a notebook. Never share that file.

**Three modes.** *Live*: new prompts call the API. *Cached*: answers saved in `outputs_cached/` replay instantly, in every mode. *Dry run* (`DRY_RUN=1`): no network; anything not saved gets a clearly marked **fake** answer, so every cell still runs.

Then run `lesson1_text_to_data/00_setup.ipynb`. It should say **Connection OK**.

## Troubleshooting

| You see | Fix |
| --- | --- |
| `No module named 'workshop'` | Start Jupyter from this folder with the environment activated, and open notebooks from their folders. |
| `No API_KEY` | Create `config.env`, then **Kernel ▸ Restart Kernel** (changes need a restart). |
| `API key rejected (401)` | The key doesn't belong to the `PROVIDER` you set. |
| `Can't reach ...` / `403` | No internet, or a blocked provider (Gemini doesn't work from mainland China). Offline? `DRY_RUN=1`. |
| `Model ... not found` | Set `MODEL=` to a model your provider offers. |
| `Rate limit (429)` | Lower `RPM` in `config.env`, or wait. Saved answers are never lost. |

A value in the `error` column of a results table is one row that failed; the rest of the run carried on.

## Attribution

This workshop includes information from the O\*NET 31.0 Database by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license. O\*NET® is a trademark of USDOL/ETA. The workshop organisers have modified all or some of this information. USDOL/ETA has not approved, endorsed, or tested these modifications. Patent data: USPTO via PatentsView (CC BY 4.0). Literature: OpenAlex (CC0). Clinical trials: ClinicalTrials.gov. Interview snippets are synthetic.
