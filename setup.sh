#!/usr/bin/env bash
# One-shot setup for the demo laptop (macOS or Linux). Safe to re-run.
#
#   ./setup.sh                 notebooks + OpenCode + agent demo folder in ~/sdc_agent_demo
#   ./setup.sh --china         same, with the Tsinghua PyPI mirror
#   ./setup.sh --demo-dir DIR  put the agent demo folder somewhere else
#   ./setup.sh --reset-demo    move an existing demo folder aside (DIR.bak-<time>) and build a fresh one
#
# What it does:
#   1. finds Python 3.10-3.12
#   2. .venv in this folder with requirements.txt (the notebooks)
#   3. config.env from config.example.env; asks for the API key (input hidden, stored only in config.env)
#   4. OpenCode 1.19.5 into ~/.local/bin (skipped if that version is already on PATH)
#   5. a copy of agent_harness/ as its own git project with its own .venv, DRY_RUN=1, and start_agent.sh
# It never uses sudo. Ollama (notebook 03 only) is not installed: see README step 2.
set -euo pipefail

OPENCODE_VERSION=1.19.5
HERE="$(cd "$(dirname "$0")" && pwd)"
DEMO_DIR="$HOME/sdc_agent_demo"
PIP_INDEX=()
RESET=0
while [ $# -gt 0 ]; do
  case "$1" in
    --china) PIP_INDEX=(--index-url https://pypi.tuna.tsinghua.edu.cn/simple) ;;
    --demo-dir) DEMO_DIR="$2"; shift ;;
    --reset-demo) RESET=1 ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
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
say "1/5 Python"
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
say "2/5 Notebook environment (.venv, a few minutes the first time)"
make_venv "$HERE/.venv"
pip_in "$HERE/.venv" -r "$HERE/requirements-dev.txt"
(cd "$HERE" && .venv/bin/python -m pytest -q tests | tail -1)

# ---------------------------------------------------------------- 3. config.env + key
say "3/5 config.env"
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
say "4/5 OpenCode $OPENCODE_VERSION"
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
say "5/5 Agent demo folder: $DEMO_DIR"
if [ -e "$DEMO_DIR" ]; then
  if [ "$RESET" = 1 ]; then
    BAK="$DEMO_DIR.bak-$(date +%Y%m%d-%H%M%S)"; mv "$DEMO_DIR" "$BAK"; echo "old demo moved to $BAK"
  else
    echo "exists already: keeping it (use --reset-demo for a fresh one)"
  fi
fi
if [ ! -e "$DEMO_DIR" ]; then
  mkdir -p "$DEMO_DIR"
  (cd "$HERE/agent_harness" && tar -cf - --exclude .venv --exclude config.env --exclude __pycache__ .) | (cd "$DEMO_DIR" && tar -xf -)
  make_venv "$DEMO_DIR/.venv"
  pip_in "$DEMO_DIR/.venv" -r "$DEMO_DIR/requirements.txt"
  # the demo starts in dry run: fake LLM answers until the researcher goes live
  sed 's/^DRY_RUN=.*/DRY_RUN=1/' "$CFG" > "$DEMO_DIR/config.env"
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

say "Done"
cat <<EOF
Notebooks:   cd "$HERE" && source .venv/bin/activate && jupyter lab     (open notebooks/00_setup.ipynb first)
Agent demo:  cd "$DEMO_DIR" && ./start_agent.sh
             then type:  /plan Do AI patents automate rather than augment work, and do Chinese and US firms differ?
             go live for LLM coding: set DRY_RUN=0 in $DEMO_DIR/config.env
Fresh demo:  ./setup.sh --reset-demo
Optional:    Ollama + 'ollama pull tev1:0.8b' for notebook 03 (README step 2)
EOF
