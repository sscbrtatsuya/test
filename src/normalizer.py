from __future__ import annotations

from .mapper import TARGET_COLUMNS
from .utils import build_post_key, normalize_ad_platform, normalize_platform, normalize_url, parse_datetime_to_date, to_float


def normalize_rows(rows: list[dict], mapping: dict[str, str], source_file: str):
    valid, errors = [], []
    for i, r in enumerate(rows, start=2):
        row = {}
        for t in TARGET_COLUMNS:
            src = mapping.get(t)
            row[t] = r.get(src) if src else None

        if not row.get("platform"):
            row["platform"] = source_file
        row["platform"] = normalize_platform(row.get("platform"))
        row["ad_platform"] = normalize_ad_platform(row.get("ad_platform"))

        row["date"] = parse_datetime_to_date(row.get("date"))
        row["post_url"] = normalize_url(row.get("post_url"))
        row["source_file"] = source_file
        row["source_row_number"] = i
        row["post_key"] = build_post_key(row.get("platform"), row.get("post_id"), row.get("post_url"))

        for c in ["impressions","reach","views","clicks","likes","comments","shares","saves","watch_time_sec","followers_gained","spend","conversions","revenue"]:
            row[c] = to_float(row.get(c))

        if not row.get("date"):
            er = dict(row)
            er["error_reason"] = "invalid_date"
            errors.append(er)
        else:
            valid.append(row)
    return valid, errors
