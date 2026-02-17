from __future__ import annotations

import csv
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from .utils import find_files, normalize_header

ENCODINGS = ["utf-8-sig", "utf-8", "cp932"]


def _read_delimited(path: Path):
    last = None
    for enc in ENCODINGS:
        try:
            text = path.read_text(encoding=enc)
            sample = text[:4096]
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
            sep = dialect.delimiter
            rows = list(csv.DictReader(text.splitlines(), delimiter=sep))
            return rows, enc, sep
        except Exception as e:
            last = e
    raise RuntimeError(last)


def _read_xlsx(path: Path):
    # minimal xlsx reader for first sheet
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = ["".join(t.itertext()) for t in root.findall("a:si", ns)]
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rid = wb.find("a:sheets/a:sheet", ns).attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        target = None
        for rel in rels:
            if rel.attrib.get("Id") == rid:
                target = rel.attrib["Target"]
                break
        sheet_xml = z.read("xl/" + target)
        root = ET.fromstring(sheet_xml)
        rows = []
        for row in root.findall(".//a:sheetData/a:row", ns):
            vals = []
            for c in row.findall("a:c", ns):
                t = c.attrib.get("t")
                v = c.find("a:v", ns)
                cell = v.text if v is not None else ""
                if t == "s" and cell.isdigit() and int(cell) < len(shared):
                    cell = shared[int(cell)]
                vals.append(cell)
            rows.append(vals)
    if not rows:
        return []
    header = [normalize_header(h) for h in rows[0]]
    data = []
    for r in rows[1:]:
        data.append({header[i]: (r[i] if i < len(r) else "") for i in range(len(header))})
    return data


def load_all_files(input_dir: str, logger):
    records = []
    for fp in find_files(input_dir):
        try:
            if fp.suffix.lower() == ".xlsx":
                rows = _read_xlsx(fp)
                enc, sep = "binary", "n/a"
            else:
                rows, enc, sep = _read_delimited(fp)
            norm_rows = [{normalize_header(k): v for k, v in r.items()} for r in rows]
            records.append({"path": str(fp), "rows": norm_rows, "status": "success", "encoding": enc, "sep": sep, "error": None})
            logger.info("Loaded file=%s rows=%s", fp, len(norm_rows))
        except Exception as e:
            records.append({"path": str(fp), "rows": [], "status": "failed", "encoding": None, "sep": None, "error": str(e)})
            logger.error("Load failed file=%s error=%s", fp, e)
    return records
