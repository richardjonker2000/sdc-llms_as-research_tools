"""Bibliometrics helpers for notebook 04: citation networks, clustering, search and an interactive map."""
from __future__ import annotations

import html
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import requests

from .llm import CACHE_DIR, CFG, EMBED_MODELS, ROOT, SetupError, _key, embed
from .style import COLORS, GREY

DATA = ROOT / "data" / "openalex"
TOPICS = ["ai_labour", "green_innovation", "china_innovation"]
STOP = set("""a an the and or of in on for to with by from as at is are was were be been being this that these
those we our it its their they which using use used based study studies paper article research results result
show shows find finds findings evidence analysis analyze analyse effect effects impact impacts model models data
new also can may more than between among into how what while such not has have had both however through over
across well within under one two three first most other however thus therefore further two ii iii""".split())


# ---------------------------------------------------------------- data
def load_topic(name: str) -> pd.DataFrame:
    """Load one prepared OpenAlex sample (see data/README.md)."""
    df = pd.read_csv(DATA / f"{name}.csv", dtype=str).fillna("")
    return _tidy(df)


def _tidy(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["cited_by_count"] = pd.to_numeric(df["cited_by_count"], errors="coerce").fillna(0).astype(int)
    df["refs"] = df["references"].str.split()
    first = lambda a, t: (a.split(";")[0].split() or [" ".join(t.split()[:2]) or "?"])[-1] if a.strip() else " ".join(t.split()[:2])  # noqa: E731
    df["short"] = [f"{first(a, t)} {y if pd.notna(y) else ''}".strip() for a, t, y in zip(df["authors"], df["title"], df["year"])]
    return df.reset_index(drop=True)


def abstract_from_index(inv: dict | None) -> str:
    """OpenAlex stores abstracts as {word: [positions]}; rebuild the text."""
    if not inv:
        return ""
    return " ".join(w for _, w in sorted((p, w) for w, ps in inv.items() for p in ps))


def flatten(w: dict) -> dict:
    """One OpenAlex work (JSON) -> one flat row."""
    short = lambda x: x.rsplit("/", 1)[-1] if x else ""  # noqa: E731
    auths = w.get("authorships") or []
    insts = [i for a in auths for i in a.get("institutions", [])]
    topic = w.get("primary_topic") or {}
    return {
        "id": short(w["id"]), "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
        "title": w.get("title") or "", "year": w.get("publication_year"), "type": w.get("type"),
        "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name", ""),
        "cited_by_count": w.get("cited_by_count", 0),
        "authors": "; ".join(a["author"]["display_name"] for a in auths if a.get("author")),
        "institutions": "; ".join(dict.fromkeys(i["display_name"] for i in insts if i.get("display_name"))),
        "countries": "; ".join(dict.fromkeys(i["country_code"] for i in insts if i.get("country_code"))),
        "topic": topic.get("display_name", ""), "subfield": (topic.get("subfield") or {}).get("display_name", ""),
        "field": (topic.get("field") or {}).get("display_name", ""),
        "abstract": abstract_from_index(w.get("abstract_inverted_index")),
        "references": " ".join(short(r) for r in w.get("referenced_works") or []),
    }


FIELDS = ("id,doi,title,publication_year,type,cited_by_count,primary_location,authorships,"
          "primary_topic,abstract_inverted_index,referenced_works")


def _get(params: dict) -> dict:
    for wait in (2, 10, 30, None):
        r = requests.get("https://api.openalex.org/works", params={**params, "api_key": CFG.get("openalex_key", "")},
                         timeout=60)
        if r.ok:
            return r.json()
        if wait is None or r.status_code == 400:   # never show the URL: it contains the API key
            msg = r.json().get("message", "") if r.headers.get("content-type", "").startswith("application/json") else ""
            raise RuntimeError(f"OpenAlex error {r.status_code}: {(msg or r.reason)[:200]}".strip())
        __import__("time").sleep(wait)


def _pages(params: dict, limit: int) -> list[dict]:
    out, page = [], 1
    while len(out) < limit:
        res = _get({**params, "select": FIELDS, "per-page": 200, "page": page})["results"]
        out += res
        if len(res) < 200:
            break
        page += 1
    return out[:limit]


PERIODS = [("before 2010", "publication_year:<2010"), ("2010-2017", "publication_year:2010-2017"),
           ("2018 onwards", "publication_year:>2017")]


SOCIAL_SCIENCES = "primary_topic.domain.id:2"   # OpenAlex domain 2: economics, business, management, psychology, social sciences


def harvest(query: str, seed_doi: str | None = None, n_citing: int = 400, n_per_period: int = 200,
            n_classics: int = 150, domain: str | None = None) -> pd.DataFrame:
    """Build a topic sample from OpenAlex in four steps (see notebook 04, "How this sample is built"):

    1. seed: `seed_doi`, or the most-cited paper among the 100 most relevant matches for the query;
    2. forward: the seed's references, plus the `n_citing` most-cited papers that cite the seed;
    3. topic search, balanced by period: the `n_per_period` most relevant journal articles (cited 5+ times)
       before 2010, in 2010-2017 and from 2018, so older work is not crowded out by the recent boom;
    4. backward: the `n_classics` works most often cited by everything above (at least 5 times) that are
       not yet in the sample: the classics the field builds on.
    The query is matched against titles and abstracts only (full-text matching drags in off-topic papers).
    `domain` (e.g. SOCIAL_SCIENCES) restricts the search steps to one OpenAlex domain, which keeps out
    engineering, medical and computer-science papers that happen to use the same words.
    """
    dom = f",{domain}" if domain else ""
    q = clean_query(query)
    if seed_doi:
        seed = _get({"filter": f"doi:{seed_doi.replace('https://doi.org/', '')}", "select": FIELDS})["results"][0]
    else:
        top = _pages({"filter": f"title_and_abstract.search:{q},type:article{dom}"}, 100)
        seed = max(top, key=lambda w: w.get("cited_by_count", 0))
    short = lambda w: w["id"].rsplit("/", 1)[-1]  # noqa: E731
    found = {short(seed): (seed, {"seed"})}
    add = lambda works, how: [found.setdefault(short(w), (w, set()))[1].add(how) for w in works]  # noqa: E731

    def by_ids(ids):
        return [w for i in range(0, len(ids), 50) for w in _pages({"filter": "openalex:" + "|".join(ids[i:i + 50])}, 50)]

    add(by_ids([r.rsplit("/", 1)[-1] for r in seed.get("referenced_works") or []]), "reference of seed")
    add(_pages({"filter": f"cites:{short(seed)}{dom}", "sort": "cited_by_count:desc"}, n_citing), "cites seed")
    spare = 0
    for i, (label, years) in enumerate(PERIODS):
        want = n_per_period + (spare if i == len(PERIODS) - 1 else 0)   # young fields: unused older quota moves to recent
        hits = _pages({"filter": f"title_and_abstract.search:{q},{years},type:article,cited_by_count:>4{dom}"}, want)
        add(hits, f"topic search {label}")
        spare += max(0, n_per_period - len(hits)) if i < len(PERIODS) - 1 else 0
    cited = Counter(r.rsplit("/", 1)[-1] for w, _ in found.values() for r in w.get("referenced_works") or [])
    classics = [r for r, c in cited.most_common() if r not in found and c >= 5][:n_classics]
    add(by_ids(classics), "classic cited by the sample")
    return pd.DataFrame([flatten(w) | {"found_via": "; ".join(sorted(how))} for w, how in found.values()])


def sample_overview(df: pd.DataFrame) -> pd.DataFrame:
    """How the sample was built: papers per route (rows) and period (columns)."""
    x = df.assign(route=df["found_via"].str.split("; ")).explode("route")
    period = pd.cut(x["year"].astype(float), [0, 1999, 2009, 2017, 2100], labels=["before 2000", "2000-2009", "2010-2017", "2018+"])
    return pd.crosstab(x["route"], period, margins=True, margins_name="total")


