# 売上・広告費・ROAS集約ツール

Next.js + TypeScriptで作成した、最小構成のROAS集計Webアプリです。  
DBは使わず、ローカルのCSVアップロードで売上と広告費を読み込み、**日別 × 媒体別**のROASを表示します。

## できること（MVP実装済み）
- 売上CSVをアップロード
- 広告費CSVをアップロード
- 日別 × 媒体別の表を表示
  - 売上
  - 広告費
  - ROAS（`売上 / 広告費`）
- 広告費が0のとき、ROASは `-` 表示

## 使い方
```bash
npm install
npm run dev
```

ブラウザで `http://localhost:3000` を開き、以下をアップロードしてください。
- 売上CSV
- 広告費CSV

## CSV列定義
### 売上CSV（sales.csv）
必須列:
- `date`: 日付（例: `2026-01-01`）
- `channel`: 媒体名（例: `Google`, `Meta`）
- `amount`: 売上金額（数値）

### 広告費CSV（ad_cost.csv）
必須列:
- `date`: 日付（例: `2026-01-01`）
- `channel`: 媒体名（例: `Google`, `Meta`）
- `amount`: 広告費金額（数値）

## サンプルCSV
- `public/samples/sales.csv`
- `public/samples/ad_cost.csv`

アプリ画面内のリンクからダウンロードして試せます。
