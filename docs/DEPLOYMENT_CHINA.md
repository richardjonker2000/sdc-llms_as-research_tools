# Deployment notes: China and local requirements

Working notes for the organisers (status 11 Nov 2026). **Tested** means it ran on the build laptop in Europe. **Untested in China** means it still needs a check from inside mainland China, ideally on the UCAS Yanqihu campus Wi-Fi, before 25 Nov.

## 1. What each participant's laptop needs

| Item | Needed for | Size | Notes |
| --- | --- | --- | --- |
| Python 3.10–3.12 | everything | ~30 MB installer | Windows: tick *Add python.exe to PATH*. 3.13+ untested. |
| Packages from `requirements.txt` | notebooks | ~430 MB in `.venv` (mostly JupyterLab) | Use a PyPI mirror in China (section 3). |
| `config.env` with the workshop key | live LLM calls | – | `PROVIDER=minimax_cn`. Without a key: `DRY_RUN=1`. |
| `outputs_cached/` | offline replay, notebook 08 embeddings | ~66 MB (50 MB of it embeddings) | **Not in git.** Build with `make_cache.py` and hand out on USB or a shared drive. |
| Ollama ≥ 0.40 + `tev1:0.8b` | notebook 03 only | 833 MB model | 0.35 is too old. Runs on CPU, about 3 decisions/s. |
| A CJK font | Chinese labels in figures | – | Windows and macOS have one (Microsoft YaHei / PingFang SC). Linux: install Noto Sans CJK. |
| Agent session only: OpenCode binary, git | `agent_harness/` | ~215 MB binary | See section 5. Windows needs *Git for Windows*. |

Disk: about 1.5 GB with Ollama and the model, about 0.6 GB without. RAM: 8 GB is enough.

**Folder location.** Put the workshop folder at a short ASCII path without spaces, for example `C:\sdc` or `~/sdc`. Windows user names in Chinese (`C:\Users\张三\...`) break some tools. `agent_harness/tools/check_env.py` warns about this.

## 2. LLM providers from China

| Provider (`PROVIDER=`) | Endpoint | From China |
| --- | --- | --- |
| `minimax_cn` (**default for Beijing**) | `https://api.minimax.cn/v1` (old host `api.minimaxi.com` still works) | Domestic service. Tested from Europe; untested in China. |
| `deepseek` | `https://api.deepseek.com` | Domestic. Set `MODEL=`. |
| `qwen` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | Domestic. Set `MODEL=`. |
| `modelscope` | `https://api-inference.modelscope.cn/v1` | Domestic; free daily quota. Set `MODEL=`. |
| `minimax_intl` | `https://api.minimax.io/v1` | International host; may be slow. Use `minimax_cn`. |
| `gemini` | `generativelanguage.googleapis.com` | **Blocked** in mainland China. Only for the Danish side. |
| `ollama` | `http://localhost:11434` | Local, no network. |

Embeddings (notebook 08): `embo-01` on MiniMax, `gemini-embedding-001` on Gemini. The embeddings for the prepared fields are in `outputs_cached/embeddings/`, so notebooks 08 and 09 need no embedding calls for those fields.

**Keys:**
- The workshop uses its **own pay-as-you-go MiniMax key**.
- The personal Token Plan key used during development must not be given to participants. Rotate it once testing is finished.
- Keys live only in `config.env`, which is git-ignored, and never in notebooks or outputs.
- Paid keys: `RPM=60`. Free tiers: `RPM=10`.

## 3. Installing in China

- **pip:** `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`. Fallback: `https://mirrors.aliyun.com/pypi/simple/`.
- **Python and Ollama installers:** python.org and ollama.com can be slow. Put the installers on the USB stick: Windows x64, macOS universal.
- **Ollama model:** `ollama pull` uses ollama.com's registry, which may be slow or fail. Copy the model folder from a prepared machine instead: `~/.ollama/models`, or the folder set by `OLLAMA_MODELS`.
- **GitHub:** may be slow; `git clone` can fail on campus. Hand out a zip of this repo plus `outputs_cached/` on USB.
- **Hugging Face:** blocked. This only matters for `tools/fetch_patents.py`, which the organiser runs, never participants. A mirror is `HF_ENDPOINT=https://hf-mirror.com`.
- **OpenAlex (`api.openalex.org`):** untested in China. Without it, notebook 08 still works with the prepared samples in `data/openalex/` (`ai_labour`, `green_innovation`, `china_innovation`). Searching your own topic needs `OPENALEX_API_KEY` and access.

## 4. Fallbacks on the day

- **No internet:** set `DRY_RUN=1` and restart the kernel.
  - Answers in `outputs_cached/` replay as real.
  - New prompts get clearly fake answers, so every cell still runs.
  - Ollama (notebook 03) keeps working.
- **Rate limits:** lower `RPM`. Re-running a cell only calls the API again for rows that failed.
- More detail is in `facilitator_notes.md`.

## 5. Agent session (`agent_harness/`): extra requirements and open issues

What has been tested so far (build laptop, Linux):
- **Setup:** OpenCode 1.19.5 with `minimax-cn-coding-plan/MiniMax-M3.1-Flash` (Anthropic-compatible endpoint `api.minimax.cn/anthropic/v1`, key in env var `MINIMAX_API_KEY`).
- **Pilot run:** a 7-turn simulated researcher session with plan → discuss → one step per turn. Each turn took 2–4 minutes and re-read 0.4–1.3 M cached input tokens.

Open items before using it with students:

1. **Key and provider.** `minimax-cn-coding-plan` is for Token Plan keys. A pay-as-you-go key probably needs the `minimax-cn` provider instead: **verify**, then update `"model"` in `agent_harness/opencode.json`.
2. **Cost per student.** Measure tokens per session against the pay-as-you-go price sheet before deciding how many students run it live. The alternative is pairs, or a facilitator demo.
3. **Windows paths.** The permission allowlist in `opencode.json` matches `.venv/bin/python ...`. On Windows the interpreter is `.venv\Scripts\python.exe`, so every Python call would hit `ask`, which rejects in `opencode run`. Add Windows patterns and test on a Windows laptop.
4. **Getting OpenCode in China.**
   - The binary downloads from GitHub releases, which are slow. Put the per-OS binaries on USB: Windows x64, macOS arm64 and x64.
   - Alternative: npm via `https://registry.npmmirror.com` (package `opencode-ai`; verify).
5. **Startup fetch.** OpenCode fetches the model list from `models.dev` at startup. Test from China whether this hangs; if it does, find the setting or env var that disables or caches it.
6. **Git.** The harness commits after every step, so git must be installed. Pre-set the git identity, because the agent is not allowed to run `git config`.
7. **Harness rule changes from the pilot:**
   - cap at 3–4 open decisions per round;
   - numbers in chat must be copied from script output;
   - always produce a researcher check sheet when the LLM labels data.
8. **Keep `DRY_RUN=1`** in the harness's `config.env` by default. Only the researcher switches live calls on.

## 6. Content

- All data is public (USPTO/PatentsView, O\*NET, ClinicalTrials.gov, OpenAlex) or synthetic. See `data/README.md` for licences.
- Keep examples on innovation, firms and patents.
- Still to review: the topic sensitivity of the notebook 08 examples (`robots_china`) for the Beijing audience.