def topic_sample(query: str, seed_doi: str | None = None, fallback: str = "ai_labour",
                 domain: str | None = SOCIAL_SCIENCES) -> pd.DataFrame:
    """Your own research topic as a sample: fetched from OpenAlex once, then saved in data/openalex/."""
    name = "my_" + slug(query)[:40] + "_" + _key(query, seed_doi, domain)[:8]
    path = DATA / f"{name}.csv"
    if path.exists():
        print(f"loaded your saved sample {path.name}")
        return load_topic(name)
    if CFG["dry_run"] or not CFG.get("openalex_key"):
        print(f"Can't fetch '{query}' (dry-run mode, or no OPENALEX_API_KEY in config.env): "
              f"using the prepared '{fallback}' sample instead.")
        return load_topic(fallback)
    print(f"fetching '{query}' from OpenAlex (about 30 seconds)...")
    df = harvest(query, seed_doi, domain=domain)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"saved {len(df)} papers to data/openalex/{path.name}")
    return load_topic(name)


def fetch_works(dois: list[str]) -> pd.DataFrame:
    """Fetch specific papers by DOI (e.g. your own) from OpenAlex; they are marked found_via = "mine"."""
    if CFG["dry_run"] or not CFG.get("openalex_key"):
        print("Skipping MY_PAPERS: fetching papers needs internet, OPENALEX_API_KEY in config.env, and DRY_RUN=0.")
        return pd.DataFrame(columns=["id"])
    rows = []
    for doi in dois:
        doi = doi.strip().replace("https://doi.org/", "")
        res = _get({"filter": f"doi:{doi}", "select": FIELDS})["results"]
        if res:
            rows.append(flatten(res[0]) | {"found_via": "mine"})
        else:
            print(f"not found in OpenAlex: {doi}")
    return _tidy(pd.DataFrame(rows).astype(str)) if rows else pd.DataFrame()


def fetch_ids(ids: list[str], cache: Path) -> pd.DataFrame:
    """Metadata for OpenAlex IDs (e.g. frequently cited references), cached in a CSV so it is fetched once."""
    have = pd.read_csv(cache, dtype=str).fillna("") if cache.exists() else pd.DataFrame(columns=["id"])
    missing = [i for i in ids if i not in set(have["id"])]
    if missing and not CFG["dry_run"] and CFG.get("openalex_key"):
        rows = [flatten(w) for j in range(0, len(missing), 50)
                for w in _pages({"filter": "openalex:" + "|".join(missing[j:j + 50])}, 50)]
        have = pd.concat([have, pd.DataFrame(rows).astype(str)], ignore_index=True)
        have.to_csv(cache, index=False, encoding="utf-8")
    return have[have["id"].isin(ids)]


# ---------------------------------------------------------------- citation network
def coupling_graph(df: pd.DataFrame, min_shared: int = 2, max_share: float = 0.2) -> nx.Graph:
    """Bibliographic coupling: two papers are linked when they cite the same works.

    Edge weight = shared references / sqrt(refs_a x refs_b) (Salton's cosine). References cited by more
    than `max_share` of all papers (e.g. the seed paper itself) link everything and are ignored.
    """
    cited_by = defaultdict(list)
    for pid, refs in zip(df["id"], df["refs"]):
        for r in set(refs):
            cited_by[r].append(pid)
    shared = Counter()
    for papers in cited_by.values():
        if 1 < len(papers) <= max_share * len(df):
            for i, a in enumerate(papers):
                for b in papers[i + 1:]:
                    shared[(a, b)] += 1
    nref = dict(zip(df["id"], df["refs"].str.len()))
    G = nx.Graph()
    G.add_nodes_from(df["id"])
    G.add_edges_from((a, b, {"shared": s, "weight": s / math.sqrt(nref[a] * nref[b])})
                     for (a, b), s in shared.items() if s >= min_shared)
    return G


def find_clusters(G: nx.Graph, max_clusters: int = 7, resolution: float = 1.0, seed: int = 1,
                  min_size: int = 15, runs: int = 20, return_stability: bool = False):
    """Research streams by consensus Louvain clustering on the largest connected part of the network.

    Louvain gives somewhat different answers with different random seeds, so we run it `runs` times, keep
    links whose two papers land together in at least half the runs, and cluster that consensus network.
    Returns {paper id: cluster}: 1..max_clusters by size, 0 = small leftover groups ("Other"), -1 = not connected.
    With return_stability=True also returns {paper id: share of runs it sits with its own stream} and the
    average agreement between single runs (adjusted Rand index; 1 = identical every time).
    """
    core = G.subgraph(max(nx.connected_components(G), key=len))
    nodes = list(core)
    idx = {n: i for i, n in enumerate(nodes)}
    R = []
    for s in range(seed, seed + runs):
        comms = nx.community.louvain_communities(core, weight="weight", resolution=resolution, seed=s)
        lab = np.empty(len(nodes), dtype=int)
        for k, c in enumerate(comms):
            lab[[idx[n] for n in c]] = k
        R.append(lab)
    C = nx.Graph()
    C.add_nodes_from(nodes)
    for a, b, d in core.edges(data=True):
        share = float(np.mean([r[idx[a]] == r[idx[b]] for r in R]))
        if share >= 0.5:
            C.add_edge(a, b, weight=share * d["weight"])
    comms = sorted(nx.community.louvain_communities(C, weight="weight", resolution=resolution, seed=seed),
                   key=len, reverse=True)
    label = {n: -1 for n in G}
    for k, c in enumerate(comms):
        label.update({n: (k + 1 if k < max_clusters and len(c) >= min_size else 0) for n in c})
    if not return_stability:
        return label
    stability = {}
    for c in comms:
        members = np.array([idx[n] for n in c])
        frac = np.zeros(len(members))
        for r in R:  # in each run: what share of my stream-mates ended up in the same group as me?
            lab, counts = np.unique(r[members], return_counts=True)
            count_of = dict(zip(lab, counts))
            frac += np.array([count_of[x] for x in r[members]]) / len(members)
        stability.update(dict(zip([nodes[i] for i in members], frac / len(R))))
    pairs = [(a, b) for i, a in enumerate(R) for b in R[i + 1:]][:45]
    return label, stability, float(np.mean([adjusted_rand(a, b) for a, b in pairs]))


def adjusted_rand(a, b) -> float:
    """Agreement between two clusterings of the same papers (1 = identical, 0 = no better than chance)."""
    comb = lambda x: x * (x - 1) / 2  # noqa: E731
    n = len(a)
    s = sum(comb(v) for v in Counter(zip(a, b)).values())
    sa, sb = sum(comb(v) for v in Counter(a).values()), sum(comb(v) for v in Counter(b).values())
    exp = sa * sb / comb(n)
    return (s - exp) / (0.5 * (sa + sb) - exp) if 0.5 * (sa + sb) != exp else 1.0


def layout(G: nx.Graph, nodes: list, seed: int = 1, per_node: int = 6) -> dict:
    """Force-directed positions (ForceAtlas2) so that strongly coupled papers end up close together.

    Uses only each paper's `per_node` strongest links: with all links, every paper pulls on every other
    and the map becomes one ball (the clustering itself still uses all links).
    """
    H = nx.Graph([(a, b, G[a][b]) for a, b in strongest_edges(G, nodes, per_node)])
    H.add_nodes_from(nodes)
    with np.errstate(divide="ignore", invalid="ignore"):  # harmless 0/0 for papers at the same spot
        return nx.forceatlas2_layout(H, weight="weight", seed=seed, max_iter=300)


def strongest_edges(G: nx.Graph, nodes: list, per_node: int = 3) -> list[tuple]:
    """Keep each paper's few strongest links: enough to see structure without a hairball."""
    keep, nodes = set(), set(nodes)
    for n in nodes:
        nb = sorted(((d["weight"], m) for m, d in G[n].items() if m in nodes), reverse=True)[:per_node]
        keep.update(tuple(sorted((n, m))) for _, m in nb)
    return list(keep)


