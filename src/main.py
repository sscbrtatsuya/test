from __future__ import annotations

import argparse
from pathlib import Path

from .classifier import classify_columns
from .io_loader import load_all_files
from .joiner import join_organic_ads
from .mapper import load_mapping
from .metrics import add_derived_metrics
from .normalizer import normalize_rows
from .reporter import build_quality_report, write_outputs
from .utils import setup_logger


def parse_args():
    p = argparse.ArgumentParser(description="SNS/広告マスターデータ統合")
    p.add_argument("--input_dir", default="./input")
    p.add_argument("--output_dir", default="./output")
    p.add_argument("--config_dir", default="./config")
    p.add_argument("--apply_suggested_mapping", default="true")
    return p.parse_args()


def main():
    args = parse_args()
    logger = setup_logger(args.output_dir)
    apply = str(args.apply_suggested_mapping).lower() == "true"

    loaded = load_all_files(args.input_dir, logger)
    all_cols = sorted({k for f in loaded for r in f.get("rows", []) for k in r.keys()})
    mapping = load_mapping(args.config_dir, apply, all_cols, logger)

    organic, ads, errors, unknown = [], [], [], []
    input_rows = 0

    for rec in loaded:
        if rec["status"] != "success":
            unknown.append({"path": rec["path"], "reason": f"load_failed: {rec['error']}"})
            continue
        rows = rec["rows"]
        input_rows += len(rows)
        cls = classify_columns(list(rows[0].keys()) if rows else [])
        logger.info("Classified file=%s as %s (%s)", rec["path"], cls.file_type, cls.reason)
        if cls.file_type == "unknown":
            unknown.append({"path": rec["path"], "reason": cls.reason})
            continue
        v, e = normalize_rows(rows, mapping, rec["path"])
        errors.extend(e)
        if cls.file_type == "organic_post_data":
            organic.extend(v)
        else:
            ads.extend(v)

    joined = join_organic_ads(organic, ads) if organic else [{**r, "join_confidence": "unmatched"} for r in ads]
    final_rows = add_derived_metrics(joined)
    write_outputs(final_rows, errors, unknown, args.output_dir)
    build_quality_report(args.output_dir, len(loaded), sum(1 for x in loaded if x['status']=='success'), sum(1 for x in loaded if x['status']=='failed'), unknown, input_rows, len(final_rows), final_rows)

    artifacts = ["master_posts_daily.csv","master_posts_daily.parquet","summary_by_date.csv","summary_by_platform.csv","summary_by_campaign.csv","top_posts_30d.csv","error_rows.csv","unknown_files.csv","data_quality_report.md","run_log.txt"]
    print("成果物一覧:")
    for a in artifacts:
        print(f"- {Path(args.output_dir)/a}")
    unmatched = sum(1 for r in final_rows if r.get("join_confidence") == "unmatched")
    print(f"unknownファイル件数: {len(unknown)}")
    print(f"unmatched件数: {unmatched}")
    print("次に人が調整すべき設定トップ3:")
    print("1) mapping.date")
    print("2) mapping.post_id")
    print("3) mapping.campaign_name")


if __name__ == "__main__":
    main()
