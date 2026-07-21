# -*- coding: utf-8 -*-
"""이동류 분류 + 정지차량 표시 (전처리 2단계).

각 차량이 어느 접근로로 진입해 어느 접근로로 진출했는지로 이동류를 나눈다.
- 진입 접근로 ≠ 진출 접근로 → 직진(반대편)·좌회전·우회전(옆)
- 진입 = 진출 접근로 → 접근로 내 (진입 전 유턴·부분궤적·대기 — 교차로 통과 아님)
- Road_Section 없음 → 미분류
접근로 방향은 segmentation 폴리곤(차로 구획)의 접근로별 중심 각도로 판정한다.
위치 이동폭(span)이 5m 미만이면 정지(주차)차량으로 표시한다.

  load_approaches(inter): 교차로의 접근로 각도 dict + segmentation 반환
  movement_table(df, ang): 세션 df → 차량별 [entry,exit,movement,parked]. 06이 재사용.
  main(): 800개 적용 → data/processed/movement_summary.csv + outputs/movement/ 그림

사용: python src/05_movement.py [입력=data/interim] [출력=data/processed]
      python src/05_movement.py plots   (그림만 재생성)
"""
import glob
import os
import sys

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

SEG_DIR = "data/segmentations"
PARK_SPAN_M = 5.0                                  # 위치 이동폭 이 미만 → 정지(주차)
MOVES = ["직진", "좌회전", "우회전", "접근로내", "미분류"]
COLORS = {"직진": "#4C78A8", "좌회전": "#E45756", "우회전": "#54A24B", "접근로내": "#F58518", "미분류": "#dddddd"}


def load_approaches(inter, seg_dir=SEG_DIR):
    """교차로 inter의 segmentation → 접근로(N)별 중심각도 dict, seg DataFrame."""
    seg = pd.read_csv(os.path.join(seg_dir, f"{inter}.csv"))
    seg["N"] = seg["Section"].str.split("_").str[0].astype(int)
    seg["cx"] = seg[["tlx", "blx", "brx", "trx"]].mean(axis=1)
    seg["cy"] = seg[["tly", "bly", "bry", "try"]].mean(axis=1)
    c = seg.groupby("N")[["cx", "cy"]].mean()
    cx0, cy0 = c["cx"].mean(), c["cy"].mean()
    ang = {int(n): float(np.degrees(np.arctan2(r["cy"] - cy0, r["cx"] - cx0))) for n, r in c.iterrows()}
    return ang, seg


def classify(entry, exit_, ang):
    """진입·진출 접근로 → 이동류. 접근로 방향차로 직진(반대)/좌·우(옆) 판정."""
    if entry is None or exit_ is None or entry not in ang or exit_ not in ang:
        return "미분류"
    if entry == exit_:
        return "접근로내"                          # 진입 전 유턴·부분궤적·대기
    d = (ang[exit_] - ang[entry] + 180) % 360 - 180
    if abs(d) > 135:
        return "직진"
    return "좌회전" if d > 0 else "우회전"


def movement_table(df, ang):
    """세션 df → 차량별 DataFrame [entry, exit, span_m, parked, movement]."""
    df = df.copy()
    df["t"] = pd.to_timedelta(df["Local_Time"]).dt.total_seconds()
    df["N"] = pd.to_numeric(df["Road_Section"].str.split("_").str[0], errors="coerce")
    df = df.sort_values(["Vehicle_ID", "t"])
    dd = df.dropna(subset=["N"])
    entry = dd.groupby("Vehicle_ID")["N"].first()
    exit_ = dd.groupby("Vehicle_ID")["N"].last()
    agg = df.groupby("Vehicle_ID").agg(xmin=("Local_X", "min"), xmax=("Local_X", "max"),
                                       ymin=("Local_Y", "min"), ymax=("Local_Y", "max"))
    out = pd.DataFrame(index=agg.index)
    out["entry"] = entry.reindex(agg.index)
    out["exit"] = exit_.reindex(agg.index)
    out["span_m"] = np.hypot(agg["xmax"] - agg["xmin"], agg["ymax"] - agg["ymin"])
    out["parked"] = out["span_m"] < PARK_SPAN_M
    out["movement"] = [classify(int(e) if pd.notna(e) else None, int(x) if pd.notna(x) else None, ang)
                       for e, x in zip(out["entry"], out["exit"])]
    return out


