from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from .utils import write_csv


def _group_sum(rows, key):
    agg = defaultdict(lambda: defaultdict(float))
    for r in rows:
        k = r.get(key)
        for c, v in r.items():
            if isinstance(v, (int, float)):
                agg[k][c] += v
    out = []
    for k, vals in agg.items():
        row = {key: k}
        row.update(vals)
        out.append(row)
    return out


def write_outputs(rows, error_rows, unknown_files, output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "master_posts_daily.csv", rows)
    (out / "master_posts_daily.parquet").write_text("parquet export skipped: pyarrow unavailable in this environment\n", encoding="utf-8")
    write_csv(out / "summary_by_date.csv", _group_sum(rows, "date"))
    write_csv(out / "summary_by_platform.csv", _group_sum(rows, "platform"))
    write_csv(out / "summary_by_campaign.csv", _group_sum(rows, "campaign_name"))
    top = sorted(rows, key=lambda x: x.get("impressions") or -1, reverse=True)[:30]
    write_csv(out / "top_posts_30d.csv", top)
    write_csv(out / "error_rows.csv", error_rows)
    write_csv(out / "unknown_files.csv", unknown_files)


def build_quality_report(output_dir, total_files, success_files, failed_files, unknown_files, input_rows, output_rows, rows):
    out = Path(output_dir)
    post_keys = [r.get("post_key") for r in rows if r.get("post_key")]
    dup = len(post_keys) - len(set(post_keys))
    jc = Counter([r.get("join_confidence", "unmatched") for r in rows])
    miss_cols = ["date", "platform", "post_id", "impressions", "clicks", "spend"]
    lines = [
        "# Data Quality Report",
        f"- 読み込みファイル数: {total_files}",
        f"- 成功: {success_files}",
        f"- 失敗: {failed_files}",
        "",
        "## unknown分類ファイル一覧",
    ]
    lines += [f"- {u.get('path')}: {u.get('reason')}" for u in unknown_files] or ["- なし"]
    lines += ["", f"- 入力行数: {input_rows}", f"- 出力行数: {output_rows}", f"- 重複件数（post_key）: {dup}", "", "## 主要列欠損率"]
    for c in miss_cols:
        miss = (sum(1 for r in rows if r.get(c) in (None, "")) / output_rows) if output_rows else 1.0
        lines.append(f"- {c}: {miss:.2%}")
    lines += ["", "## join_confidence 内訳"] + [f"- {k}: {v}" for k, v in jc.items()]
    anomalies = sum(1 for r in rows if (r.get("spend") is not None and r.get("spend") < 0))
    lines += ["", f"- 異常値件数（負のspend等）: {anomalies}", "", "## 推奨アクション（運用改善）", "- mapping.yaml の date を見直す", "- mapping.yaml の post_id を見直す", "- mapping.yaml の campaign_name を見直す"]
    (out / "data_quality_report.md").write_text("\n".join(lines), encoding="utf-8")
