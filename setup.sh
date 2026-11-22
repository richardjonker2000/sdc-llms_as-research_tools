#!/usr/bin/env bash
# One-shot setup for the demo laptop (macOS or Linux). Safe to re-run.
#
#   ./setup.sh                 notebooks + OpenCode + agent demo folder in ~/sdc_agent_demo
#   ./setup.sh --china         same, with the Tsinghua PyPI mirror
#   ./setup.sh --demo-dir DIR  put the agent demo folder somewhere else
#   ./setup.sh --reset-demo    move an existing demo folder aside (DIR.bak-<time>) and build a fresh one
#   ./setup.sh --cache-from SRC  copy saved answers + embeddings (outputs_cached/) from a folder, USB stick
#                              or another machine (rsync syntax, e.g. me@desktop:~/projects/sdc_work/outputs_cached)
#   ./setup.sh --no-ollama     skip Ollama and the decision model
#
# What it does:
#   1. finds Python 3.10-3.12
#   2. .venv in this folder with requirements.txt (the notebooks)
#   3. config.env from config.example.env; asks for the API key (input hidden, stored only in config.env)
#   4. OpenCode 1.19.5 into ~/.local/bin (skipped if that version is already on PATH)
#   5. a copy of lesson2_agentic_coding/agent_harness/ as its own git project with its own .venv, DRY_RUN=1, and start_agent.sh
#   6. Ollama >= 0.40 (Linux: into ~/.local/ollama, no sudo; macOS: Homebrew), starts it,
#      pulls the decision model (DECISION_MODEL in config.env, default tev1:0.8b, 833 MB) and tests it
#   7. outputs_cached/ (with --cache-from), then runs lesson1_text_to_data/00_setup headless: must say "Connection OK"
set -euo pipefail

OPENCODE_VERSION=1.19.5
HERE="$(cd "$(dirname "$0")" && pwd)"
DEMO_DIR="$HOME/sdc_agent_demo"
PIP_INDEX=()
RESET=0
CACHE_FROM=""
OLLAMA=1
OLLAMA_MIN=0.40.0
OLLAMA_VERSION=0.40.15     # tested; Linux download ~1.5 GB (includes GPU libraries)
export PIP_DISABLE_PIP_VERSION_CHECK=1
while [ $# -gt 0 ]; do
  case "$1" in
    --china) PIP_INDEX=(--index-url https://pypi.tuna.tsinghua.edu.cn/simple) ;;
    --demo-dir) DEMO_DIR="$2"; shift ;;
    --reset-demo) RESET=1 ;;
    --cache-from) CACHE_FROM="$2"; shift ;;
    --no-ollama) OLLAMA=0 ;;
    -h|--help) sed -n '2,23p' "$0"; exit 0 ;;
    *) echo "unknown option: $1"; exit 1 ;;
  esac
  shift
done
say() { printf '\n\033[1m== %s\033[0m\n' "$*"; }
warn() { printf '\033[33mWARNING: %s\033[0m\n' "$*"; }
# venv with the standard library; falls back to uv where python3-venv is missing (Debian/Ubuntu)
make_venv() {
  if [ -x "$1/bin/python" ] && "$1/bin/python" -c 'import sys' 2>/dev/null; then return; fi
  rm -rf "$1"
  if "$PY" -m venv "$1" >/dev/null 2>&1; then return; fi
  rm -rf "$1"
  if command -v uv >/dev/null 2>&1; then uv venv -q --python "$PY" "$1"; return; fi
  echo "Could not create a virtual environment. Either: sudo apt install python3-venv  (Debian/Ubuntu)"
  echo "or install uv (no sudo): curl -LsSf https://astral.sh/uv/install.sh | sh   then re-run ./setup.sh"
  exit 1
}
pip_in() {  # pip_in <venv> <pip args...>
  local v="$1"; shift
  if "$v/bin/python" -m pip --version >/dev/null 2>&1; then "$v/bin/python" -m pip install -q "$@" "${PIP_INDEX[@]}"
  else uv pip install -q --python "$v/bin/python" "$@" "${PIP_INDEX[@]}"; fi
}

# ---------------------------------------------------------------- 1. Python
say "1/7 Python"
PY=""
for c in python3.12 python3.11 python3.10 python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(not ((3,10) <= sys.version_info[:2] <= (3,12)))' 2>/dev/null; then
    PY="$(command -v "$c")"; break
  fi
done
[ -n "$PY" ] || { echo "Need Python 3.10, 3.11 or 3.12 (python.org; macOS: brew install python@3.12)."; exit 1; }
echo "using $PY ($("$PY" --version))"
command -v git >/dev/null || { echo "Need git (macOS: xcode-select --install)."; exit 1; }

