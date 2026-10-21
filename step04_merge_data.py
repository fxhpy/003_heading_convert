"""第4部分 把小时级波浪插值到本船时间轴。"""

import numpy as np
import pandas as pd

from step03_convert_direction import interpolate_direction, relative_wave_direction

def merge_ship_and_wave(ship: pd.DataFrame, wave: pd.DataFrame) -> pd.DataFrame:
    source_time = wave["weather_timestamp_utc"].astype("int64").to_numpy() / 1e9
    target_time = ship["timestamp_utc"].astype("int64").to_numpy() / 1e9

    result = ship.copy()
    result["wave_height_m"] = np.interp(
        target_time, source_time, wave["wave_height_m"]
    )
    result["wave_period_s"] = np.interp(
        target_time, source_time, wave["wave_period_s"]
    )
    result["wave_direction_from_true_deg"] = interpolate_direction(
        source_time,
        wave["wave_direction_from_true_deg"].to_numpy(dtype=float),
        target_time,
    )

    relative_360, relative_signed = relative_wave_direction(
        result["wave_direction_from_true_deg"].to_numpy(),
        result["heading_true_deg"].to_numpy(),
    )
    result["relative_wave_from_deg_360"] = relative_360
    result["relative_wave_from_deg_signed"] = relative_signed
    return result
