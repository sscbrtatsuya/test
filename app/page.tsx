"use client";

import { ChangeEvent, useMemo, useState } from "react";

type CsvRow = Record<string, string>;

type SalesRow = {
  date: string;
  channel: string;
  amount: number;
};

type AdCostRow = {
  date: string;
  channel: string;
  amount: number;
};

type AggregatedRow = {
  date: string;
  channel: string;
  sales: number;
  adCost: number;
  roas: number | null;
};

const REQUIRED_SALES_COLUMNS = ["date", "channel", "amount"];
const REQUIRED_AD_COLUMNS = ["date", "channel", "amount"];

function parseCsv(content: string): CsvRow[] {
  const lines = content
    .trim()
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  if (lines.length < 2) {
    return [];
  }

  const headers = lines[0].split(",").map((h) => h.trim());

  return lines.slice(1).map((line) => {
    const values = line.split(",").map((value) => value.trim());
    const row: CsvRow = {};

    headers.forEach((header, index) => {
      row[header] = values[index] ?? "";
    });

    return row;
  });
}

function validateColumns(rows: CsvRow[], requiredColumns: string[]): boolean {
  if (rows.length === 0) {
    return false;
  }

  return requiredColumns.every((column) => column in rows[0]);
}

function toSalesRows(rows: CsvRow[]): SalesRow[] {
  return rows
    .map((row) => ({
      date: row.date,
      channel: row.channel,
      amount: Number(row.amount),
    }))
    .filter((row) => row.date && row.channel && Number.isFinite(row.amount));
}

function toAdCostRows(rows: CsvRow[]): AdCostRow[] {
  return rows
    .map((row) => ({
      date: row.date,
      channel: row.channel,
      amount: Number(row.amount),
    }))
    .filter((row) => row.date && row.channel && Number.isFinite(row.amount));
}

function aggregateMetrics(salesRows: SalesRow[], adCostRows: AdCostRow[]): AggregatedRow[] {
  const map = new Map<string, { date: string; channel: string; sales: number; adCost: number }>();

  for (const row of salesRows) {
    const key = `${row.date}__${row.channel}`;
    const existing = map.get(key) ?? { date: row.date, channel: row.channel, sales: 0, adCost: 0 };
    existing.sales += row.amount;
    map.set(key, existing);
  }

  for (const row of adCostRows) {
    const key = `${row.date}__${row.channel}`;
    const existing = map.get(key) ?? { date: row.date, channel: row.channel, sales: 0, adCost: 0 };
    existing.adCost += row.amount;
    map.set(key, existing);
  }

  return Array.from(map.values())
    .map((row) => ({
      ...row,
      roas: row.adCost === 0 ? null : row.sales / row.adCost,
    }))
    .sort((a, b) => {
      if (a.date !== b.date) {
        return a.date.localeCompare(b.date);
      }
      return a.channel.localeCompare(b.channel);
    });
}

async function readFileAsText(file: File): Promise<string> {
  return await file.text();
}

export default function HomePage() {
  const [salesRows, setSalesRows] = useState<SalesRow[]>([]);
  const [adCostRows, setAdCostRows] = useState<AdCostRow[]>([]);
  const [salesError, setSalesError] = useState<string | null>(null);
  const [adError, setAdError] = useState<string | null>(null);

  const aggregatedRows = useMemo(() => aggregateMetrics(salesRows, adCostRows), [salesRows, adCostRows]);

  const onUploadSales = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    const content = await readFileAsText(file);
    const rows = parseCsv(content);

    if (!validateColumns(rows, REQUIRED_SALES_COLUMNS)) {
      setSalesError("売上CSVの列が不正です。date, channel, amount を含めてください。");
      setSalesRows([]);
      return;
    }

    setSalesError(null);
    setSalesRows(toSalesRows(rows));
  };

  const onUploadAdCost = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    const content = await readFileAsText(file);
    const rows = parseCsv(content);

    if (!validateColumns(rows, REQUIRED_AD_COLUMNS)) {
      setAdError("広告費CSVの列が不正です。date, channel, amount を含めてください。");
      setAdCostRows([]);
      return;
    }

    setAdError(null);
    setAdCostRows(toAdCostRows(rows));
  };

  return (
    <main>
      <h1>売上・広告費・ROAS 集計ツール（MVP）</h1>
      <p className="muted">売上CSVと広告費CSVをアップロードすると、日別×媒体別のROASを表示します。</p>

      <section className="panel">
        <div className="upload-grid">
          <div>
            <label htmlFor="sales-file">売上CSV</label>
            <input id="sales-file" type="file" accept=".csv,text/csv" onChange={onUploadSales} />
            {salesError && <p className="error">{salesError}</p>}
            <p className="muted">サンプル: <a href="/samples/sales.csv" download>sales.csv</a></p>
          </div>

          <div>
            <label htmlFor="ad-file">広告費CSV</label>
            <input id="ad-file" type="file" accept=".csv,text/csv" onChange={onUploadAdCost} />
            {adError && <p className="error">{adError}</p>}
            <p className="muted">サンプル: <a href="/samples/ad_cost.csv" download>ad_cost.csv</a></p>
          </div>
        </div>
      </section>

      <section className="panel">
        <h2>日別 × 媒体別 ROAS</h2>
        {aggregatedRows.length === 0 ? (
          <p className="muted">CSVをアップロードするとここに表が表示されます。</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>日付</th>
                <th>媒体</th>
                <th>売上</th>
                <th>広告費</th>
                <th>ROAS</th>
              </tr>
            </thead>
            <tbody>
              {aggregatedRows.map((row) => (
                <tr key={`${row.date}-${row.channel}`}>
                  <td>{row.date}</td>
                  <td>{row.channel}</td>
                  <td>{row.sales.toLocaleString()}</td>
                  <td>{row.adCost.toLocaleString()}</td>
                  <td>{row.roas === null ? "-" : row.roas.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}