# ---------------------------------------------------------------- 2. notebook environment
say "2/7 Notebook environment (.venv, a few minutes the first time)"
make_venv "$HERE/.venv"
pip_in "$HERE/.venv" -r "$HERE/requirements-dev.txt"
(cd "$HERE" && .venv/bin/python -m pytest -q tests | tail -1)

# ---------------------------------------------------------------- 3. config.env + key
say "3/7 config.env"
CFG="$HERE/config.env"
[ -f "$CFG" ] || cp "$HERE/config.example.env" "$CFG"
key_in_cfg() { grep -E '^API_KEY=' "$CFG" | cut -d= -f2- | awk '{print $1}'; }
if [ -z "$(key_in_cfg)" ]; then
  if [ -t 0 ]; then
    printf 'Paste the MiniMax China API key (input hidden; Enter to skip and use DRY_RUN): '
    read -rs KEY; echo
    if [ -n "$KEY" ]; then
      "$HERE/.venv/bin/python" - "$CFG" "$KEY" <<'EOF'
import sys, re, pathlib
p, key = pathlib.Path(sys.argv[1]), sys.argv[2]
s = p.read_text(encoding="utf-8")
p.write_text(re.sub(r"(?m)^API_KEY=.*$", lambda m: "API_KEY=" + key, s), encoding="utf-8")
EOF
      echo "key saved in config.env (git-ignored)"
    fi
  fi
fi
if [ -z "$(key_in_cfg)" ]; then
  sed -i.bak 's/^DRY_RUN=.*/DRY_RUN=1/' "$CFG" && rm -f "$CFG.bak"
  warn "no API key: config.env set to DRY_RUN=1 (fake answers). Add API_KEY= later and set DRY_RUN=0."
else
  echo "API key present ($(key_in_cfg | wc -c | tr -d ' ') characters, not shown)"
fi

# ---------------------------------------------------------------- 4. OpenCode
say "4/7 OpenCode $OPENCODE_VERSION"
OC="$(command -v opencode || true)"
if [ -n "$OC" ] && [ "$("$OC" --version 2>/dev/null)" = "$OPENCODE_VERSION" ]; then
  echo "already installed: $OC"
else
  case "$(uname -s)-$(uname -m)" in
    Linux-x86_64)  ASSET=opencode-linux-x64.tar.gz ;;
    Linux-aarch64) ASSET=opencode-linux-arm64.tar.gz ;;
    Darwin-arm64)  ASSET=opencode-darwin-arm64.zip ;;
    Darwin-x86_64) ASSET=opencode-darwin-x64.zip ;;
    *) echo "No OpenCode build for $(uname -s)-$(uname -m); get it from https://opencode.ai/download"; exit 1 ;;
  esac
  URL="https://github.com/anomalyco/opencode/releases/download/v$OPENCODE_VERSION/$ASSET"
  TMP="$(mktemp -d)"
  echo "downloading $ASSET (~70-100 MB; slow in China: or copy the binary from USB to ~/.local/bin/opencode)"
  curl -fL --progress-bar -o "$TMP/$ASSET" "$URL"
  case "$ASSET" in *.zip) (cd "$TMP" && unzip -q "$ASSET") ;; *) tar -xzf "$TMP/$ASSET" -C "$TMP" ;; esac
  mkdir -p "$HOME/.local/bin"
  mv "$TMP/opencode" "$HOME/.local/bin/opencode"; chmod +x "$HOME/.local/bin/opencode"
  rm -rf "$TMP"
  OC="$HOME/.local/bin/opencode"
  echo "installed $OC ($("$OC" --version))"
  case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) warn "~/.local/bin is not on your PATH; start_agent.sh works anyway. To type 'opencode' directly: echo 'export PATH=\$HOME/.local/bin:\$PATH' >> ~/.zshrc (or ~/.bashrc)" ;; esac
fi

# ---------------------------------------------------------------- 5. agent demo folder
say "5/7 Agent demo folder: $DEMO_DIR"
if [ -e "$DEMO_DIR" ]; then
  if [ "$RESET" = 1 ]; then
    BAK="$DEMO_DIR.bak-$(date +%Y%m%d-%H%M%S)"; mv "$DEMO_DIR" "$BAK"; echo "old demo moved to $BAK"
  else
    echo "exists already: keeping it (use --reset-demo for a fresh one)"
  fi
fi
if [ ! -e "$DEMO_DIR" ]; then
  mkdir -p "$DEMO_DIR"
  (cd "$HERE/lesson2_agentic_coding/agent_harness" && tar -cf - --exclude .venv --exclude config.env --exclude __pycache__ .) | (cd "$DEMO_DIR" && tar -xf -)
  make_venv "$DEMO_DIR/.venv"
  pip_in "$DEMO_DIR/.venv" -r "$DEMO_DIR/requirements.txt"
  # the demo starts in dry run: fake LLM answers until the researcher goes live
  sed 's/^DRY_RUN=.*/DRY_RUN=1/' "$CFG" > "$DEMO_DIR/config.env"
  # saved answers: the agent's LLM coding replays notebook 01's answers instead of calling the API
  ln -s "$HERE/outputs_cached" "$DEMO_DIR/outputs_cached"
  cat > "$DEMO_DIR/start_agent.sh" <<EOF
