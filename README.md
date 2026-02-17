# SNS / 広告データ統合ツール

## 実行方法（この1コマンドだけ）
```bash
python -m src.main --input_dir ./input --output_dir ./output --config_dir ./config --apply_suggested_mapping true
```

- `input` フォルダに元データ（CSV/TSV/XLSX）を入れて実行してください。
- 初回実行で `config/mapping.suggested.yaml` が生成され、同時に `config/mapping.yaml` に反映されます。
- 次回以降は `config/mapping.yaml` を再利用します。
