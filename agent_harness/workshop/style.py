"""One consistent, quiet matplotlib look for every workshop chart."""
import matplotlib.pyplot as plt

# Validated colour-blind-safe categorical order (blue, orange, aqua, yellow, magenta, green, violet, red)
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
GREY = "#a3a29c"

# Fonts that can draw Chinese: Windows, macOS, Linux. Older matplotlib names Noto's .ttc "Noto Sans CJK JP" (same glyphs).
CJK_FONTS = ["Microsoft YaHei", "SimHei", "PingFang SC", "Hiragino Sans GB", "Heiti SC", "STHeiti", "Songti SC", "Noto Sans CJK SC", "Noto Sans CJK JP", "Noto Sans CJK TC", "Noto Sans SC", "Source Han Sans SC", "WenQuanYi Zen Hei", "WenQuanYi Micro Hei", "Droid Sans Fallback", "Arial Unicode MS"]


def cjk_font() -> list[str]:
    """The first installed font that can draw Chinese, as a one-item list (empty if none)."""
    from matplotlib import font_manager
    have = {f.name for f in font_manager.fontManager.ttflist}
    return [f for f in CJK_FONTS if f in have][:1]


def setup_plots() -> None:
    plt.rcParams.update({
        "figure.figsize": (7, 3.8), "figure.dpi": 110, "figure.facecolor": "#fcfcfb",
        "axes.facecolor": "#fcfcfb", "axes.prop_cycle": plt.cycler(color=COLORS),
        "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#52514e",
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": "#e6e5e0", "grid.linewidth": 0.8,
        "axes.axisbelow": True, "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
        "font.size": 10, "lines.linewidth": 2, "lines.markersize": 7,
        # DejaVu Sans for Latin text; Chinese characters fall back to the first CJK font found (see cjk_font)
        "font.family": ["DejaVu Sans", *cjk_font()],
    })


def show_diff(before: str, after: str) -> None:
    """Show a before/after text diff in the notebook: removed text struck out in red, new text in green."""
    import difflib
    import html
    import re
    from IPython.display import HTML, display

    def tokens(s: str) -> list[str]:  # words for English, single characters for Chinese
        return re.findall(r"\[[A-Z]+\]|[A-Za-z0-9À-ÿ'’-]+|\s+|.", s)

    a, b = tokens(before), tokens(after)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        old, new = html.escape("".join(a[i1:i2])), html.escape("".join(b[j1:j2]))
        if op == "equal":
            out.append(old)
        else:
            if old:
                out.append(f'<del style="background:#fbe3e3;color:#a12a2a">{old}</del>')
            if new:
                out.append(f'<ins style="background:#dff3e8;color:#11663f;text-decoration:none">{new}</ins>')
    display(HTML(f'<div style="line-height:1.6;max-width:60em">{"".join(out)}</div>'))


def plot_confusion(rows, cols, labels: list, row_title: str, col_title: str, title: str):
    """Confusion matrix as a heatmap: counts in every cell, agreement on the outlined diagonal."""
    import pandas as pd
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Rectangle

    m = pd.crosstab(pd.Series(rows, name=row_title), pd.Series(cols, name=col_title))
    m = m.reindex(index=labels, columns=labels, fill_value=0)
    cmap = LinearSegmentedColormap.from_list("blues", ["#f4f8fd", "#86b6ef", "#2a78d6", "#104281"])
    fig, ax = plt.subplots(figsize=(1.3 * len(labels) + 2.2, 1.1 * len(labels) + 1.4))
    ax.imshow(m.values, cmap=cmap, vmin=0, vmax=max(m.values.max(), 1))
    for i in range(len(labels)):
        for j in range(len(labels)):
            v = m.values[i, j]
            ax.text(j, i, str(v), ha="center", va="center", fontsize=13, fontweight="bold" if i == j else "normal",
                    color="white" if v > 0.55 * m.values.max() else "#0b0b0b")
        ax.add_patch(Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False, edgecolor="#0b0b0b", linewidth=1.5))
    ax.set_xticks(range(len(labels)), labels); ax.set_yticks(range(len(labels)), labels)
    ax.xaxis.set_label_position("top"); ax.xaxis.tick_top()
    ax.set_xlabel(col_title); ax.set_ylabel(row_title)
    ax.grid(False); ax.tick_params(length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_title(title, pad=12)
    plt.show()
    return m


def plot_heatmap(table, title: str, xlabel: str = "", ylabel: str = "", fmt: str = "{:.0f}", figsize=None):
    """Heatmap of a table (rows x columns) with the value written in each cell."""
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap

    v = np.asarray(table.values, dtype=float)
    cmap = LinearSegmentedColormap.from_list("blues", ["#f4f8fd", "#86b6ef", "#2a78d6", "#104281"])
    fig, ax = plt.subplots(figsize=figsize or (1.1 * v.shape[1] + 3.5, 0.55 * v.shape[0] + 1.6))
    ax.imshow(v, cmap=cmap, aspect="auto", vmin=0, vmax=max(np.nanmax(v), 1e-9))
    for i in range(v.shape[0]):
        for j in range(v.shape[1]):
            ax.text(j, i, fmt.format(v[i, j]), ha="center", va="center", fontsize=9,
                    color="white" if v[i, j] > 0.55 * np.nanmax(v) else "#0b0b0b")
    ax.set_xticks(range(v.shape[1]), [str(c) for c in table.columns], rotation=30, ha="right")
    ax.set_yticks(range(v.shape[0]), [str(r) for r in table.index])
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.grid(False); ax.tick_params(length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_title(title, pad=10)
    plt.show()
