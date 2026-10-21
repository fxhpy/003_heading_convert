"""第2部分 从 Open-Meteo 查询一个模型网格的历史波浪。"""

import pandas as pd
import requests

from config import API_URL, MODEL, WAVE_COLUMNS


def fetch_wave_data(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(WAVE_COLUMNS),
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "GMT",
        "cell_selection": "sea",
        "models": MODEL,
    }
    response = requests.get(API_URL, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, list):
        data = data[0]

    hourly = data["hourly"]
    return pd.DataFrame(
        {
            "weather_timestamp_utc": pd.to_datetime(hourly["time"], utc=True),
            "wave_height_m": hourly["wave_height"],
            "wave_direction_from_true_deg": hourly["wave_direction"],
            "wave_period_s": hourly["wave_period"],
        }
    )
