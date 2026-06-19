from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .results import LyapunovResult

_RADON_LINE_RE = re.compile(
    r"""^\s*
    (?P<idx>\d+)\)\s+
    (?P<date>\d{4}-\d{2}-\d{2})\s+
    (?P<time>\d{2}:\d{2}:\d{2})\s+
    (?P<radon>[-+]?\d+(?:\.\d+)?)\s+
    (?P<temperature>[-+]?\d+(?:\.\d+)?)\s*°?C\s+
    (?P<humidity>[-+]?\d+(?:\.\d+)?)\s*%
    """,
    re.VERBOSE,
)


def read_radon_eye(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    rows: list[dict[str, object]] = []
    with path.open('r', encoding='utf-8', errors='replace') as f:
        for line in f:
            m = _RADON_LINE_RE.match(line)
            if not m:
                continue
            gd = m.groupdict()
            rows.append({
                'index': int(gd['idx']),
                'datetime': pd.to_datetime(gd['date'] + ' ' + gd['time']),
                'radon_bq_m3': float(gd['radon']),
                'temperature_c': float(gd['temperature']),
                'humidity_percent': float(gd['humidity']),
            })
    if not rows:
        raise ValueError(f'No Radon Eye rows could be parsed from: {path}')
    return pd.DataFrame(rows).sort_values('datetime').reset_index(drop=True)


def read_excel_series(path: str | Path, column: str | int, sheet: str | int = 0, header_none: bool = False) -> np.ndarray:
    header = None if header_none else 0
    df = pd.read_excel(path, sheet_name=sheet, header=header)
    if isinstance(column, int):
        s = df.iloc[:, column]
    else:
        if column not in df.columns:
            available = ', '.join(str(c) for c in df.columns)
            raise ValueError(f"Column '{column}' not found. Available columns: {available}")
        s = df[column]
    return pd.to_numeric(s, errors='coerce').dropna().to_numpy(dtype=float)


def read_series(path: str | Path, column: str | int = 0, delimiter: str = ',', header_none: bool = False, input_format: str = 'csv', sheet: str | int = 0) -> np.ndarray:
    path = Path(path)
    if input_format == 'radon-eye':
        df = read_radon_eye(path)
        if column in {'radon', 'radon_bq_m3', 0}:
            return df['radon_bq_m3'].to_numpy(dtype=float)
        if column in {'temperature', 'temperature_c', 1}:
            return df['temperature_c'].to_numpy(dtype=float)
        if column in {'humidity', 'humidity_percent', 2}:
            return df['humidity_percent'].to_numpy(dtype=float)
        raise ValueError('For radon-eye input use field/column: radon, temperature, or humidity.')
    if input_format == 'excel':
        return read_excel_series(path, column=column, sheet=sheet, header_none=header_none)
    if input_format != 'csv':
        raise ValueError('input_format must be one of: csv, excel, radon-eye')
    header = None if header_none else 'infer'
    df = pd.read_csv(path, delimiter=delimiter, header=header)
    if isinstance(column, int):
        s = df.iloc[:, column]
    else:
        if column not in df.columns:
            available = ', '.join(str(c) for c in df.columns)
            raise ValueError(f"Column '{column}' not found. Available columns: {available}")
        s = df[column]
    return pd.to_numeric(s, errors='coerce').dropna().to_numpy(dtype=float)


def write_summary(results: Iterable[LyapunovResult], outpath: str | Path) -> None:
    outpath = Path(outpath)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    payload = [r.summary_dict() for r in results]
    outpath.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def write_local_estimates(results: Iterable[LyapunovResult], outpath: str | Path) -> None:
    rows = []
    for r in results:
        for value in r.local_estimates:
            rows.append({'method': r.method, 'local_estimate': float(value)})
    pd.DataFrame(rows).to_csv(outpath, index=False)
