# 003_heading_convert：航向与相对浪向转换

读取船舶航线 Excel，使用整段航迹的平均经纬度向 Open-Meteo 查询小时级波浪数据，再把波高、周期和浪向插值到航线时间轴，计算相对于船艏的来波方向。

## 项目文件

| 文件 | 功能 |
| --- | --- |
| `config.py` | 默认输入输出路径、工作表名称、Excel 列映射和 API 参数 |
| `step01_read_data.py` | 读取、清理航线数据并打印时间范围与间隔统计 |
| `step02_fetch_wave.py` | 请求 Open-Meteo 海洋接口并整理小时级波浪数据 |
| `step03_convert_direction.py` | 浪向圆周插值和相对来波方向计算 |
| `step04_merge_data.py` | 将小时级波浪插值到每条航线记录 |
| `step05_main.py` | 命令行入口，串联读取、查询、换算和保存 |
| `test_convert.py` | 方向跨越 0° 和相对方向的离线单元测试 |

原始 `heading.xlsx` 和 `output/` 中的结果保留在本地，不上传到 GitHub。克隆仓库后需要自行准备输入数据；缓存、编辑器设置和虚拟环境也不纳入版本管理。

## 环境准备

代码使用 Python 3.9 起支持的类型标注。依赖为 NumPy、pandas、requests，以及读取 `.xlsx` 所需的 openpyxl。

在项目根目录的 PowerShell 中执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 输入与配置

默认输入是项目根目录下的 `heading.xlsx`，工作表为 `Sheet1`。脚本按列名读取以下四列，其他列不会进入输出：

| Excel 原始列名 | 内部列名 | 含义 |
| --- | --- | --- |
| `timestamp` | `timestamp_utc` | 时间戳 |
| `全球定位系统1-纬度(-)` | `latitude` | 纬度，范围 −90 到 90 |
| `全球定位系统1-经度(-)` | `longitude` | 经度，范围 −180 到 180 |
| `航向（真北）(°)` | `heading_true_deg` | 相对真北的航向，单位为度 |

时间通过 `pd.to_datetime(..., utc=True)` 解析；没有时区的信息会直接按 UTC 解释，不会自动从北京时间转换。请先核对原始记录的时区。

脚本将数值列转换为数字，删除缺失、解析失败和超出范围的记录；航向允许输入 0° 到 360°，随后归一化到 `[0, 360)`。记录按时间排序，同一时间戳只保留一条。清理后必须至少有一条记录，否则后续读取首末时间会失败。

可在 `config.py` 修改 `SHEET_NAME`、`EXCEL_COLUMNS`、`API_URL`、`MODEL` 和 `WAVE_COLUMNS`。默认接口为 `https://marine-api.open-meteo.com/v1/marine`，请求模型参数为 `era5_ocean`；代码请求波高、浪向和周期三个小时级字段。输入文件与输出目录也可以通过命令行指定。

## 执行

先进行离线输入检查，只读取 Excel 和打印摘要，不请求 API，也不写结果：

```powershell
.\.venv\Scripts\python.exe step05_main.py --dry-run
```

正式运行：

```powershell
.\.venv\Scripts\python.exe step05_main.py
```

指定其他输入或输出位置：

```powershell
.\.venv\Scripts\python.exe step05_main.py --input "D:\data\heading.xlsx" --output-dir "D:\results\heading_convert"
```

正式运行需要联网。程序向 Open-Meteo 发送清理后航线的**平均经纬度**、首末日期及波浪参数；它只查询一个代表位置，不会沿航线逐点查询。请求使用 `timezone=GMT`、`cell_selection=sea` 和 `timeout=60`。当前没有重试或本地缓存逻辑，HTTP 错误直接抛出；接口的数据可用日期、返回内容和访问限制需要由实际运行确认。

## 转换规则

波高和周期使用 `numpy.interp` 进行线性插值。浪向先转换成单位圆上的正弦、余弦分量，分别插值后通过 `atan2` 还原，避免把 359° 与 1° 的中间方向算成 180°。

代码把 API 的 `wave_direction` 作为相对真北的来波方向，并按下面的公式计算船体相对方向：

```text
relative_wave_from_deg_360 = (绝对来波方向 − 真航向) mod 360
relative_wave_from_deg_signed = ((relative_wave_from_deg_360 + 180) mod 360) − 180
```

`0°` 表示船艏来波，`90°` 表示右舷来波，`270°`（有符号角 `−90°`）表示左舷来波，`180°`（有符号角 `−180°`）表示船艉来波。有符号角范围为 `[-180, 180)`。

小时级数据插值后与航线记录数量一致，但时间上的插值不会增加原始波浪数据的分辨率。超出 API 时间范围的目标时间会使用 `numpy.interp` 的端点值；代码没有另行检查覆盖范围、API 空结果或缺失值，正式使用前应检查结果。

## 输出

默认写入 `output/`，目录不存在时自动创建。再次运行会覆盖同名 CSV，编码为 `utf-8-sig`，不写 pandas 索引。

| 文件 | 列 |
| --- | --- |
| `wave_hourly.csv` | `weather_timestamp_utc`、`wave_height_m`、`wave_direction_from_true_deg`、`wave_period_s` |
| `ship_wave.csv` | 清理后的四个航线字段，以及 `wave_height_m`、`wave_period_s`、`wave_direction_from_true_deg`、`relative_wave_from_deg_360`、`relative_wave_from_deg_signed` |

## 离线测试

```powershell
.\.venv\Scripts\python.exe -m unittest test_convert.py
```

这两项测试检查方向跨越 0° 的插值和相对方向公式，不会读取真实航线或连接天气接口；它们不能替代真实输入、接口返回和完整输出的验证。
