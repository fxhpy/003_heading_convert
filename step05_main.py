"""第5部分 串联读取、查询、换算和保存。"""

import argparse
from pathlib import Path

from config import INPUT_FILE, OUTPUT_DIR
from step01_read_data import print_ship_summary, read_ship_data
from step02_fetch_wave import fetch_wave_data
from step04_merge_data import merge_ship_and_wave

def run(input_file: Path, output_dir: Path, dry_run: bool = False) -> None:
    ship = read_ship_data(input_file)
    print_ship_summary(ship)
    if dry_run:
        print("dry-run 完成：没有联网，也没有写结果。")
        return

    # 整段航迹约15 km，小于 ERA5-Ocean 约50 km网格，因此只查一个代表坐标。
    latitude = float(ship["latitude"].mean())
    longitude = float(ship["longitude"].mean())
    start_date = ship["timestamp_utc"].iloc[0].date().isoformat()
    end_date = ship["timestamp_utc"].iloc[-1].date().isoformat()

    wave = fetch_wave_data(latitude, longitude, start_date, end_date)
    result = merge_ship_and_wave(ship, wave)

    output_dir.mkdir(parents=True, exist_ok=True)
    wave.to_csv(output_dir / "wave_hourly.csv", index=False, encoding="utf-8-sig")
    result.to_csv(output_dir / "ship_wave.csv", index=False, encoding="utf-8-sig")
    print(f"结果已写入：{output_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description="查询波浪并计算相对浪向")
    parser.add_argument("--input", type=Path, default=INPUT_FILE)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run(args.input, args.output_dir, args.dry_run)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
