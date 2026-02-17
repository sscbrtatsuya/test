from __future__ import annotations

from pathlib import Path

from .utils import normalize_header, parse_simple_yaml, write_simple_yaml

TARGET_COLUMNS = ["date","platform","account_name","post_id","post_url","campaign_name","ad_platform","paid_organic","impressions","reach","views","clicks","likes","comments","shares","saves","watch_time_sec","followers_gained","spend","conversions","revenue"]

SYNONYMS = {
    "date": ["date", "day", "投稿日", "createdat", "datetime", "日時"],
    "platform": ["platform", "媒体", "sns", "channel"],
    "account_name": ["account", "accountname", "アカウント", "アカウント名"],
    "post_id": ["postid", "mediaid", "投稿id", "videoid"],
    "post_url": ["posturl", "url", "投稿url", "permalink", "リンク"],
    "campaign_name": ["campaign", "campaignname", "キャンペーン", "キャンペーン名"],
    "ad_platform": ["adplatform", "広告媒体", "adsource"],
    "paid_organic": ["paidorganic", "種別", "配信種別"],
    "impressions": ["impressions", "imp", "表示回数"],
    "reach": ["reach", "リーチ"],
    "views": ["views", "再生数", "視聴回数"],
    "clicks": ["clicks", "クリック"],
    "likes": ["likes", "いいね"],
    "comments": ["comments", "コメント"],
    "shares": ["shares", "シェア"],
    "saves": ["saves", "保存"],
    "watch_time_sec": ["watchtime", "watchtimesec", "視聴時間"],
    "followers_gained": ["followersgained", "フォロワー増加"],
    "spend": ["spend", "cost", "広告費", "消化金額"],
    "conversions": ["conversions", "cv", "コンバージョン"],
    "revenue": ["revenue", "sales", "売上", "購入金額"],
}


def suggest_mapping(columns: list[str]) -> dict[str, str]:
    out = {}
    norm_cols = {c: normalize_header(c) for c in columns}
    for target, syns in SYNONYMS.items():
        ns = [normalize_header(s) for s in syns]
        best = None
        best_score = 0
        for raw, nc in norm_cols.items():
            if nc in ns:
                best, best_score = raw, 100
                break
            if any(n in nc or nc in n for n in ns):
                if 80 > best_score:
                    best, best_score = raw, 80
        if best:
            out[target] = best
    return out


def load_mapping(config_dir: str, apply_suggested: bool, all_columns: list[str], logger):
    cdir = Path(config_dir)
    cdir.mkdir(parents=True, exist_ok=True)
    primary = cdir / "mapping.yaml"
    suggested = cdir / "mapping.suggested.yaml"

    if primary.exists():
        logger.info("Using mapping.yaml")
        return parse_simple_yaml(primary)

    sg = suggest_mapping(all_columns)
    write_simple_yaml(suggested, sg)
    logger.info("Generated mapping.suggested.yaml")
    if apply_suggested:
        write_simple_yaml(primary, sg)
        logger.info("Promoted suggested mapping to mapping.yaml")
        return sg
    return {}