def cluster_color(k: int) -> str:
    return COLORS[(k - 1) % len(COLORS)] if k > 0 else GREY


def most_cited_by_sample(df: pd.DataFrame, ids, n: int = 10) -> list:
    """IDs of the n papers among `ids` that the sample itself cites most often (the field's foundations on the map)."""
    cited = Counter(r for refs in df["refs"] for r in set(refs))
    ids = set(ids)
    return [pid for pid, _ in sorted(((p, cited[p]) for p in ids if cited[p] > 0), key=lambda t: -t[1])[:n]]


def draw_map(df: pd.DataFrame, G: nx.Graph, pos: dict, names: dict, title: str, highlight: list | None = None,
             closest: list | None = None, foundations: list | None = None, question: str | None = None):
    """Static map: one dot per paper, colour = cluster, size = citations.

    highlight:   papers to ring (the seed or your own papers)
    closest:     papers closest to your question, best first (thick black outline)
    foundations: the field's foundational papers (diamond, labelled); replaces the most-cited-per-stream labels
    question:    a label for your question, drawn as a star in the middle of its 10 closest papers
    """
    d = df[df["id"].isin(pos)]
    fig, ax = plt.subplots(figsize=(10, 7.5))
    for a, b in strongest_edges(G, list(pos), 2):
        ax.plot(*zip(pos[a], pos[b]), color="#d9d8d3", lw=0.4, zorder=1)
    ax.scatter([pos[i][0] for i in d["id"]], [pos[i][1] for i in d["id"]], s=8 + 3 * np.sqrt(d["cited_by_count"]),
               c=[cluster_color(k) for k in d["cluster"]], edgecolors="#fcfcfb", linewidths=0.4, zorder=2)
    INK = "#0b0b0b"
    extra = []
    close_in = [p for p in closest or [] if p in pos]
    if close_in:
        c = d.set_index("id").loc[close_in]
        ax.scatter([pos[i][0] for i in close_in], [pos[i][1] for i in close_in], s=8 + 3 * np.sqrt(c["cited_by_count"]),
                   c=[cluster_color(k) for k in c["cluster"]], edgecolors=INK, linewidths=1.6, zorder=4)
        extra.append(plt.Line2D([], [], marker="o", ls="", mfc="white", mec=INK, mew=1.6, label=f"closest to your question ({len(close_in)})"))
    found_in = [p for p in foundations or [] if p in pos]
    if found_in:
        ax.scatter([pos[i][0] for i in found_in], [pos[i][1] for i in found_in], s=90, marker="D",
                   facecolors="none", edgecolors=INK, linewidths=1.2, zorder=5)
        short = d.set_index("id")["short"]
        for pid in found_in:
            ax.annotate(short[pid], pos[pid], fontsize=8, xytext=(5, 5), textcoords="offset points", zorder=6)
        extra.append(plt.Line2D([], [], marker="D", ls="", mfc="none", mec=INK, mew=1.2, label="foundational (most cited by the field)"))
    else:
        for k, g in d[d["cluster"] > 0].groupby("cluster"):
            top = g.nlargest(1, "cited_by_count").iloc[0]
            ax.annotate(top["short"], pos[top["id"]], fontsize=8, xytext=(4, 4), textcoords="offset points", zorder=3)
    for pid in highlight or []:
        if pid in pos:
            ax.scatter(*pos[pid], s=220, facecolors="none", edgecolors=INK, linewidths=1.5, zorder=4)
    if highlight and any(p in pos for p in highlight):
        extra.append(plt.Line2D([], [], marker="o", ls="", mfc="none", mec=INK, mew=1.5, ms=13, label="seed / your papers"))
    if question and close_in:
        P = np.array([pos[i] for i in close_in[:10]])           # the most central of the 10 closest papers (an average
        q = P[np.argmin(((P[:, None] - P[None]) ** 2).sum(-1).sum(1))]   # could land in empty space between streams)
        ax.scatter(*q, s=420, marker="*", color=INK, edgecolors="#fcfcfb", linewidths=1.2, zorder=7)
        ax.annotate(question, q, fontsize=10, fontweight="bold", xytext=(10, -4), textcoords="offset points", zorder=7,
                    bbox=dict(boxstyle="round,pad=0.25", fc="#fcfcfb", ec="none", alpha=0.85))
        extra.append(plt.Line2D([], [], marker="*", ls="", color=INK, ms=14, label="your question (at the centre of its 10 closest papers)"))
    handles = [plt.Line2D([], [], marker="o", ls="", color=cluster_color(k), label=f"{names.get(k, f'Cluster {k}')} ({n})")
               for k, n in d["cluster"].value_counts().sort_index().items() if k > 0]
    if extra:
        handles += [plt.Line2D([], [], ls="", label=" ")] + extra
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1, 1), frameon=False, fontsize=9)
    ax.set_title(title); ax.set_axis_off()
    plt.show()


# ---------------------------------------------------------------- text: clustering and search
def _words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z][a-z\-]{2,}", text.lower()) if w not in STOP]


def text_clusters(texts: list[str], k: int, seed: int = 1, n_init: int = 5) -> tuple[np.ndarray, list[str]]:
    """Group papers by the words they use: TF-IDF vectors + spherical k-means (no citations involved)."""
    docs = [_words(t) for t in texts]
    dfreq = Counter(w for d in docs for w in set(d))
    n = len(docs)
    vocab = sorted(w for w, c in dfreq.items() if 3 <= c <= 0.4 * n)
    idx = {w: i for i, w in enumerate(vocab)}
    X = np.zeros((n, len(vocab)), dtype=np.float32)
    for r, d in enumerate(docs):
        for w, c in Counter(d).items():
            if w in idx:
                X[r, idx[w]] = 1 + math.log(c)
    X *= np.log(n / np.array([dfreq[w] for w in vocab], dtype=np.float32))
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    rng, best = np.random.default_rng(seed), None
    for _ in range(n_init):
        C = X[rng.choice(n, k, replace=False)]
        for _ in range(60):
            lab = (X @ C.T).argmax(1)
            new = np.stack([X[lab == j].sum(0) if (lab == j).any() else C[j] for j in range(k)])
            new /= np.linalg.norm(new, axis=1, keepdims=True) + 1e-9
            if np.allclose(new, C):
                break
            C = new
        score = (X @ C.T).max(1).sum()
        if best is None or score > best[0]:
            best = (score, lab, C)
    _, lab, C = best
    return lab + 1, [", ".join(vocab[i] for i in np.argsort(-C[j])[:6]) for j in range(k)]


def search(df: pd.DataFrame, query: str, k: int = 8) -> pd.DataFrame:
    """Keyword search over titles and abstracts (BM25, the classic search-engine ranking)."""
    docs = [_words(t + " " + a) for t, a in zip(df["title"], df["abstract"])]
    N, avgdl = len(docs), sum(map(len, docs)) / len(docs)
    dfreq = Counter(w for d in docs for w in set(d))
    q = _words(query)
    scores = []
    for d in docs:
        tf, s = Counter(d), 0.0
        for w in q:
            if w in tf:
                idf = math.log(1 + (N - dfreq[w] + 0.5) / (dfreq[w] + 0.5))
                s += idf * tf[w] * 2.2 / (tf[w] + 1.2 * (0.25 + 0.75 * len(d) / avgdl))
        scores.append(s)
    return df.assign(score=scores).nlargest(k, "score")


