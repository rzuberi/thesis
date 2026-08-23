"""Core extraction engine: negation-aware regex matching over report text."""
import re

# spans matching these are treated as negated and their sentence's matches dropped
NEGATION = re.compile(
    r"\b(?:no|not|without|negative for|free of|absence of|no evidence of|"
    r"insufficient for|cannot exclude)\b",
    re.IGNORECASE,
)
SENT_SPLIT = re.compile(r"(?<=[.;:\n])\s+")


def _sentences(text):
    return [s for s in SENT_SPLIT.split(text) if s.strip()]


def _sentence_negates(sentence, match_start):
    """A match is negated if a negation cue appears before it in the sentence,
    within a 130-char window. Widened from 60 after the ERIN adjudication audit:
    negated list constructions ('no active inflammation, intestinal metaplasia,
    dysplasia nor evidence of malignancy') routinely exceed 60 chars, producing
    false CANCER calls. Sentence scoping still prevents cross-sentence overreach."""
    for m in NEGATION.finditer(sentence[:match_start]):
        if match_start - m.end() <= 130:
            return True
    return False


def label_report(text, schema, explain=False):
    """Return {field_name: label or None}; with explain=True also
    {field_name+"_evidence": (label, pattern, sentence)} for the winning rung."""
    out = {}
    evidence = {}
    text = str(text)
    sentences = _sentences(text)
    for f in schema.fields:
        hits = []  # (level_index, label)
        for li, (label, patterns) in enumerate(f.levels):
            for pat in patterns:
                rx = re.compile(pat, re.IGNORECASE)
                for sent in sentences:
                    for m in rx.finditer(sent):
                        if not _sentence_negates(sent, m.start()):
                            hits.append((li, label, pat, sent))
        if not hits:
            out[f.name] = None
        elif f.ladder:
            win = max(hits, key=lambda h: h[0])
            out[f.name] = win[1]
            evidence[f.name + "_evidence"] = {"label": win[1], "pattern": win[2],
                                              "sentence": win[3].strip()[:300]}
        else:
            counts = {}
            for li, label, pat, sent in hits:
                counts[label] = counts.get(label, 0) + 1
            out[f.name] = max(counts.items(), key=lambda kv: (kv[1], -[l for l, _ in f.levels].index(kv[0])))[0]
            win = next(h for h in hits if h[1] == out[f.name])
            evidence[f.name + "_evidence"] = {"label": win[1], "pattern": win[2],
                                              "sentence": win[3].strip()[:300]}
    if explain:
        out.update(evidence)
    return out


def label_frame(df, text_col, schema):
    """Label every row of a DataFrame; returns a new DataFrame of labels."""
    import pandas as pd
    rows = [label_report(t, schema) for t in df[text_col]]
    return pd.DataFrame(rows, index=df.index)
