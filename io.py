"""
CSV loader helper.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CSVLoadConfig:
    path: str
    column: str | int = 0
    delimiter: str = ","
    skiprows: int = 0
    header_none: bool = False


def load_series_from_csv(cfg: CSVLoadConfig) -> np.ndarray:
    header = None if cfg.header_none else "infer"
    df = pd.read_csv(cfg.path, delimiter=cfg.delimiter, skiprows=cfg.skiprows, header=header)
    if isinstance(cfg.column, int):
        s = df.iloc[:, cfg.column]
    else:
        s = df[cfg.column]
    return s.to_numpy(dtype=float)