# ---------------------------------------------------------------- interactive HTML map
def export_html(df: pd.DataFrame, G: nx.Graph, pos: dict, names: dict, path: Path, title: str,
                highlight: list | None = None) -> Path:
    """Write a self-contained interactive map (no internet needed): hover, click, search, filter by cluster."""
    d = df[df["id"].isin(pos)].reset_index(drop=True)
    xs, ys = np.array([pos[i][0] for i in d["id"]]), np.array([pos[i][1] for i in d["id"]])
    span = max(np.ptp(xs), np.ptp(ys)) or 1                       # one scale for both axes: the layout keeps its shape
    sx = lambda v, lo, hi: 500 + 920 * (v - (lo + hi) / 2) / span  # noqa: E731
    index = {pid: i for i, pid in enumerate(d["id"])}
    nodes = [{"x": round(float(sx(x, xs.min(), xs.max())), 1), "y": round(float(sx(y, ys.min(), ys.max())), 1),
              "r": round(min(4 + 0.4 * math.sqrt(c), 20), 1), "c": int(k), "t": t, "a": a.split(";")[0] + (" et al." if ";" in a else ""),
              "y0": int(yr) if pd.notna(yr) else "", "v": v, "n": int(c), "doi": doi, "m": int("mine" in fv or pid in (highlight or []))}
             for pid, x, y, k, t, a, yr, v, c, doi, fv in zip(d["id"], xs, ys, d["cluster"], d["title"], d["authors"], d["year"],
                                                                d["venue"], d["cited_by_count"], d["doi"], d["found_via"])]
    edges = [[index[a], index[b]] for a, b in strongest_edges(G, list(d["id"]), 2)]
    legend = [{"c": int(k), "name": names.get(int(k), f"Cluster {k}") if k > 0 else ("Other" if k == 0 else "Not linked"),
               "col": cluster_color(int(k)), "n": int(n)} for k, n in d["cluster"].value_counts().sort_index(ascending=False).items()]
    legend.sort(key=lambda e: (e["c"] <= 0, e["c"]))
    page = (_HTML.replace("__TITLE__", html.escape(title))
            .replace("__DATA__", json.dumps({"nodes": nodes, "edges": edges, "legend": legend}, ensure_ascii=False)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding="utf-8")
    return path


_HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>
:root{--bg:#fcfcfb;--ink:#0b0b0b;--muted:#52514e;--line:#e6e5e0;--panel:#ffffff}
@media (prefers-color-scheme:dark){:root{--bg:#1a1a19;--ink:#f0efec;--muted:#c3c2b7;--line:#383835;--panel:#232322}}
*{box-sizing:border-box}body{margin:0;font:14px/1.45 system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--ink)}
header{padding:14px 16px 6px}h1{font-size:18px;margin:0 0 4px}header p{margin:0;color:var(--muted)}
.wrap{display:flex;gap:12px;padding:8px 16px 16px;flex-wrap:wrap}
#map{flex:1 1 560px;min-height:420px;height:72vh;border:1px solid var(--line);border-radius:8px;background:var(--panel);touch-action:none;cursor:grab}
aside{flex:0 1 300px;display:flex;flex-direction:column;gap:10px}
input{width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--panel);color:var(--ink);font:inherit}
.leg{border:1px solid var(--line);border-radius:8px;padding:8px;background:var(--panel)}
.leg button{display:flex;align-items:center;gap:8px;width:100%;border:0;background:none;color:var(--ink);font:inherit;text-align:left;padding:4px;border-radius:4px;cursor:pointer}
.leg button:hover{background:var(--line)}.leg button.off{opacity:.35}.dot{width:12px;height:12px;border-radius:50%;flex:none}
#info{border:1px solid var(--line);border-radius:8px;padding:10px;background:var(--panel);min-height:120px}
#info h2{font-size:14px;margin:0 0 6px}#info p{margin:2px 0;color:var(--muted)}#info a{color:#2a78d6}
#tip{position:fixed;pointer-events:none;background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:6px 8px;max-width:320px;font-size:12px;display:none;box-shadow:0 2px 8px #0002}
circle{stroke:var(--panel);stroke-width:1;vector-effect:non-scaling-stroke;cursor:pointer}circle.dim{opacity:.12}circle.hit{stroke:var(--ink);stroke-width:2.5}circle.sel{stroke:var(--ink);stroke-width:3}line{stroke:var(--line);stroke-width:1;vector-effect:non-scaling-stroke}
</style></head><body><header><h1>__TITLE__</h1><p>Each dot is a paper; papers that cite the same works sit close together. Colour = research stream, size = citations.
Hover for details, click a dot to see the paper, scroll to zoom, drag to pan, double-click to reset.</p></header>
<div class="wrap"><svg id="map" viewBox="0 0 1000 1000"><g id="g"></g></svg><aside>
<input id="q" placeholder="Search titles (e.g. spillover, China)…" aria-label="Search titles"><div class="leg" id="leg"></div>
<div id="info"><p>Click a paper to see its details.</p></div></aside></div><div id="tip"></div>
<script>
const D=__DATA__,ns="http://www.w3.org/2000/svg",g=document.getElementById("g"),svg=document.getElementById("map");
const col={};D.legend.forEach(l=>col[l.c]=l.col);const off=new Set();
D.edges.forEach(([a,b])=>{const l=document.createElementNS(ns,"line"),A=D.nodes[a],B=D.nodes[b];
 l.setAttribute("x1",A.x);l.setAttribute("y1",A.y);l.setAttribute("x2",B.x);l.setAttribute("y2",B.y);g.appendChild(l)});
const tip=document.getElementById("tip"),info=document.getElementById("info");
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const circles=D.nodes.map((n,i)=>{const c=document.createElementNS(ns,"circle");c.setAttribute("cx",n.x);c.setAttribute("cy",n.y);
 c.setAttribute("r",n.m?n.r+4:n.r);c.setAttribute("fill",col[n.c]);if(n.m)c.classList.add("hit");
 c.onmousemove=e=>{tip.style.display="block";tip.style.left=(e.clientX+12)+"px";tip.style.top=(e.clientY+12)+"px";
  tip.innerHTML="<b>"+esc(n.t)+"</b><br>"+esc(n.a)+" ("+n.y0+") · "+n.n+" citations"};
 c.onmouseleave=()=>tip.style.display="none";
 c.onclick=()=>{circles.forEach(x=>x.classList.remove("sel"));c.classList.add("sel");const L=D.legend.find(l=>l.c===n.c);info.innerHTML="<h2>"+esc(n.t)+"</h2><p>"+esc(n.a)+", "+n.y0+"</p><p>"+esc(n.v)+"</p><p>"+n.n+
  " citations · "+esc(L?L.name:"")+"</p>"+(n.doi?"<p><a target=_blank rel=noopener href='https://doi.org/"+esc(n.doi)+"'>Open DOI</a></p>":"")};
 g.appendChild(c);return c});
const leg=document.getElementById("leg");D.legend.forEach(l=>{const b=document.createElement("button");
 b.innerHTML="<span class=dot style='background:"+l.col+"'></span><span>"+esc(l.name)+" <small>("+l.n+")</small></span>";
 b.onclick=()=>{off.has(l.c)?off.delete(l.c):off.add(l.c);b.classList.toggle("off");paint()};leg.appendChild(b)});
const q=document.getElementById("q");q.oninput=paint;
function paint(){const s=q.value.trim().toLowerCase();D.nodes.forEach((n,i)=>{const c=circles[i];
 c.classList.toggle("dim",off.has(n.c)||(s&&!n.t.toLowerCase().includes(s)));c.classList.toggle("hit",!!n.m||(!!s&&n.t.toLowerCase().includes(s)))})}
let vb=[0,0,1000,1000],drag=null,moved=false;const setVB=()=>svg.setAttribute("viewBox",vb.join(" "));
function fit(){const r=svg.getBoundingClientRect(),a=(r.width||1)/(r.height||1);
 vb=a>1?[500-500*a,0,1000*a,1000]:[0,500-500/a,1000,1000/a];setVB()}
fit();addEventListener("resize",fit);svg.ondblclick=fit;
svg.addEventListener("wheel",e=>{e.preventDefault();const f=e.deltaY>0?1.15:1/1.15,r=svg.getBoundingClientRect(),
 mx=vb[0]+vb[2]*(e.clientX-r.left)/r.width,my=vb[1]+vb[3]*(e.clientY-r.top)/r.height;
 vb=[mx-(mx-vb[0])*f,my-(my-vb[1])*f,vb[2]*f,vb[3]*f];setVB()},{passive:false});
svg.onpointerdown=e=>{drag=[e.clientX,e.clientY];moved=false};
svg.onpointermove=e=>{if(!drag)return;
 if(!moved){if(Math.hypot(e.clientX-drag[0],e.clientY-drag[1])<4)return;moved=true;svg.setPointerCapture(e.pointerId);tip.style.display="none"}
 const r=svg.getBoundingClientRect();vb[0]-=(e.clientX-drag[0])*vb[2]/r.width;
 vb[1]-=(e.clientY-drag[1])*vb[3]/r.height;drag=[e.clientX,e.clientY];setVB()};
svg.onpointerup=svg.onpointercancel=()=>drag=null;
</script></body></html>"""


# ---------------------------------------------------------------- PhD toolkit: reading list, bridges, Zotero export
def reading_list(df: pd.DataFrame, names: dict, n_classic: int = 3, n_rising: int = 3, now: int = 2026) -> pd.DataFrame:
    """Per stream: the classics (most cited ever) and the rising papers (most citations per year, last 5 years)."""
    rows = []
    for k in sorted(c for c in df["cluster"].unique() if c > 0):
        g = df[df["cluster"] == k].copy()
        g["per_year"] = g["cited_by_count"] / (now - g["year"].fillna(now).astype(int) + 1)
        classic = g.nlargest(n_classic, "cited_by_count").assign(role="classic")
        rising = (g[(g["year"] >= now - 5) & ~g["id"].isin(classic["id"])]
                  .nlargest(n_rising, "per_year").assign(role="rising"))
        rows.append(pd.concat([classic, rising]).assign(stream=names.get(k, f"Cluster {k}")))
    out = pd.concat(rows)
    return out[["stream", "role", "short", "title", "year", "venue", "cited_by_count", "doi", "id", "authors", "abstract"]]


def bridges(df: pd.DataFrame, G: nx.Graph, names: dict, n: int = 8) -> pd.DataFrame:
    """Papers that connect two streams: strongly linked to their own stream AND to a second one."""
    cl = dict(zip(df["id"], df["cluster"]))
    rows = []
    for pid in df.loc[df["cluster"] > 0, "id"]:
        w = Counter()
        for other, d in G[pid].items():
            if cl.get(other, -1) > 0:
                w[cl[other]] += d["weight"]
        top = w.most_common(2)
        if len(top) == 2 and top[0][0] == cl[pid]:
            rows.append({"id": pid, "bridge_strength": top[1][1], "from": names.get(cl[pid]), "to": names.get(top[1][0])})
    b = pd.DataFrame(rows).sort_values("bridge_strength", ascending=False)
    b = b[b.groupby(b[["from", "to"]].apply(lambda r: tuple(sorted(map(str, r))), axis=1)).cumcount() < 2].head(n)
    return b.merge(df[["id", "short", "title", "cited_by_count"]], on="id")  # at most 2 per pair of streams


def export_ris(df: pd.DataFrame, path: Path) -> Path:
    """Write a RIS file: File > Import in Zotero, EndNote or Mendeley."""
    lines = []
    for r in df.itertuples():
        lines += ["TY  - JOUR", f"TI  - {r.title}"] + [f"AU  - {a.strip()}" for a in str(r.authors).split(";") if a.strip()]
        lines += [f"PY  - {r.year}", f"JO  - {r.venue}"] + ([f"DO  - {r.doi}"] if r.doi else [])
        lines += ([f"AB  - {r.abstract}"] if r.abstract else []) + [f"KW  - {getattr(r, 'stream', '')}"]
        lines += [f"N1  - {getattr(r, 'role', '')} paper, from the workshop field map", "ER  - ", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path



# ---------------------------------------------------------------- lenses for notebook A4
def lsa_vectors(texts: list[str], dims: int = 100) -> np.ndarray:
    """Word-based meaning vectors (LSA: TF-IDF + SVD). The fallback when AI embeddings are unavailable."""
    docs = [_words(t) for t in texts]
    dfreq = Counter(w for d in docs for w in set(d))
    vocab = sorted(w for w, c in dfreq.items() if 3 <= c <= 0.4 * len(docs))
    idx = {w: i for i, w in enumerate(vocab)}
    X = np.zeros((len(docs), len(vocab)), dtype=np.float32)
    for r, d in enumerate(docs):
        for w, c in Counter(d).items():
            if w in idx:
                X[r, idx[w]] = (1 + math.log(c)) * math.log(len(docs) / dfreq[w])
    U, S, _ = np.linalg.svd(X - X.mean(0), full_matrices=False)
    V = U[:, :dims] * S[:dims]
    return (V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9)).astype(np.float32)


def paper_vectors(df: pd.DataFrame, name: str) -> tuple[np.ndarray, str]:
    """AI embeddings of title + abstract for every paper (cached per topic), or LSA vectors as a fallback."""
    model = EMBED_MODELS.get(CFG["provider"], "none")
    cache = CACHE_DIR / "embeddings" / f"{name}__{model}.npz"
    texts = (df["title"] + ". " + df["abstract"]).tolist()
    have = dict(zip(*np.load(cache, allow_pickle=False).values())) if cache.exists() else {}
    missing = [i for i, pid in enumerate(df["id"]) if pid not in have]
    try:
        if missing:
            new = embed([texts[i] for i in missing])
            have.update({df["id"].iloc[i]: v for i, v in zip(missing, new.astype(np.float16))})
            cache.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(cache, ids=np.array(list(have)), vecs=np.stack(list(have.values())))
        V = np.stack([have[pid] for pid in df["id"]]).astype(np.float32)
        V -= V.mean(0)  # centre: raw embeddings all point roughly the same way, which squashes similarities
        return V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9), f"AI embeddings ({model})"
    except (SetupError, RuntimeError) as e:
        print(f"Using word-based LSA vectors instead of AI embeddings: {e}")
        return lsa_vectors(texts), "LSA (word statistics)"


def similarity_graph(V: np.ndarray, ids: list, k: int = 10) -> nx.Graph:
    """Link each paper to its k most similar papers by meaning (cosine similarity of the vectors)."""
    S = V @ V.T
    np.fill_diagonal(S, -1)
    G = nx.Graph()
    G.add_nodes_from(ids)
    for i, row in enumerate(S):
        for j in np.argpartition(-row, k)[:k]:
            G.add_edge(ids[i], ids[j], weight=float(max(row[j], 0)), shared=0)
    return G


def hidden_connections(df: pd.DataFrame, V: np.ndarray, G_cite: nx.Graph, n: int = 8, min_cites: int = 10,
                       k: int = 10) -> pd.DataFrame:
    """Pairs of papers that are very close in meaning but share no references and sit in different streams.

    Scored with CSLS: similarity minus each paper's average similarity to its k nearest neighbours, so broad
    "impact of AI on everything" papers (close to everything) don't crowd out the specific pairs.
    Only papers with an abstract and at least `min_cites` citations.
    """
    S = V @ V.T
    np.fill_diagonal(S, -1)
    r = np.sort(S, axis=1)[:, -k:].mean(1)                # how "central" each paper is
    score = 2 * S - r[:, None] - r[None, :]
    thin = ((df["abstract"].str.len() < 300) | (df["cited_by_count"] < min_cites)).to_numpy()
    score[thin, :] = score[:, thin] = -9
    cl, ids, rows = df["cluster"].to_numpy(), df["id"].to_numpy(), []
    for i, j in zip(*np.unravel_index(np.argsort(-score, axis=None)[:50000], score.shape)):
        if i < j and cl[i] > 0 and cl[j] > 0 and cl[i] != cl[j] and not G_cite.has_edge(ids[i], ids[j]):
            rows.append({"similarity": round(float(S[i, j]), 3), "paper_a": df["short"].iloc[i], "title_a": df["title"].iloc[i],
                         "stream_a": df["stream"].iloc[i], "paper_b": df["short"].iloc[j], "title_b": df["title"].iloc[j],
                         "stream_b": df["stream"].iloc[j]})
            if len(rows) == n:
                break
    return pd.DataFrame(rows)


def cocitation(df: pd.DataFrame, top: int = 150, min_together: int = 3) -> nx.Graph:
    """Co-citation: two *references* are linked when the same papers cite them together.

    Nodes are the `top` most-cited references of the corpus; weight = association strength
    (times cited together / (cites_a x cites_b)), so very popular works don't dominate.
    """
    counts = Counter(r for refs in df["refs"] for r in set(refs))
    keep = {r for r, _ in counts.most_common(top)}
    pair = Counter()
    for refs in df["refs"]:
        rs = sorted(set(refs) & keep)
        for i, a in enumerate(rs):
            for b in rs[i + 1:]:
                pair[(a, b)] += 1
    G = nx.Graph()
    G.add_nodes_from((r, {"cites": counts[r]}) for r in keep)
    G.add_edges_from((a, b, {"together": c, "weight": c / (counts[a] * counts[b]) * 1000})
                     for (a, b), c in pair.items() if c >= min_together)
    return G


GENERIC = set("""crucial enhancing enhance enhances enhanced promote promotes promoting improve improves improving
improved significant significantly various key role roles novel provide provides providing important importance
potential increasingly increasing increase increases growing comprehensive insights insight valuable explore explores
explored exploring examine examines examined examining investigate investigates investigated highlight highlights
highlighting reveal reveals revealed suggest suggests critical essential effective effectively strategies strategy
approach approaches framework address addressing particularly notably overall current recent future implications
paper's aims aim objective purpose contributes contribute contribution understanding""".split())


def emerging_terms(df: pd.DataFrame, recent=(2023, 2025), base=(2015, 2020), n: int = 15, min_docs: int = 8) -> pd.DataFrame:
    """Words and two-word phrases whose share of papers grew most between a base period and recent years."""
    def terms(text):
        w = [x for x in _words(text) if x not in GENERIC]
        return set(w) | {f"{a} {b}" for a, b in zip(w, w[1:])}
    docs = [(y, terms(t + " " + a)) for y, t, a in zip(df["year"], df["title"], df["abstract"]) if pd.notna(y)]
    old = [d for y, d in docs if base[0] <= y <= base[1]]
    new = [d for y, d in docs if recent[0] <= y <= recent[1]]
    c_old, c_new = Counter(t for d in old for t in d), Counter(t for d in new for t in d)
    rows = [{"term": t, "recent_share": c / len(new), "earlier_share": c_old[t] / max(len(old), 1)}
            for t, c in c_new.items() if c >= min_docs]
    out = pd.DataFrame(rows)
    out["growth"] = (out.recent_share + 0.002) / (out.earlier_share + 0.002)
    return out.nlargest(n, "growth").round(3)


def semantic_search(df: pd.DataFrame, V: np.ndarray, text: str, name: str, k: int = 10) -> pd.DataFrame:
    """Papers closest in *meaning* to a piece of text (e.g. your project description), using AI embeddings."""
    model = EMBED_MODELS.get(CFG["provider"], "none")
    cache = CACHE_DIR / "embeddings" / f"{name}__{model}.npz"
    key = CACHE_DIR / "embeddings" / f"query__{model}__{_key(text)}.npy"
    try:
        if key.exists():                      # saved before: replay (also offline)
            q = np.load(key)
        elif CFG["dry_run"]:
            raise SetupError("dry run: no new embeddings")
        else:
            q = embed([text], kind="query")[0]
            np.save(key, q)
        if q.shape[0] != V.shape[1]:          # e.g. dry run: word-based vectors, so no AI query vector
            raise SetupError("vectors are not AI embeddings")
        raw = np.load(cache)["vecs"].astype(np.float32)
        q = q - (raw / np.linalg.norm(raw, axis=1, keepdims=True)).mean(0)
        sims = V @ (q / np.linalg.norm(q))
        return df.assign(similarity=sims.round(3)).nlargest(k, "similarity")
    except (SetupError, RuntimeError, FileNotFoundError) as e:
        print(f"Semantic search unavailable ({e}); using keyword search instead.")
        return search(df, text, k)


def load_field(name: str, folder: Path = ROOT / "outputs") -> tuple[pd.DataFrame, dict]:
    """The field saved by notebook 04 (papers with their stream), plus {cluster: stream name}."""
    path = folder / f"field_{name}.csv"
    if not path.exists():
        raise SetupError(f"Run notebook 04 with this topic first: it saves outputs/{path.name}.")
    df = pd.read_csv(path, dtype=str).fillna("")
    df = _tidy(df.drop(columns=["short"], errors="ignore"))
    df["cluster"] = pd.to_numeric(df["cluster"], errors="coerce").fillna(-1).astype(int)
    names = df[df["cluster"] > 0].drop_duplicates("cluster").set_index("cluster")["stream"].to_dict()
    return df, names


def foundations(df: pd.DataFrame, name: str, top: int = 150) -> tuple[nx.Graph, pd.DataFrame]:
    """Co-citation network of the `top` most-cited works, with their metadata.

    `cited_by_count` in the returned table is how often THIS corpus cites the work, not its global count.
    """
    CC = cocitation(df, top=top, min_together=3)
    meta = fetch_ids(list(CC), DATA / f"{name}_refs.csv")
    refs = pd.concat([df[df["id"].isin(CC)].drop(columns=["refs", "short", "cluster", "stream", "semantic"], errors="ignore"),
                      meta[~meta["id"].isin(df["id"])]]).drop_duplicates("id").astype(str).fillna("")
    refs = _tidy(refs)
    refs["cited_by_count"] = refs["id"].map(nx.get_node_attributes(CC, "cites")).fillna(0).astype(int)
    return CC.subgraph(refs["id"]).copy(), refs


def foundation_table(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """The classics: works in the sample that the sample itself cites most often."""
    cited = Counter(r for refs in df["refs"] for r in set(refs))
    out = df.assign(cited_by_sample=df["id"].map(cited).fillna(0).astype(int))
    return out.nlargest(n, "cited_by_sample")[["short", "title", "venue", "cited_by_sample", "found_via"]]


# ---------------------------------------------------------------- hybrid streams (notebook 04)
def hybrid_graph(G_cite: nx.Graph, V: np.ndarray, ids: list, k: int = 15, alpha: float = 0.5) -> nx.Graph:
    """Combine citation links (bibliographic coupling) and meaning links (k most similar papers by embedding).

    weight = alpha x coupling (rescaled to 0-1) + (1 - alpha) x semantic similarity. Meaning links also connect
    papers that share no references (often older ones), so every paper can be placed.
    """
    H = nx.Graph()
    H.add_nodes_from(ids)
    top = max((d["weight"] for *_, d in G_cite.edges(data=True)), default=1)
    for a, b, d in G_cite.edges(data=True):
        if a in H and b in H:
            H.add_edge(a, b, weight=alpha * d["weight"] / top, shared=d["shared"])
    for a, b, d in similarity_graph(V, ids, k=k).edges(data=True):
        if H.has_edge(a, b):
            H[a][b]["weight"] += (1 - alpha) * d["weight"]
        else:
            H.add_edge(a, b, weight=(1 - alpha) * d["weight"], shared=0)
    return H


def choose_resolution(G: nx.Graph, options=(0.6, 0.8, 1.0), runs: int = 10) -> tuple[float, pd.DataFrame]:
    """Try several resolutions and pick the most stable one (fewest streams if tied within 0.02)."""
    rows = []
    for res in options:
        lab, _, agree = find_clusters(G, max_clusters=12, resolution=res, runs=runs, return_stability=True)
        rows.append({"resolution": res, "streams (15+ papers)": len({v for v in lab.values() if v > 0}),
                     "agreement between runs": round(agree, 2)})
    table = pd.DataFrame(rows)
    best = table["agreement between runs"].max()
    pick = table[table["agreement between runs"] >= best - 0.02].iloc[0]["resolution"]
    return float(pick), table


def stream_profiles(df: pd.DataFrame, col: str = "cluster", n_terms: int = 8, n_titles: int = 8) -> dict:
    """For each stream: size, median year, its most distinctive words and its most-cited titles."""
    d = df[df[col] > 0]
    docs = {k: Counter(w for t in (g["title"] + " " + g["abstract"]) for w in set(_words(t))) for k, g in d.groupby(col)}
    total = Counter()
    for c in docs.values():
        total.update(c)
    out = {}
    for k, g in d.groupby(col):
        n = len(g)
        score = {w: (c / n) * math.log((c / n) / (total[w] / len(d))) for w, c in docs[k].items() if c >= 5}
        out[k] = {"papers": n, "median_year": int(g["year"].dropna().median()) if g["year"].notna().any() else None,
                  "distinctive_words": [w for w, _ in sorted(score.items(), key=lambda x: -x[1])[:n_terms]],
                  "top_titles": g.nlargest(n_titles, "cited_by_count")["title"].str[:110].tolist()}
    return out


# ---------------------------------------------------------------- from research question to search (notebook 04)
EXAMPLES = {
    "fdi_spillovers": "Does foreign direct investment lead to technology spillovers to domestic firms, and does this "
                      "depend on their absorptive capacity? I'm especially interested in China.",
    "green_subsidies": "Do government subsidies for green innovation lead to more and better environmental patents "
                       "in Chinese firms?",
    "ai_danish_firms": "Do firms that adopt artificial intelligence hire more or fewer workers, and which occupations "
                       "are affected? Evidence from Danish register data.",
}


def clean_query(query: str) -> str:
    """OpenAlex filters break on commas, and title/abstract search has no wildcards: remove both."""
    return query.replace(",", " ").replace("*", "")


def slug(text: str) -> str:
    """A safe file name from a topic or query."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:60] or "topic"


def query_counts(query: str, domain: str | None = SOCIAL_SCIENCES) -> pd.Series:
    """How many relevant articles (cited 5+ times) OpenAlex finds per period: is the query too narrow or too broad?"""
    cache = CACHE_DIR / "openalex_counts.json"
    saved = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
    key = f"{query} | {domain}"
    if key in saved:                       # counted before: replay (also works offline)
        return pd.Series(saved[key], name="articles found")
    if CFG["dry_run"] or not CFG.get("openalex_key"):
        return None  # can't check without internet and an OpenAlex key
    q = clean_query(query)
    out = {}
    for label, years in PERIODS:
        r = _get({"filter": f"title_and_abstract.search:{q},{years},type:article,cited_by_count:>4" + (f",{domain}" if domain else ""),
                  "per-page": 1, "select": "id"})
        out[label] = r["meta"]["count"]
    saved[key] = out
    cache.write_text(json.dumps(saved, ensure_ascii=False, indent=1), encoding="utf-8")
    return pd.Series(out, name="articles found")


def seed_candidates(query: str, n: int = 15, domain: str | None = SOCIAL_SCIENCES) -> pd.DataFrame | None:
    """The n most-cited papers among the 100 most relevant matches: candidates for the seed paper (cached)."""
    cache = CACHE_DIR / "openalex_seeds.json"
    saved = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
    key = f"{query} | {domain}"
    if key not in saved:
        if CFG["dry_run"] or not CFG.get("openalex_key"):
            return None
        top = _pages({"filter": f"title_and_abstract.search:{clean_query(query)},type:article" + (f",{domain}" if domain else "")}, 100)
        top = sorted(top, key=lambda w: -w.get("cited_by_count", 0))[:n]
        saved[key] = [{k: flatten(w)[k] for k in ("id", "doi", "title", "year", "cited_by_count", "abstract")} for w in top]
        cache.write_text(json.dumps(saved, ensure_ascii=False, indent=1), encoding="utf-8")
    return pd.DataFrame(saved[key])


# ---------------------------------------------------------------- plan_search: research question -> tested search (notebook 04)
from dataclasses import dataclass  # noqa: E402

from pydantic import BaseModel, Field  # noqa: E402

from .llm import extract, extract_many  # noqa: E402


class SearchPlan(BaseModel):
    concepts: list[str] = Field(description="The 2 or 3 core concepts of the question")
    query: str = Field(description='An OpenAlex search query: at most 3 concept groups joined with AND; inside a group, '
                                   'synonyms joined with OR; multi-word terms in "double quotes". Example: '
                                   '("industrial robots" OR automation) AND (wages OR earnings OR employment)')
    project: str = Field(description="The question restated as a 2-sentence project description: what is studied, how, where")
    literature_question: str = Field(description="One question to ask the existing literature, useful for this project")


class LitQuestion(BaseModel):
    rewritten: str = Field(description="The question rewritten for a literature search: ONE clear question, spelling "
                                       "fixed, using the terms researchers in this field actually use")
    focus: str = Field(description="The core topic in 3 to 8 words")
    field_terms: list[str] = Field(description="3 to 8 established terms and synonyms the literature uses for this topic")
    setting: list[str] = Field(description="The specific setting of the question that a closely matching paper would "
                                           "share: industry, country, population, policy, technology. Empty if none")
    set_aside: list[str] = Field(description="Parts of the question not used for searching at all (methods, data, "
                                             "secondary sub-questions); empty if none")
    alternatives: list[str] = Field(description="If the question can be read in clearly different ways, 1 or 2 other "
                                                "rewritten questions; otherwise empty")


REWRITE_INSTR = ("A PhD student will map the existing literature around their research question. Rewrite the question so "
                 "it works well for a literature search: keep the student's intent, fix spelling, keep ONE core question, "
                 "and use the established terms of the field rather than everyday wording. The rewritten question should "
                 "name the general phenomenon; list the specific setting (industry, country, population, policy) under "
                 "setting. Methods, data and secondary sub-questions go under set_aside.")


class SeedChoice(BaseModel):
    number: int = Field(description="The number of the paper most central to the research question")
    reason: str = Field(description="One sentence: why this paper is the best anchor for the question")


PLAN_INSTR = ("A PhD student wants to map the literature around their research question. Turn it into a search plan for "
              "OpenAlex, which searches titles and abstracts. The query should find the SURROUNDING FIELD, not only papers "
              "answering this exact question: a few hundred to a few thousand articles. Leave out the country, the data and "
              "the method unless they are the core topic; those details go in the project description.")


@dataclass
class Plan:
    question: str
    query: str | None            # None = use the prepared sample (the wider field: "context" search)
    project: str
    literature_question: str
    seed_doi: str | None = None
    name: str = "ai_labour"
    prepared: str = "ai_labour"


def plan_search(question: str, domain: str | None = SOCIAL_SCIENCES, rounds: int = 4, prepared: str = "ai_labour",
                rewrite: bool = True) -> Plan:
    """From a research question (or just a field) to a tested search plan, step by step:

    0. the LLM rewrites the question for a literature search (one core question, the field's own terms) and says
       what it set aside and how else the question could be read;
    1. the LLM proposes a query, a 2-sentence project description and a question for the literature;
    2. OpenAlex counts the hits per period; too few or too many -> feedback to the LLM, up to `rounds` times;
    3. the LLM picks the seed paper from the 15 most-cited matches, with a reason.
    With an empty question it returns a plan for a prepared sample (works offline).
    """
    if not question:
        print(f"No research question: using the prepared sample '{prepared}'.")
        return Plan("", None, prepared.replace("_", " "), prepared.replace("_", " "), name=prepared, prepared=prepared)
    original, base, setting = question, question, []
    if rewrite:
        rw = extract(question, LitQuestion, REWRITE_INSTR).data
        if rw:
            base = f"{rw.rewritten}\nEstablished terms: {', '.join(rw.field_terms)}"
            setting = rw.setting
            print(f"your question:   {original}\nrewritten:       {rw.rewritten}\nfield terms:     {', '.join(rw.field_terms)}")
            if setting:
                print(f"setting:         {'; '.join(setting)}  (kept in your project description, used to rank papers)")
            if rw.set_aside:
                print(f"set aside:       {'; '.join(rw.set_aside)}  (in the project description, not in the search)")
            for alt in rw.alternatives:
                print(f"or did you mean: {alt}")
            print()
            question = rw.rewritten
    text = base
    for rnd in range(1, rounds + 1):
        plan = extract(text, SearchPlan, PLAN_INSTR).data
        if plan is None:
            raise SetupError("The LLM could not produce a search plan. Rephrase the question and try again.")
        counts = query_counts(plan.query, domain)
        print(f"round {rnd}: {counts.to_dict() if counts is not None else 'not checked (offline)'}\n   {plan.query}")
        if counts is None or (counts["2018 onwards"] >= 150 and counts.sum() <= 30000):
            break
        hint = "too few: fewer AND groups, more synonyms" if counts["2018 onwards"] < 150 else "too many: be more specific"
        text = f"{base}\n\nYour previous query was:\n{plan.query}\nIt found {counts.to_dict()} articles: {hint}."
    project = plan.project if original == question else f"{plan.project} (Original question: {original})"
    out = Plan(original, plan.query, project, plan.literature_question, name=slug(original)[:50], prepared=prepared)
    print(f"\nproject: {out.project}\nquestion for the literature: {out.literature_question}")
    cands = seed_candidates(plan.query, domain=domain)
    if cands is not None:
        listing = "\n".join(f"{i}. {r.title} ({r.year}, {r.cited_by_count} citations). {r.abstract[:300]}" for i, r in cands.iterrows())
        pick = extract(f"RESEARCH QUESTION: {question}\n\nCANDIDATE PAPERS:\n{listing}", SeedChoice,
                       "Choose the paper that is the best anchor for mapping the literature around this research question.").data
        if pick and 0 <= pick.number < len(cands):
            out.seed_doi = cands.doi[pick.number]
            print(f"\nseed paper: {cands.title[pick.number]} ({cands.year[pick.number]}, {cands.cited_by_count[pick.number]} citations)"
                  f"\nwhy: {pick.reason}")
    return out



def is_topical(df: pd.DataFrame) -> pd.Series:
    """Papers that are ABOUT the topic: the seed, papers citing it, search hits and your own papers.

    The seed's references and the classics are the field's foundations: shown separately, not mapped, because
    widely cited methods works (e.g. on thematic analysis or panel econometrics) would form fake "streams".
    """
    routes = df["found_via"].str.split("; ")
    return routes.apply(lambda r: any(x in ("seed", "cites seed", "mine") or x.startswith("topic search") for x in r))


def relevance(df: pd.DataFrame, V: np.ndarray, text: str, name: str) -> np.ndarray:
    """How close each paper is in meaning to a text (your project description): cosine similarity of embeddings,
    or keyword-search scores when embeddings are unavailable."""
    model = EMBED_MODELS.get(CFG["provider"], "none")
    cache = CACHE_DIR / "embeddings" / f"{name}__{model}.npz"
    key = CACHE_DIR / "embeddings" / f"query__{model}__{_key(text)}.npy"
    try:
        if key.exists():                      # saved before: replay (also offline)
            q = np.load(key)
        elif CFG["dry_run"]:
            raise SetupError("dry run: no new embeddings")
        else:
            q = embed([text], kind="query")[0]
            np.save(key, q)
        if q.shape[0] != V.shape[1]:          # e.g. dry run: word-based vectors, so no AI query vector
            raise SetupError("vectors are not AI embeddings")
        raw = np.load(cache)["vecs"].astype(np.float32)
        q = q - (raw / np.linalg.norm(raw, axis=1, keepdims=True)).mean(0)
        return V @ (q / np.linalg.norm(q))
    except (SetupError, RuntimeError, FileNotFoundError):
        return search(df, text, k=len(df)).reindex(df.index)["score"].fillna(0).to_numpy()


# --- Chat with the literature (retrieval-augmented generation, RAG) -----------------------------------------
ASK_SYSTEM = ("You answer questions about a research literature using ONLY the numbered sources given "
              "(titles and abstracts). Cite every claim as [ID] with the source IDs exactly as given. "
              "If the sources do not answer the question, say so plainly instead of guessing. "
              "Note where sources disagree. Be concise: at most 250 words.")


def retrieve(df: pd.DataFrame, V: np.ndarray, question: str, name: str, k: int = 15) -> pd.DataFrame:
    """Raw retrieval: the k papers closest in meaning to the question, with or without an abstract.
    Papers without an abstract are matched on their title only."""
    hits = semantic_search(df, V, question, name, k=len(df))
    if "similarity" not in hits:                       # offline: keyword search was used; keep one column name
        hits = hits.rename(columns={"score": "similarity"})
    return hits.assign(has_abstract=hits.abstract.str.len() >= 100).head(k)


def ask_literature(df: pd.DataFrame, V: np.ndarray, question: str, name: str, k: int = 8,
                   system: str = ASK_SYSTEM) -> tuple[str, pd.DataFrame]:
    """RAG in three steps: (1) retrieve the k closest papers THAT HAVE AN ABSTRACT, (2) give their abstracts
    to the LLM with the question, (3) check that every [ID] it cites was really among the retrieved papers."""
    from .llm import chat
    hits = retrieve(df, V, question, name, k=len(df))                                      # 1. retrieve
    hits = hits[hits.has_abstract].head(k)
    sources = "\n\n".join(f"[{r.id}] {r.title} ({r.year})\n{r.abstract[:1200]}" for r in hits.itertuples())
    answer = chat(f"SOURCES:\n\n{sources}\n\nQUESTION: {question}", system=system)  # 2. generate
    answer = re.sub(r"\[([^\]]*)\]", lambda m: "[" + re.sub(r"\b(\d{8,})\b", r"W\1", m.group(1)) + "]", answer)  # LLMs sometimes drop the W
    cited = ["W" + n for n in re.findall(r"\bW?(\d{6,})\b", answer)]                      # 3. check
    bad = sorted(set(cited) - set(hits.id))
    hits = hits.assign(cited_in_answer=hits.id.isin(cited))
    print(f"answered from {len(hits)} papers with abstracts · answer cites {len(set(cited))} of them"
          + (f" · NOT among the sources: {bad}" if bad else " · no invented citations"))
    return answer, hits


class QuestionIdeas(BaseModel):
    questions: list[str] = Field(description="Exactly 5 questions, each one sentence")


SUGGEST_INSTR = ("Suggest 5 questions a PhD student with this project could ask the research literature. "
                 "They must be answerable from paper abstracts: about findings, mechanisms, conditions, methods or "
                 "disagreements. Make them varied: at least one about where studies disagree, one about methods or "
                 "data, and one linking two streams. Plain, specific wording, at most 25 words each.")


def suggest_questions(project: str, streams: dict | None = None, instructions: str = SUGGEST_INSTR) -> list[str]:
    """Five questions to ask the literature (Lens 9), drafted by the LLM from your project description."""
    text = "MY PROJECT: " + project + ("\n\nRESEARCH STREAMS IN THE FIELD: " + "; ".join(streams.values()) if streams else "")
    r = extract(text, QuestionIdeas, instructions)
    return r.data.questions[:5] if r.data else ["Where do studies in this field disagree, and why might their results differ?"]
