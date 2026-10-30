"""Profile 15,000 incidents into root-cause buckets, and measure how right the profile is.

    python -m desk profile          # prints the stages and metrics; writes .runtime/profile.json and PROFILE-REPORT.md

Buckets: knowledge_gap, user_education, defect, access_permission, routing_config, data_issue, outage_performance, duplicate_noise.

Four stages, each measured against a held-out answer key (the generator's labels; in real life: a sample a human labelled):
  1 RULES       high-precision patterns on close_code / close_notes ("Duplicate", "PRB…", "unlocked", "parent INC…")
  2 CLASSIFIER  logistic regression on the incident vectors already in Chroma, trained on 600 labelled incidents.
                It predicts a *family*: knowledge_gap and user_education share one family, "explained", because the
                incident text cannot tell them apart. The caller asked; an analyst explained. The difference is elsewhere:
  3 COVERAGE    for "explained" incidents, search the policy / workflow / UI documents. A document above the coverage gate
                means the answer existed (user_education); nothing above it means nobody wrote it down (knowledge_gap).
  4 CLUSTERS    k-means over the knowledge-gap incidents: each cluster is a candidate article, with its size, its words,
                representative incidents and the closest existing document (which is, by definition, not close enough).
Plus a contradiction check: numbers in resolutions ("limit is 25 MB") that disagree with the document they matched.
"""
from __future__ import annotations

import json
import re
import time
from collections import Counter, defaultdict
from datetime import datetime

import numpy as np

from desk import config
from desk.rag.clean import clean_incidents
from desk.rag.embed import QUERY_PREFIX, embedder
from desk.rag.index import get_collection
from desk.rag.load import load_incidents
from desk.stats import confusion, macro_f1

GENERIC = re.compile(r"^(Resolved|Fixed|Assisted caller|Issue resolved|Caller confirmed|Resolved per caller|Explained to caller)", re.I)
BUCKETS = ["knowledge_gap", "user_education", "defect", "access_permission", "routing_config", "data_issue",
           "outage_performance", "duplicate_noise"]
FAMILY = {b: ("explained" if b in ("knowledge_gap", "user_education") else b) for b in BUCKETS}
N_LABELLED = 600
MERGE_COS = 0.85                       # two gap clusters this close are one topic worded differently
PROFILE_JSON = config.RUNTIME_DIR / "profile.json"
REPORT = config.RUNTIME_DIR / "PROFILE-REPORT.md"

RULES = [  # (name, test(incident) -> bool, bucket)  -- ordered; first match wins
    ("close_code Duplicate", lambda r: r.get("close_code") == "Duplicate", "duplicate_noise"),
    ("parent major incident", lambda r: bool(r.get("parent_incident")) or "major incident" in r["close_notes"].lower(), "outage_performance"),
    ("PRB / Known Error", lambda r: "PRB0" in r["close_notes"] or r.get("close_code") == "Known Error", "defect"),
    ("routing rule / reassigned", lambda r: re.search(r"\bRR-\d{4}\b|reassigned|UNASSIGNED", r["close_notes"]) is not None, "routing_config"),
    ("unlock / access catalog", lambda r: re.search(r"[Uu]nlock|REQ00\d+|approver group|[Pp]rovisioned", r["close_notes"]) is not None, "access_permission"),
    ("data corrected", lambda r: re.search(r"[Dd]ata (corrected|refreshed|sync)|directory feed|regenerated", r["close_notes"]) is not None, "data_issue"),
    ("caller unreachable / test", lambda r: re.search(r"could not be reached|No response from caller|Test ticket", r["close_notes"]) is not None, "duplicate_noise"),
]


def _vectors(ids: list[str]) -> np.ndarray:
    """Reuse the vectors the RAG build stored: profiling 15,000 incidents should not embed them a second time."""
    col = get_collection("incident_resolutions")
    vecs = {}
    for s in range(0, len(ids), 2000):
        got = col.get(ids=ids[s: s + 2000], include=["embeddings"])
        vecs.update(zip(got["ids"], got["embeddings"]))
    return np.array([vecs[i] for i in ids], dtype=np.float32)


