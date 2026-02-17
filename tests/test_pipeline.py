from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.joiner import join_organic_ads
from src.mapper import suggest_mapping
from src.normalizer import normalize_rows
from src.utils import build_post_key, safe_div


def test_column_name_variation_mapping():
    m = suggest_mapping(["表示回数", "いいね", "投稿日"])
    assert m["impressions"] == "表示回数"
    assert m["likes"] == "いいね"
    assert m["date"] == "投稿日"


def test_date_conversion_and_error_isolation():
    rows = [{"投稿日": "2024-01-01T00:00:00+00:00"}, {"投稿日": "bad"}]
    valid, err = normalize_rows(rows, {"date": "投稿日"}, "x.csv")
    assert len(valid) == 1
    assert len(err) == 1


def test_post_key_when_post_id_missing():
    assert build_post_key("instagram", None, "https://instagram.com/p/x/").startswith("instagram:url_")


def test_join_confidence_priority():
    o = [{"platform": "instagram", "post_id": "p1", "post_url": "a", "date": "2024-01-01", "campaign_name": "c"}, {"platform": "tiktok", "post_id": None, "post_url": "u", "date": "2024-01-01", "campaign_name": "c2"}]
    a = [{"platform": "instagram", "post_id": "p1"}, {"platform": "tiktok", "post_id": "x", "post_url": "u"}]
    j = join_organic_ads(o, a)
    conf = {x["join_confidence"] for x in j}
    assert "high" in conf and "medium" in conf


def test_safe_div_null_behavior():
    assert safe_div(1, 0) is None
    assert safe_div(None, 1) is None
