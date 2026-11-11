"""Check the project environment and record it. Read-only: installs nothing.

Run with the project's Python:  .venv/bin/python tools/check_env.py   (Windows: .venv\\Scripts\\python.exe tools\\check_env.py)
"""
import platform, sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CJK_FONTS = ["Microsoft YaHei", "SimHei", "PingFang SC", "Heiti SC", "Noto Sans CJK SC", "Noto Sans SC",
             "Source Han Sans SC", "WenQuanYi Zen Hei", "Arial Unicode MS"]
problems, warnings = [], []
lines = [f"python {platform.python_version()} ({sys.executable})", f"platform {platform.platform()}"]

# 1. the right interpreter
if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
    win = platform.system() == "Windows"
    problems.append(f"running {sys.executable}, not the project .venv. Use "
                    + (r".venv\Scripts\python.exe" if win else ".venv/bin/python"))

# 2. pinned packages
for req in (ROOT / "requirements.txt").read_text(encoding="utf-8").split():
    name, _, want = req.partition("==")
    try:
        have = metadata.version(name)
    except metadata.PackageNotFoundError:
        problems.append(f"{name} not installed (want {want})"); continue
    lines.append(f"{name}=={have}")
    if want and have != want:
        warnings.append(f"{name} {have} installed, requirements.txt pins {want}: numbers may differ from the reference")

# 3. a font that can draw Chinese
try:
    from matplotlib import font_manager
    have_fonts = {f.name for f in font_manager.fontManager.ttflist}
    cjk = next((f for f in CJK_FONTS if f in have_fonts), None)
    lines.append(f"cjk_font {cjk or 'none'}")
    if not cjk:
        warnings.append("no Chinese-capable font found: Chinese labels in figures will show as boxes")
except ImportError:
    pass

# 4. paths and encodings that break tools
if any(ord(ch) > 127 for ch in str(ROOT)) or " " in str(ROOT):
    warnings.append(f"project path {ROOT} has spaces or non-ASCII characters; some tools fail on such paths")
lines.append(f"default_encoding {sys.getdefaultencoding()} / filesystem {sys.getfilesystemencoding()} / "
             f"locale-preferred {__import__('locale').getpreferredencoding(False)}")

for w in warnings:
    print("WARNING:", w)
if problems:
    print("ENV PROBLEM"); print("\n".join("- " + p for p in problems)); sys.exit(1)
(ROOT / "outputs").mkdir(exist_ok=True)
(ROOT / "outputs/ENVIRONMENT.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("ENV OK"); print("\n".join(lines))
