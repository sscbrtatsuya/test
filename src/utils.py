from __future__ import annotations

import csv
import hashlib
import logging
import os
import re
import unicodedata
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

JST = timezone(timedelta(hours=9))


def normalize_header(name: str) -> str:
    text = unicodedata.normalize("NFKC", str(name or ""))
    text = text.strip().lower().replace("_", "")
    text = re.sub(r"\s+", "", text)
    return text


def safe_div(num: Any, den: Any):
    try:
        if num in (None, "") or den in (None, ""):
            return None
        n = float(num)
        d = float(den)
        if d == 0:
            return None
        return n / d
    except Exception:
        return None


def to_float(v: Any):
    try:
        if v in (None, ""):
            return None
        return float(str(v).replace(",", ""))
    except Exception:
        return None


def normalize_platform(value: str) -> str:
    v = str(value or "").lower()
    if "insta" in v:
        return "instagram"
    if "tiktok" in v or "tik tok" in v:
        return "tiktok"
    if "youtube" in v:
        return "youtube"
    return "unknown"


def normalize_ad_platform(value: str) -> str:
    v = str(value or "").lower()
    if any(x in v for x in ["meta", "facebook", "instagram ads"]):
        return "meta"
    if "tiktok" in v:
        return "tiktok_ads"
    if "google" in v:
        return "google_ads"
    if not v or v in {"none", "organic"}:
        return "none"
    return "other"


def normalize_url(url: str | None) -> str | None:
    if not url:
        return None
    u = str(url).strip().lower()
    u = re.sub(r"^https?://", "", u).rstrip("/")
    return u or None


def build_post_key(platform: str, post_id: str | None, post_url: str | None) -> str:
    p = normalize_platform(platform)
    if post_id:
        return f"{p}:{str(post_id).strip()}"
    digest = hashlib.md5((normalize_url(post_url) or "missing-url").encode()).hexdigest()[:12]
    return f"{p}:url_{digest}"


def parse_datetime_to_date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    s = str(value).strip()
    for fmt in [None, "%Y/%m/%d", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
        try:
            if fmt:
                dt = datetime.strptime(s, fmt)
            else:
                dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(JST).date().isoformat()
        except Exception:
            pass
    return None


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not fieldnames:
        fieldnames = sorted({k for r in rows for k in r.keys()}) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})


def setup_logger(output_dir: str) -> logging.Logger:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("sns_master")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fh = logging.FileHandler(Path(output_dir) / "run_log.txt", encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)
    return logger


def find_files(input_dir: str):
    base = Path(input_dir)
    files = []
    if not base.exists():
        return []
    for ext in ("*.csv", "*.tsv", "*.xlsx"):
        files.extend(base.rglob(ext))
    return sorted(set(files))


def parse_simple_yaml(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip("'\"")
    return out


def write_simple_yaml(path: Path, data: dict[str, str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{k}: {v}" for k, v in sorted(data.items())]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
