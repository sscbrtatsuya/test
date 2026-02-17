from __future__ import annotations

from dataclasses import dataclass

ORGANIC_HINTS = {
    "likes",
    "comments",
    "shares",
    "saves",
    "watchtime",
    "posturl",
    "postid",
    "followersgained",
    "いいね",
    "コメント",
    "シェア",
    "保存",
    "投稿url",
}

AD_HINTS = {
    "spend",
    "campaign",
    "adset",
    "clicks",
    "impressions",
    "cpm",
    "cpc",
    "広告費",
    "キャンペーン",
    "クリック",
    "表示回数",
}


@dataclass
class ClassificationResult:
    file_type: str
    reason: str


def classify_columns(columns: list[str]) -> ClassificationResult:
    cols = set(columns)
    organic_score = sum(1 for c in cols if c in ORGANIC_HINTS)
    ad_score = sum(1 for c in cols if c in AD_HINTS)
    if organic_score == 0 and ad_score == 0:
        return ClassificationResult("unknown", "No organic/ad hint columns found")
    if organic_score >= ad_score:
        return ClassificationResult("organic_post_data", f"organic_score={organic_score}, ad_score={ad_score}")
    return ClassificationResult("ad_data", f"organic_score={organic_score}, ad_score={ad_score}")
