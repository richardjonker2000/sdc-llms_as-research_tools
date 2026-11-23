---
name: cluster-texts
description: Group texts by their words without labels (TF-IDF and k-means, no LLM, runs on the CPU), the method of lesson 1 notebook 03. Use when a plan step asks what themes or groups are in a set of texts. Reports top words, typical texts, group sizes and how stable the groups are.
---

# Group texts without labels

Same method as **lesson 1, notebook 03**. Groups are a map for reading, **not findings**: the report says so.

## Ask first (method: the researcher decides)

1. **Which texts** (and which column: title, abstract, both).
2. **The number of groups k.** Propose 3 values (e.g. 4, 6, 8) and show the top words for each if the researcher has no preference; the researcher picks.
3. **Stop words** beyond the standard list (words that appear everywhere in this corpus).
4. Whether an LLM may **name** the groups (one call, optional).

## Steps (one script: `analysis/sN_cluster_<what>.py`)

```python
import re
from collections import Counter
import numpy as np
import pandas as pd

STOP = set("""a an and are as at be by for from has have in is it its of on or that the their this to was were with
which we our these those study paper results using used based analysis effect effects data new""".split())

def words(text):
    return [w for w in re.findall(r"[a-z][a-z\-]{2,}", str(text).lower()) if w not in STOP]

docs = [words(t) for t in texts]                                     # texts: the column the plan names
doc_freq = Counter(w for d in docs for w in set(d))
vocab = sorted(w for w, c in doc_freq.items() if 5 <= c <= 0.5 * len(docs))
col = {w: i for i, w in enumerate(vocab)}
X = np.zeros((len(docs), len(vocab)))
for i, d in enumerate(docs):
    for w, c in Counter(d).items():
        if w in col:
            X[i, col[w]] = c
X *= np.log(len(docs) / np.array([doc_freq[w] for w in vocab]))      # TF-IDF
X /= np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)    # length 1: dot product = cosine

def kmeans(X, k, seed):
    rng = np.random.default_rng(seed)
    centres = X[rng.choice(len(X), k, replace=False)]
    for _ in range(100):
        group = (X @ centres.T).argmax(axis=1)
        new = np.array([X[group == j].mean(axis=0) if (group == j).any() else centres[j] for j in range(k)])
        new /= np.maximum(np.linalg.norm(new, axis=1, keepdims=True), 1e-12)
        if np.allclose(new, centres):
            break
        centres = new
    return group, centres, (X @ centres.T).max(axis=1).mean()

group, centres, fit = max((kmeans(X, k, s) for s in range(20)), key=lambda r: r[2])   # best of 20 starts
```

## Required in the report

- N texts, vocabulary size, k, and the fit.
- Per group: size, the 10 top words (`centres[j].argsort()[::-1][:10]`), and the 3 most typical texts (highest similarity to the centre).
- **Stability**: run again with other seeds and report the share of pairs of texts still in the same group (as in notebook 03), next to the share for random groups (`(sizes ** 2).sum()`).
- Save `outputs/<name>_groups.csv` (id, group) and commit.

## Never

- present groups as findings or give them names as facts (names are labels for reading);
- pick k because the result looks nicer without telling the researcher;
- drop texts from groups without saying how many and why.
