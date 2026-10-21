from pathlib import Path


CONVERT_DIR = Path(__file__).resolve().parent
INPUT_FILE = CONVERT_DIR / "heading.xlsx"
OUTPUT_DIR = CONVERT_DIR / "output"
SHEET_NAME = "Sheet1"

API_URL = "https://marine-api.open-meteo.com/v1/marine"
MODEL = "era5_ocean"
WAVE_COLUMNS = ["wave_height", "wave_direction", "wave_period"]

EXCEL_COLUMNS = {
    "timestamp": "timestamp_utc",
    "全球定位系统1-纬度(-)": "latitude",
    "全球定位系统1-经度(-)": "longitude",
    "航向（真北）(°)": "heading_true_deg",
}