#!/usr/bin/env bash
# Starts OpenCode in this folder with the key from config.env (never printed).
# Other model:  ./start_agent.sh -m minimax-cn/MiniMax-M3.1-Flash   (e.g. for a pay-as-you-go key)
cd "\$(dirname "\$0")"
export MINIMAX_API_KEY="\$(grep -E '^API_KEY=' config.env | cut -d= -f2- | awk '{print \$1}')"
[ -n "\$MINIMAX_API_KEY" ] || echo "No API_KEY in config.env: the agent cannot reach the model."
exec "$OC" "\$@"
EOF
  chmod +x "$DEMO_DIR/start_agent.sh"
  ( cd "$DEMO_DIR"
    git init -q
    git config user.name "Researcher (workshop)"; git config user.email researcher@workshop.local
    printf '%s\n' start_agent.sh >> .gitignore
    git add -A && git commit -qm "Starter: data, rules, agents, commands, skill"
    .venv/bin/python tools/check_env.py | head -3 )
fi

# ---------------------------------------------------------------- 6. Ollama + decision model
cfg_val() { grep -E "^$1=" "$CFG" | cut -d= -f2- | awk '{print $1}'; }
ver_ge() { [ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | head -1)" = "$2" ]; }   # ver_ge A B: A >= B
OLLAMA_STATUS="skipped (--no-ollama)"
if [ "$OLLAMA" = 1 ]; then
  say "6/7 Ollama + decision model (notebook 03)"
  OURL="$(cfg_val OLLAMA_URL)"; OURL="${OURL:-http://localhost:11434}"
  DMODEL="$(cfg_val DECISION_MODEL)"; DMODEL="${DMODEL:-tev1:0.8b}"
  export OLLAMA_HOST="${OURL#http://}"
  oll_ver() { ollama --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | tail -1; }
  if ! command -v ollama >/dev/null 2>&1 || ! ver_ge "$(oll_ver)" "$OLLAMA_MIN"; then
    command -v ollama >/dev/null 2>&1 && echo "Ollama $(oll_ver) is too old (need $OLLAMA_MIN+; tev1 models fail on 0.35)" || echo "Ollama not found"
    case "$(uname -s)" in
      Linux)
        # No sudo, no apt: unpack the official release into ~/.local/ollama. The release is .tar.zst;
        # without the zstd tool we decompress with Python's zstandard package (works when apt is broken).
        case "$(uname -m)" in x86_64) OARCH=amd64 ;; aarch64) OARCH=arm64 ;; *) echo "unsupported CPU $(uname -m)"; exit 1 ;; esac
        OURL_DL="https://github.com/ollama/ollama/releases/download/v$OLLAMA_VERSION/ollama-linux-$OARCH.tar.zst"
        # Unpacked it is ~2.4 GB (mostly NVIDIA GPU libraries), plus 833 MB for the model.
        NEED_MB=3600
        echo "Installing Ollama $OLLAMA_VERSION into ~/.local/ollama (no sudo; ~1.5 GB download, ~2.4 GB on disk)"
        rm -rf "$HOME/.local/ollama.new"
        FREE_MB=$(df -Pm "$HOME" | awk 'NR==2 {print $4}')
        [ "$FREE_MB" -ge "$NEED_MB" ] || { echo "Only $FREE_MB MB free in $HOME; need about $NEED_MB MB (Ollama + the 833 MB model). Free some space and re-run."; exit 1; }
        mkdir -p "$HOME/.local/ollama.new" "$HOME/.local/bin"
        if command -v zstd >/dev/null 2>&1; then UNZST=(zstd -d -c)
        else pip_in "$HERE/.venv" zstandard
             UNZST=("$HERE/.venv/bin/python" -c "import sys, zstandard; zstandard.ZstdDecompressor().copy_stream(sys.stdin.buffer, sys.stdout.buffer)"); fi
        curl -fL --progress-bar "$OURL_DL" | "${UNZST[@]}" | tar -x -C "$HOME/.local/ollama.new"
        rm -rf "$HOME/.local/ollama"; mv "$HOME/.local/ollama.new" "$HOME/.local/ollama"
        ln -sf "$HOME/.local/ollama/bin/ollama" "$HOME/.local/bin/ollama"
        export PATH="$HOME/.local/bin:$PATH" ;;
      Darwin)
        if command -v brew >/dev/null 2>&1; then brew install ollama || brew upgrade ollama
        else echo "Install the Ollama app from https://ollama.com/download (or install Homebrew), then re-run ./setup.sh"; exit 1; fi ;;
    esac
    hash -r
  fi
  echo "Ollama $(oll_ver)"
  if ! curl -fs "$OURL/api/version" >/dev/null 2>&1; then
    echo "starting the Ollama server (log: ~/.ollama_serve.log)"
    if [ "$(uname -s)" = Darwin ] && command -v brew >/dev/null 2>&1 && brew list ollama >/dev/null 2>&1; then brew services start ollama >/dev/null
    else nohup ollama serve > "$HOME/.ollama_serve.log" 2>&1 & fi
    for _ in $(seq 1 20); do curl -fs "$OURL/api/version" >/dev/null 2>&1 && break; sleep 1; done
  fi
  curl -fs "$OURL/api/version" >/dev/null 2>&1 || { echo "Ollama server not reachable at $OURL (see ~/.ollama_serve.log)"; exit 1; }
  SERVER_VER="$(curl -fs "$OURL/api/version" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')"
  ver_ge "$SERVER_VER" "$OLLAMA_MIN" || { echo "The running Ollama server is $SERVER_VER (too old). Quit/stop it, then re-run ./setup.sh"; exit 1; }
  if ollama list 2>/dev/null | awk '{print $1}' | grep -qx "$DMODEL"; then echo "$DMODEL already pulled"
  else echo "pulling $DMODEL (833 MB for tev1:0.8b, once)"; ollama pull "$DMODEL"; fi
  (cd "$HERE" && .venv/bin/python - <<'EOF'
import workshop.llm as L
L.CFG["dry_run"] = False          # test the real local model even when config.env says DRY_RUN=1
r = L.decide("Write a short summary of a research paper", {"can_do": {"type": "choice",
    "instructions": "Could a language model do this work task?",
    "criteria": {"yes": "reading, writing or analysing text", "no": "physical or in-person work"}}}, use_cache=False)
print("decision model answer:", r)
EOF
  ) && OLLAMA_STATUS="ok: Ollama $SERVER_VER, $DMODEL" || { OLLAMA_STATUS="FAILED: see the error above"; warn "decision model test failed"; }
