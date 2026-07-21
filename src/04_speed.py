# -*- coding: utf-8 -*-
"""좌표에서 속도·방향을 재계산한다 (전처리 1단계).

제공 Vehicle_Speed는 정지·저속 구간이 결측이라, 좌표(Local_X/Y, 미터)에서
차량별로 속도(km/h)와 진행 방향(도)을 다시 계산한다. 규칙은
notebook/01_속도재계산_탐색.ipynb에서 검증했다(제공 속도와 r=0.98 일치,
Ortho는 픽셀 좌표라 안 씀).

  add_kinematics(df) : 세션 df에 speed_kmh·direction_deg·speed_smooth 추가.
                       05_movement·06_conflicts가 이 함수를 그대로 가져다 쓴다.
  main()             : 800개 세션에 적용해 세션별 속도 요약을 저장(검증용).
                       전체 궤적은 저장하지 않는다(디스크 중복 방지) — 속도는
                       하위 단계에서 이 함수로 그때그때 붙인다.

규칙: 속도 = √(ΔX²+ΔY²)/Δt × 3.6,  방향 = atan2(ΔY, ΔX).
      Δt>0.1초(세그먼트 경계·궤적 시작)면 NaN. 이동 중앙값 평활(11프레임).

출력: data/processed/speed_summary.csv (세션 800개 한 줄씩)
사용: python src/04_speed.py [입력=data/interim] [출력=data/processed]
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

GAP_S = 0.1        # Δt가 이보다 크면 연속 프레임 아님 → 속도 NaN
SMOOTH = 11        # 이동 중앙값 창(프레임, ~0.37초)
STOP_KMH = 5.0     # 이 미만이면 정지로 간주(요약 지표용)


def local_time_to_sec(series: pd.Series) -> pd.Series:
    """'17:11:40.561' → 자정 기준 초. 벡터화."""
    parts = series.str.split(":", expand=True)
    return (parts[0].astype("int32") * 3600
            + parts[1].astype("int32") * 60
            + parts[2].astype("float64"))


def add_kinematics(df: pd.DataFrame, smooth: bool = True) -> pd.DataFrame:
    """세션 df에 speed_kmh·direction_deg(·speed_smooth) 추가해 반환.
    차량별 시간순 차분으로 계산하고, 세그먼트 경계(Δt>0.1s)·첫 프레임은 NaN.
    smooth=False면 평활 생략(속도만 필요한 요약 패스에서 빠름)."""
    df = df.copy()
    df["t"] = local_time_to_sec(df["Local_Time"])
    df = df.sort_values(["Vehicle_ID", "t"], kind="stable")
    g = df.groupby("Vehicle_ID", sort=False)
    dt = g["t"].diff()
    dx = g["Local_X"].diff()
    dy = g["Local_Y"].diff()
    ok = (dt > 0) & (dt <= GAP_S)                     # 연속 프레임만 (첫프레임·중복타임스탬프 제외)
    df["speed_kmh"] = np.where(ok, np.sqrt(dx * dx + dy * dy) / dt * 3.6, np.nan)
    df["direction_deg"] = np.where(ok, np.degrees(np.arctan2(dy, dx)), np.nan)
    if smooth:
        df["speed_smooth"] = (df.groupby("Vehicle_ID", sort=False)["speed_kmh"]
                              .transform(lambda s: s.rolling(SMOOTH, center=True, min_periods=1).median()))
    return df


def summarize(df: pd.DataFrame, name: str) -> dict:
    sp = df["speed_kmh"]
    valid = sp.notna()
    nv = int(valid.sum())
    moving = sp[valid & (sp >= STOP_KMH)]
    q = float(sp[valid].quantile(0.95)) if nv else np.nan
    return {
        "file": name,
        "rows": len(df),
        "vehicles": int(df["Vehicle_ID"].nunique()),
        "speed_nan_pct": round(100 * float((~valid).mean()), 2),   # 첫 프레임·세그먼트 경계
        "speed_median_kmh": round(float(sp[valid].median()), 1) if nv else np.nan,
        "speed_p95_kmh": round(q, 1) if nv else np.nan,
        "speed_max_kmh": round(float(sp[valid].max()), 1) if nv else np.nan,
        "moving_median_kmh": round(float(moving.median()), 1) if len(moving) else np.nan,
        "stopped_pct": round(100 * int((valid & (sp < STOP_KMH)).sum()) / max(nv, 1), 1),
    }


def main() -> None:
    src = sys.argv[1] if len(sys.argv) > 1 else "data/interim"
    out = sys.argv[2] if len(sys.argv) > 2 else "data/processed"
    os.makedirs(out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src, "*", "*.csv")))
    print(f"세션 {len(files)}개 속도 재계산 시작", flush=True)

    usecols = ["Vehicle_ID", "Local_Time", "Local_X", "Local_Y"]
    rows = []
    for i, f in enumerate(files, 1):
        df = pd.read_csv(f, usecols=usecols, low_memory=False)
        df = add_kinematics(df, smooth=False)   # 요약엔 평활 불필요 → 빠르게
        rows.append(summarize(df, os.path.basename(f)[:-4]))
        if i % 100 == 0 or i == len(files):
            print(f"  {i}/{len(files)}", flush=True)

    s = pd.DataFrame(rows)
    s.to_csv(os.path.join(out, "speed_summary.csv"), index=False, encoding="utf-8-sig")
    print("\n=== 전체 요약 ===")
    print(f"세션당 속도 결측률(첫프레임·경계): 중앙 {s.speed_nan_pct.median():.1f}%")
    print(f"이동 속도 중앙(km/h): 중앙 {s.moving_median_kmh.median():.1f}, "
          f"범위 {s.moving_median_kmh.min():.0f}~{s.moving_median_kmh.max():.0f}")
    print(f"정지 프레임 비율: 중앙 {s.stopped_pct.median():.1f}%")
    print(f"저장: {out}/speed_summary.csv")


if __name__ == "__main__":
    main()