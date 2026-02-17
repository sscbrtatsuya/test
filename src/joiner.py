from __future__ import annotations

from .utils import normalize_url


def _first_index(rows, key_fn):
    idx = {}
    for r in rows:
        idx.setdefault(key_fn(r), r)
    return idx


def join_organic_ads(organic_rows: list[dict], ad_rows: list[dict]):
    out = []
    k1 = _first_index(ad_rows, lambda r: (r.get("platform"), r.get("post_id")))
    k2 = _first_index(ad_rows, lambda r: normalize_url(r.get("post_url")))
    k3 = _first_index(ad_rows, lambda r: (r.get("platform"), r.get("date"), r.get("campaign_name")))

    for o in organic_rows:
        merged = dict(o)
        conf = "unmatched"
        m = k1.get((o.get("platform"), o.get("post_id"))) if o.get("post_id") else None
        if m:
            conf = "high"
        else:
            m = k2.get(normalize_url(o.get("post_url"))) if o.get("post_url") else None
            if m:
                conf = "medium"
            else:
                m = k3.get((o.get("platform"), o.get("date"), o.get("campaign_name")))
                if m:
                    conf = "low"
        if m:
            for k, v in m.items():
                if merged.get(k) in (None, "") and v not in (None, ""):
                    merged[k] = v
        merged["join_confidence"] = conf
        out.append(merged)
    return out