fi

# ---------------------------------------------------------------- 7. saved answers + notebook check
say "7/7 Saved answers and notebook check"
if [ -n "$CACHE_FROM" ]; then
  mkdir -p "$HERE/outputs_cached"
  if command -v rsync >/dev/null 2>&1; then rsync -a "${CACHE_FROM%/}/" "$HERE/outputs_cached/"
  else cp -R "${CACHE_FROM%/}/." "$HERE/outputs_cached/"; fi
fi
NCACHE=$(find "$HERE/outputs_cached" -name '*.json' 2>/dev/null | wc -l | tr -d ' ')
if [ "$NCACHE" -gt 0 ]; then echo "outputs_cached/: $NCACHE saved answers"
else warn "outputs_cached/ is empty: notebooks will call the API for every answer (about 200 calls). Get it with --cache-from <path>"; fi
NB_OUT="$(mktemp -d)"
if (cd "$HERE/lesson1_text_to_data" && ../.venv/bin/jupyter nbconvert --to notebook --execute 00_setup.ipynb --output-dir "$NB_OUT" \
      --ExecutePreprocessor.timeout=300 >"$NB_OUT/log.txt" 2>&1); then
  # look only at what the cells printed (the source code contains the words too)
  NB_STATUS="$("$HERE/.venv/bin/python" - "$NB_OUT/00_setup.ipynb" <<'EOF'
import json, sys
out = "".join("".join(o.get("text", "")) for c in json.load(open(sys.argv[1], encoding="utf-8"))["cells"]
              if c["cell_type"] == "code" for o in c.get("outputs", []))
if "Connection OK" not in out:
    print("FAILED: 00_setup did not reach Connection OK; open it in Jupyter to see the red items")
else:
    print("ok: 00_setup says Connection OK" + (" (DRY RUN: chat answers are fake; set API_KEY and DRY_RUN=0 for live)" if "dry run" in out.split("Connection OK")[1][:60] else " (live)"))
EOF
)"
else
  NB_STATUS="FAILED: notebook 00 crashed (log: $NB_OUT/log.txt)"
fi
echo "$NB_STATUS"

say "Done"
echo "Ollama:      $OLLAMA_STATUS"
echo "Notebook 00: $NB_STATUS"
cat <<EOF
Notebooks:   cd "$HERE" && source .venv/bin/activate && jupyter lab     (open lesson1_text_to_data/00_setup.ipynb first)
Agent demo:  cd "$DEMO_DIR" && ./start_agent.sh
             then type:  /plan  (the research question is in lesson2_agentic_coding/demo/DEMO.md)
             go live for LLM coding: set DRY_RUN=0 in $DEMO_DIR/config.env
Fresh demo:  ./setup.sh --reset-demo
EOF