def plot_validation(inter="A", session="data/interim/2022-10-04_A/2022-10-04_A_AM1.csv",
                    outdir="outputs/movement"):
    """한 교차로에서 궤적을 이동류 색으로, segmentation 폴리곤 위에 겹쳐 검증."""
    os.makedirs(outdir, exist_ok=True)
    ang, seg = load_approaches(inter)
    df = pd.read_csv(session, usecols=["Vehicle_ID", "Local_Time", "Ortho_X", "Ortho_Y",
                                       "Local_X", "Local_Y", "Road_Section"])
    mt = movement_table(df, ang)
    fig, ax = plt.subplots(figsize=(9, 9))
    for _, r in seg.iterrows():
        poly = [(r["tlx"], r["tly"]), (r["blx"], r["bly"]), (r["brx"], r["bry"]), (r["trx"], r["try"]), (r["tlx"], r["tly"])]
        ax.plot(*zip(*poly), color="#bbbbbb", lw=0.7)
    for vid, g in df.groupby("Vehicle_ID"):
        ax.plot(g["Ortho_X"], g["Ortho_Y"], color=COLORS.get(mt.loc[vid, "movement"], "#ccc"), lw=0.4, alpha=0.5)
    ax.set_aspect("equal"); ax.invert_yaxis()
    ax.set_title(f"교차로 {inter} 이동류 분류 (통과=직/좌/우, 나머지=접근로내)")
    ax.legend([Line2D([0], [0], color=c, lw=3) for c in COLORS.values()], list(COLORS.keys()), loc="upper right")
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "검증_이동류분류.png"), dpi=120); plt.close(fig)


def plot_summary(s, outdir="outputs/movement"):
    """이동류 구성 그림 2장."""
    os.makedirs(outdir, exist_ok=True)
    tot = s[MOVES].sum()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(MOVES, tot.values, color=[COLORS[m] for m in MOVES])
    ax.set_ylabel("차량 수 (전 세션 합)")
    ax.set_title("이동류 구성 (800개 세션 합)")
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "분포_이동류구성.png"), dpi=120); plt.close(fig)

    by = s.groupby("intersection")[["직진", "좌회전", "우회전"]].sum()
    by = by.div(by.sum(axis=1), axis=0) * 100
    fig, ax = plt.subplots(figsize=(11, 4))
    bottom = np.zeros(len(by))
    for m in ["직진", "좌회전", "우회전"]:
        ax.bar(by.index, by[m], bottom=bottom, color=COLORS[m], label=m)
        bottom += by[m].values
    ax.set_ylabel("통과 이동류 비율 (%)"); ax.set_title("교차로별 통과 이동류 구성")
    ax.legend(loc="upper right")
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "분포_교차로별이동류.png"), dpi=120); plt.close(fig)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "data/interim"
    out = sys.argv[2] if len(sys.argv) > 2 else "data/processed"
    os.makedirs(out, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src, "*", "*.csv")))
    print(f"세션 {len(files)}개 이동류 분류 시작", flush=True)
    appr_cache, rows = {}, []
    for i, f in enumerate(files, 1):
        inter = os.path.basename(f)[:-4].rsplit("_", 2)[1]
        if inter not in appr_cache:
            appr_cache[inter] = load_approaches(inter)[0]
        df = pd.read_csv(f, usecols=["Vehicle_ID", "Local_Time", "Local_X", "Local_Y", "Road_Section"], low_memory=False)
        mt = movement_table(df, appr_cache[inter])
        vc = mt["movement"].value_counts()
        row = {"file": os.path.basename(f)[:-4], "intersection": inter,
               "vehicles": len(mt), "parked": int(mt["parked"].sum())}
        row.update({m: int(vc.get(m, 0)) for m in MOVES})
        rows.append(row)
        if i % 100 == 0 or i == len(files):
            print(f"  {i}/{len(files)}", flush=True)
    s = pd.DataFrame(rows)
    s.to_csv(os.path.join(out, "movement_summary.csv"), index=False, encoding="utf-8-sig")
    print("\n=== 전체 이동류 (합) ===")
    print(f"직진 {s['직진'].sum():,} / 좌회전 {s['좌회전'].sum():,} / 우회전 {s['우회전'].sum():,} / "
          f"접근로내 {s['접근로내'].sum():,} / 미분류 {s['미분류'].sum():,}")
    print(f"정지(주차) 차량: {s['parked'].sum():,}")
    print(f"저장: {out}/movement_summary.csv")
    plot_summary(s)
    plot_validation()
    print("그림 저장: outputs/movement/")


if __name__ == "__main__":
    matplotlib.use("Agg")
    if len(sys.argv) > 1 and sys.argv[1] == "plots":
        s = pd.read_csv("data/processed/movement_summary.csv")
        plot_summary(s)
        plot_validation()
        print("그림 저장: outputs/movement/")
    else:
        main()