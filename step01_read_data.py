"""第1部分：读取和清理本船航线。"""

from pathlib import Path

import pandas as pd

from config import EXCEL_COLUMNS, SHEET_NAME


def read_ship_data(path: Path, sheet_name: str = SHEET_NAME) -> pd.DataFrame:
    """读取 Excel  只保留时间、经纬度和真航向"""
    raw = pd.read_excel(path, sheet_name=sheet_name)
    missing = [name for name in EXCEL_COLUMNS if name not in raw.columns]
    if missing:
        raise ValueError(f"Excel 缺少列：{missing}")

    ship = raw[list(EXCEL_COLUMNS)].rename(columns=EXCEL_COLUMNS).copy()
    ship["timestamp_utc"] = pd.to_datetime(
        ship["timestamp_utc"], errors="coerce", utc=True
    )
    for column in ["latitude", "longitude", "heading_true_deg"]:
        ship[column] = pd.to_numeric(ship[column], errors="coerce")

    ship = ship.dropna().copy()
    ship = ship[
        ship["latitude"].between(-90, 90)
        & ship["longitude"].between(-180, 180)
        & ship["heading_true_deg"].between(0, 360)
    ]
    ship["heading_true_deg"] %= 360
    ship = ship.sort_values("timestamp_utc").drop_duplicates("timestamp_utc")
    return ship.reset_index(drop=True)


def print_ship_summary(ship: pd.DataFrame) -> None:
    """打印最基本的检查结果"""
    gaps = ship["timestamp_utc"].diff().dt.total_seconds()
    print(f"航线行数：{len(ship)}")
    print(f"时间范围：{ship.timestamp_utc.iloc[0]} ~ {ship.timestamp_utc.iloc[-1]}")
    print(f"超过1秒的时间间隔：{int((gaps > 1.5).sum())} 处")
