"""Full live run of every notebook, so all answers land in outputs_cached/ for offline replay.

Usage (from the workshop folder, with API_KEY set in config.env and Ollama running):
    python organisers/build/make_cache.py

Takes about 25 minutes at RPM=10 (roughly 200 API calls). Safe to re-run: answers already in
outputs_cached/ are reused, so a second run only fills the gaps. Executed copies of the
notebooks (with outputs) are written to outputs/executed/.
"""
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from workshop import llm  # noqa: E402

cfg = llm.load_config()
if cfg["dry_run"] or not cfg["api_key"]:
    sys.exit("make_cache.py needs a live setup: set API_KEY and DRY_RUN=0 in config.env.")
llm.status()
if llm.ollama_ready() != "ready":
    print(f"WARNING: decision model not ready, so notebook A6 answers won't be cached. Run: ollama pull {cfg['decision_model']}")

log = ROOT / "outputs" / "make_cache_calls.log"
log.parent.mkdir(exist_ok=True)
log.unlink(missing_ok=True)
env = {**os.environ, "WORKSHOP_CALL_LOG": str(log), "DRY_RUN": "0"}
failed = []
for nb in sorted((ROOT / "lesson1_text_to_data").glob("0*.ipynb")) + sorted((ROOT / "additional_materials").glob("A*.ipynb")):
    print(f"\n=== {nb.name}", flush=True)
    r = subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", str(nb),
                        "--output-dir", str(ROOT / "outputs" / "executed"), "--ExecutePreprocessor.timeout=3600",
                        "--log-level=ERROR"], env=env, cwd=nb.parent)
    if r.returncode:
        failed.append(nb.name)
    time.sleep(60)  # each notebook is a new process with a fresh rate limiter: let the RPM window clear

sources = Counter(line.split("\t")[0] for line in log.read_text(encoding="utf-8").splitlines()) if log.exists() else {}
print(f"\nAPI calls this run: {sources.get('live', 0)} live, {sources.get('cache', 0)} replayed from cache")
print(f"Cache now holds {len(list(llm.CACHE_DIR.glob('*.json')))} answers in outputs_cached/")
print("Notebooks with errors:", failed or "none", "(see outputs/executed/)")