def _doc_matrix() -> tuple[np.ndarray, list[dict]]:
    """All policy / workflow / UI chunk vectors in one matrix, for the coverage test (a few hundred rows)."""
    mats, metas = [], []
    for src in ("kb_policy", "kb_workflow", "kb_ui", "kb_drafts"):
        try:
            got = get_collection(src).get(include=["embeddings", "metadatas", "documents"])
        except Exception:
            continue
        if len(got["ids"]):
            mats.append(np.array(got["embeddings"], dtype=np.float32))
            metas += [{"id": i, "source": src, **m, "text": d} for i, m, d in zip(got["ids"], got["metadatas"], got["documents"])]
    return (np.vstack(mats) if mats else np.zeros((0, config.EMBED_DIM), np.float32)), metas


def boot_acc(correct: np.ndarray, n: int = 1000, seed: int = 2026) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = np.sort(correct[rng.integers(0, len(correct), (n, len(correct)))].mean(axis=1))
    return round(float(means[int(n * 0.025)]), 3), round(float(means[int(n * 0.975) - 1]), 3)


def run(explain: bool = True) -> dict:
    from sklearn.cluster import KMeans
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import silhouette_score

    out_lines: list[str] = []

    def say(s: str = ""):
        out_lines.append(s)
        if explain:
            print(s, flush=True)

    t0 = time.time()
    key = json.loads((config.RUNTIME_DIR / "answer_key.json").read_text())
    rows, _ = load_incidents()
    rows, _ = clean_incidents(rows)
    rows = [r for r in rows if r["number"] in key]                     # the 15,000 with an answer key (recent live ones have none)
    ids = [r["number"] for r in rows]
    gold = [key[i]["bucket"] for i in ids]
    rng = np.random.default_rng(config.SEED)
    labelled = set(rng.choice(len(rows), N_LABELLED, replace=False).tolist())
    test = [i for i in range(len(rows)) if i not in labelled]
    say(f"# Incident profile · {len(rows):,} incidents · labelled sample {N_LABELLED} (train/calibrate) · held out {len(test):,} (measure)")

    # ---- stage 1: rules ----
    rule_pred, rule_name = [], []
    for r in rows:
        hit = next(((n, b) for n, f, b in RULES if f(r)), (None, None))
        rule_name.append(hit[0])
        rule_pred.append(hit[1])
    fired = [i for i in test if rule_pred[i]]
    prec = sum(rule_pred[i] == gold[i] for i in fired) / max(1, len(fired))
    say(f"\n1 RULES       fired on {len(fired) / len(test):.1%} of held-out incidents · precision {prec:.1%}")
    for n, _, b in RULES:
        f_i = [i for i in fired if rule_name[i] == n]
        if f_i:
            say(f"    {n:28s} -> {b:20s} fired {len(f_i):5,d}  precision {sum(gold[i] == b for i in f_i) / len(f_i):.1%}")

    # ---- stage 2: classifier on stored vectors ----
    X = _vectors(ids)
    fam_gold = [FAMILY[g] for g in gold]
    tr = sorted(labelled)
    clf = LogisticRegression(max_iter=2000, C=4.0)
    clf.fit(X[tr], [fam_gold[i] for i in tr])
    fam_clf = clf.predict(X)
    fam_pred = [FAMILY[rule_pred[i]] if rule_pred[i] else fam_clf[i] for i in range(len(rows))]
    acc_clf_only = np.mean([fam_clf[i] == fam_gold[i] for i in test])
    acc_fam = np.mean([fam_pred[i] == fam_gold[i] for i in test])
    say(f"\n2 CLASSIFIER  logistic regression on {X.shape[1]}-dim vectors from Chroma (no re-embedding), trained on {len(tr)} labelled incidents")
    say(f"    family accuracy, classifier alone: {acc_clf_only:.1%} · rules first, then classifier: {acc_fam:.1%}")

    # ---- stage 3: coverage test for the 'explained' family ----
    D, dmeta = _doc_matrix()
    e = embedder()
    expl = [i for i in range(len(rows)) if fam_pred[i] == "explained"]

    def emb(texts):
        return np.array(list(e.model.embed(texts, batch_size=16)), dtype=np.float32) if texts else np.zeros((0, config.EMBED_DIM), np.float32)

    QV = emb([QUERY_PREFIX + rows[i]["short_description"] for i in expl])
    informative = np.array([0.0 if GENERIC.match(rows[i]["close_notes"]) else 1.0 for i in expl])
    sim_q_all = QV @ D.T if len(D) else np.zeros((len(expl), 1))
    sim_q = sim_q_all.max(axis=1)
    best_doc = sim_q_all.argmax(axis=1)
    lab = [k for k, i in enumerate(expl) if i in labelled and gold[i] in ("knowledge_gap", "user_education")]
    y = np.array([gold[expl[k]] == "user_education" for k in lab])
    # naive: one cosine gate on the question ("is there a document ABOUT this?")
    grid = np.round(np.arange(0.55, 0.92, 0.005), 3)
    gate = float(max(grid, key=lambda g: np.sum((sim_q[lab] >= g) == y))) if lab else 0.7
    naive = np.where(sim_q >= gate, "user_education", "knowledge_gap")
    # better: coverage is a property of a TOPIC. Cluster the explained incidents, label each cluster from its labelled members.
    from sklearn.cluster import KMeans as _KM
    ks = {}
    samp = np.random.default_rng(config.SEED).choice(len(expl), min(3000, len(expl)), replace=False)
    for k in (8, 10, 12, 14, 16, 18, 20):
        km_ = _KM(n_clusters=k, n_init=4, random_state=config.SEED).fit(QV[samp])
        ks[k] = silhouette_score(QV[samp], km_.labels_, random_state=config.SEED)
    k_topics = max(ks, key=ks.get)
    topics = _KM(n_clusters=k_topics, n_init=8, random_state=config.SEED).fit(QV).labels_
    topic_label, topic_info = {}, []
    for c in range(k_topics):
        mem = [k for k in range(len(expl)) if topics[k] == c]
        labs = [gold[expl[k]] for k in mem if expl[k] in labelled and gold[expl[k]] in ("knowledge_gap", "user_education")]
        hint = float(np.mean(sim_q[mem]))
        if labs:
            topic_label[c] = Counter(labs).most_common(1)[0][0]
            how = f"{len(labs)} labelled"
        else:
            topic_label[c] = "user_education" if hint >= gate else "knowledge_gap"
            how = "no labels: cosine hint"
        topic_info.append((c, len(mem), topic_label[c], how, hint, rows[expl[mem[0]]]["short_description"]))
    smart = np.array([topic_label[topics[k]] for k in range(len(expl))])
    final = list(fam_pred)
    for k, i in enumerate(expl):
        final[i] = smart[k]
    held = [k for k, i in enumerate(expl) if i not in labelled and gold[i] in ("knowledge_gap", "user_education")]
    acc_naive = float(np.mean([naive[k] == gold[expl[k]] for k in held])) if held else 0.0
    acc_smart = float(np.mean([smart[k] == gold[expl[k]] for k in held])) if held else 0.0
    rec = lambda arr: float(np.mean([arr[k] == "knowledge_gap" for k in held if gold[expl[k]] == "knowledge_gap"]))
    say(f"\n3 COVERAGE    {len(expl):,} 'explained' incidents vs {len(D)} document chunks (policy, workflow, UI)")
    say(f"    naive, per incident: question cosine >= {gate:.3f} means 'covered' -> accuracy {acc_naive:.1%}, knowledge-gap recall {rec(naive):.1%}")
    say(f"    why it fails: every in-domain question scores ~0.7-0.8 against SOME document; being ABOUT a screen is not being ANSWERED by it")
    say(f"    per topic: {k_topics} topics (k by silhouette: " + ", ".join(f"{k} {s:.3f}" for k, s in ks.items()) + ")")
    say(f"      each topic takes the majority label of its labelled members (a person reviews ~20 per topic, not 15,000 incidents)")
    for c, n, tl, how, hint, ex in sorted(topic_info, key=lambda x: -x[1]):
        say(f"      topic {c:2d} {n:5,d} incidents -> {tl:15s} ({how}; mean doc cosine {hint:.3f}) e.g. \"{ex[:60]}\"")
    say(f"      -> accuracy {acc_smart:.1%}, knowledge-gap recall {rec(smart):.1%}")

    # ---- metrics: all 8 buckets on the held-out set ----
    g_t, p_t = [gold[i] for i in test], [final[i] for i in test]
    correct = np.array([a == b for a, b in zip(g_t, p_t)], dtype=float)
    acc, (lo, hi) = float(correct.mean()), boot_acc(correct)
    mf1, per = macro_f1(g_t, p_t)
    labels, cm = confusion(g_t, p_t)
    say(f"\nMEASURED on {len(test):,} held-out incidents: accuracy {acc:.1%} (95% CI {lo:.1%}-{hi:.1%}) · macro-F1 {mf1:.3f}")
    say(f"    {'bucket':20s} {'prec':>6s} {'recall':>7s} {'F1':>6s} {'n':>6s}")
    for b in BUCKETS:
        if b in per:
            v = per[b]
            say(f"    {b:20s} {v['precision']:6.2f} {v['recall']:7.2f} {v['f1']:6.2f} {v['support']:6,d}")
    rec_cat = Counter((r["category"], key[r["number"]]["bucket"]) for r in rows)
    say("    (the recorded ServiceNow category alone cannot do this: 'other' holds "
        + ", ".join(f"{b} {n}" for (c, b), n in rec_cat.most_common() if c == "other")[:200] + " ...)")

    # ---- stage 4: clusters of knowledge gaps ----
    gap_idx = [i for i in range(len(rows)) if final[i] == "knowledge_gap"]
    clusters = []
    if len(gap_idx) >= 10:
        Xg = X[gap_idx]
        scores = {}
        for k in range(2, 8):
            km = KMeans(n_clusters=k, n_init=5, random_state=config.SEED).fit(Xg)
            scores[k] = silhouette_score(Xg, km.labels_, sample_size=min(2000, len(gap_idx)), random_state=config.SEED)
        k_best = max(scores, key=scores.get)
        km = KMeans(n_clusters=k_best, n_init=10, random_state=config.SEED).fit(Xg)
        cents = km.cluster_centers_ / np.linalg.norm(km.cluster_centers_, axis=1, keepdims=True)
        parent = list(range(k_best))                                  # merge clusters whose centres point the same way
        for a in range(k_best):
            for b in range(a + 1, k_best):
                if float(cents[a] @ cents[b]) > MERGE_COS:
                    parent[b] = parent[a]
        km.labels_ = np.array([parent[l] for l in km.labels_])
        merged = k_best - len(set(parent))
        say(f"\n4 CLUSTERS    {len(gap_idx):,} knowledge-gap incidents · k chosen by silhouette: "
            + ", ".join(f"k={k} {s:.3f}" for k, s in scores.items()) + f" -> k={k_best}")
        if merged:
            say(f"    merged {merged} cluster(s) whose centres have cosine > {MERGE_COS} (typos split one topic into several)")
        for c in sorted(set(parent)):
            members = [gap_idx[j] for j in range(len(gap_idx)) if km.labels_[j] == c]
            cen = X[members].mean(axis=0)
            cen = cen / np.linalg.norm(cen)
            order = sorted(members, key=lambda i: -float(X[i] @ cen))
            words = Counter(w for i in members for w in re.findall(r"[a-z]{4,}", rows[i]["short_description"].lower())
                            if w not in {"what", "does", "this", "that", "with", "have", "need", "from", "there", "request", "portal"})
            dsim = D @ cen if len(D) else np.zeros(0)
            near = dmeta[int(dsim.argmax())] if len(D) else {}
            topic_mix = Counter(key[rows[i]["number"]]["topic"] for i in members)
            clusters.append({"cluster": c, "size": len(members), "top_words": [w for w, n in words.most_common(12) if n >= 0.1 * len(members)][:6],
                             "examples": [{"number": rows[i]["number"], "problem": rows[i]["short_description"], "resolution": rows[i]["close_notes"]} for i in order[:4]],
                             "resolutions": [r for r, _ in Counter(rows[i]["close_notes"] for i in members
                                                                   if not GENERIC.match(rows[i]["close_notes"])).most_common(3)],
                             "nearest_doc": {"id": near.get("id"), "title": near.get("title"), "similarity": round(float(dsim.max()), 3) if len(D) else None},
                             "true_topics": dict(topic_mix.most_common(3)), "regions": dict(Counter(rows[i]["u_region"] for i in members))})
        clusters.sort(key=lambda c: -c["size"])
        for c in clusters:
            say(f"    cluster {c['cluster']}: {c['size']:4d} incidents · words {', '.join(c['top_words'])} · nearest doc "
                f"{c['nearest_doc']['id']} ({c['nearest_doc']['similarity']}) · answer key says {c['true_topics']}")
            say(f"        e.g. {c['examples'][0]['number']}: \"{c['examples'][0]['problem']}\" -> \"{c['examples'][0]['resolution'][:90]}\"")

    # ---- contradictions: resolution numbers vs the matched document ----
    contradictions = defaultdict(lambda: {"incidents": 0, "says": Counter(), "doc_says": set()})
    for k, i in enumerate(expl):
        if final[i] != "user_education" or not informative[k]:
            continue
        rs = re.findall(r"(\d+)\s?MB", rows[i]["close_notes"])
        if not rs:
            continue
        d = dmeta[int(best_doc[k])]
        ds = set(re.findall(r"(\d+)\s?MB", d["text"]))
        if ds and not set(rs) & ds:
            c = contradictions[d["source_id"]]
            c["incidents"] += 1
            c["says"].update(rs)
            c["doc_says"] |= ds
            c["title"] = d.get("title")
    contra = [{"doc": k, "title": v["title"], "incidents": v["incidents"], "resolutions_say": dict(v["says"]), "doc_says": sorted(v["doc_says"])}
              for k, v in contradictions.items() if v["incidents"] >= 5]
    if contra:
        say("\nCONTRADICTIONS (resolutions disagree with the document they matched):")
        for c in contra:
            say(f"    {c['doc']} '{c['title']}' says {', '.join(x + ' MB' for x in c['doc_says'])}; {c['incidents']} resolutions say "
                + ", ".join(f"{k} MB ({v})" for k, v in c["resolutions_say"].items()))

    # ---- dashboard data ----
    by_bucket = Counter(final)
    weekly = defaultdict(Counter)
    for r, b in zip(rows, final):
        wk = datetime.strptime(r["sys_created_on"], "%Y-%m-%d %H:%M:%S").strftime("%G-W%V")
        weekly[wk][b] += 1
    region = defaultdict(Counter)
    for r, b in zip(rows, final):
        region[r["u_region"]][b] += 1
    _write_back(ids, final)
    say(f"\nprofile_accuracy: {acc:.3f} (95% CI {lo:.3f}-{hi:.3f}) · macro_f1 {mf1:.3f} · knowledge_gap {by_bucket['knowledge_gap']:,} · "
        f"gap clusters {len(clusters)} · {time.time() - t0:.0f}s")
    result = {"n": len(rows), "labelled": N_LABELLED, "held_out": len(test), "buckets": dict(by_bucket.most_common()),
              "accuracy": round(acc, 4), "ci": [lo, hi], "macro_f1": mf1, "per_bucket": per, "confusion": {"labels": labels, "matrix": cm},
              "rules": {"coverage": round(len(fired) / len(test), 4), "precision": round(prec, 4)},
              "family_accuracy": {"classifier_only": round(float(acc_clf_only), 4), "rules_then_classifier": round(float(acc_fam), 4)},
              "coverage_gate": gate, "clusters": clusters, "contradictions": contra,
              "weekly": {k: dict(v) for k, v in sorted(weekly.items())}, "by_region": {k: dict(v) for k, v in region.items()},
              "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    PROFILE_JSON.write_text(json.dumps(result, indent=1), encoding="utf-8")
    REPORT.write_text("\n".join(out_lines), encoding="utf-8")
    return result


def _write_back(ids: list[str], buckets: list[str]):
    """Enrich the incident collection's metadata with the predicted bucket, so retrieval can filter on it (bucket_pred)."""
    col = get_collection("incident_resolutions")
    for s in range(0, len(ids), 1000):
        got = col.get(ids=ids[s: s + 1000], include=["metadatas"])
        lookup = dict(zip(ids[s: s + 1000], buckets[s: s + 1000]))
        col.update(ids=got["ids"], metadatas=[{**m, "bucket_pred": lookup[i]} for i, m in zip(got["ids"], got["metadatas"])])
