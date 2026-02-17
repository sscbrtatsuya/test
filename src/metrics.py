from __future__ import annotations

from .utils import safe_div


def add_derived_metrics(rows: list[dict]):
    out = []
    for r in rows:
        x = dict(r)
        engage = sum([(x.get(c) or 0) for c in ["likes", "comments", "shares", "saves"]])
        x["er"] = safe_div(engage, x.get("impressions"))
        x["ctr"] = safe_div(x.get("clicks"), x.get("impressions"))
        x["cpm"] = safe_div((x.get("spend") or 0) * 1000, x.get("impressions"))
        x["cpc"] = safe_div(x.get("spend"), x.get("clicks"))
        x["cpf"] = safe_div(x.get("spend"), x.get("followers_gained"))
        x["cpv"] = safe_div(x.get("spend"), x.get("views"))
        x["roas"] = safe_div(x.get("revenue"), x.get("spend"))
        out.append(x)
    return out
