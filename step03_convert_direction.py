"""第3部分 方向圆周插值和绝对浪向转相对浪向。"""

import numpy as np

def interpolate_direction(
    source_time: np.ndarray,
    source_degree: np.ndarray,
    target_time: np.ndarray,
) -> np.ndarray:
    """在单位圆上插值，避免 359° 和 1° 被插成 180°。"""
    radian = np.radians(source_degree)
    sin_value = np.interp(target_time, source_time, np.sin(radian))
    cos_value = np.interp(target_time, source_time, np.cos(radian))
    return np.degrees(np.arctan2(sin_value, cos_value)) % 360


def relative_wave_direction(
    absolute_wave_from_deg: np.ndarray,
    heading_true_deg: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:

    """0°为船艏来波 正值代表右舷 负值代表左舷。"""

    relative_360 = (absolute_wave_from_deg - heading_true_deg) % 360
    relative_signed = ((relative_360 + 180) % 360) - 180
    return relative_360, relative_signed
