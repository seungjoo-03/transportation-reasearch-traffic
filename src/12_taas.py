# -*- coding: utf-8 -*-
"""TAAS 사고이력 대조 (RQ6·H6): 상충이 가려낸 위험 교차로가 실제 사고와 일치하는가.

입력: notebook/taas_output/ 의 크롤링 CSV (송도동 2020~2024, 전 심각도, 1,202건)
절차:
  ① 교차로 중심 좌표 — 각 교차로 궤적(Local_X/Y, EPSG:5186)의 중앙값
  ② TAAS 좌표(EPSG:5179) → EPSG:5186 변환 → 미터 단위 거리 계산
  ③ 반경 매칭 — 기본 50m (사전지정), 민감도 30·100m. 최근접 교차로에만 배정
     (최근접 교차로 간 거리 중앙값 333m → 이중 배정 불가)
  ④ 교차로별 사고 수 — 기본: 사망+중상(5년 안정: 72/55/57/63/64), 민감도: 전체
  ⑤ H6 판정 — 상충 순위(고정 1.5s 상충률·통합 q5 상충률·PET) vs 사고 순위
     Spearman·Kendall. 사전 규칙: 교차로별 사고 중앙값 < 3건이면 상·중·하
     등급(7/6/7) 일치도로 전환(계획서 §5).
  ⑥ 검증 그림 — 사고~최근접 교차로 거리 분포(컷이 골짜기에 있는지)

출력: data/processed/taas/ (intersection_crashes.csv, h6_tests.csv, taas_matched.csv)
그림: outputs/taas/ (검증_거리분포, 분포_연도별사고, 산점_상충vs사고)
사용: python src/12_taas.py
"""
import glob
import os

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from pyproj import Transformer
from scipy.stats import spearmanr, kendalltau

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

TAAS_CSV = "notebook/taas_output/taas_accidents_20200101T000000_20241231T235959_dong2818510600.csv"
RADIUS_MAIN = 50.0                  # m — 사전지정 (계획서 RQ6)
RADII = [30.0, 50.0, 100.0]         # 민감도
SEVERE = ["사망사고", "중상사고"]     # 기본 심각도 컷 (사전지정)


def intersection_centers() -> pd.DataFrame:
    """교차로별 중심 = 궤적 Local_X/Y(EPSG:5186)의 중앙값 (교차로당 세션 1개면 충분)."""
    rows = []
    seen = set()
    for folder in sorted(glob.glob("data/interim/2022-10-04_*")):
        inter = os.path.basename(folder).rsplit("_", 1)[-1]
        if inter in seen:
            continue
        seen.add(inter)
        f = sorted(glob.glob(os.path.join(folder, "*.csv")))[0]
        d = pd.read_csv(f, usecols=["Local_X", "Local_Y"], low_memory=False)
        rows.append({"intersection": inter, "cx": d["Local_X"].median(), "cy": d["Local_Y"].median()})
    return pd.DataFrame(rows)


def match_crashes(taas: pd.DataFrame, centers: pd.DataFrame) -> pd.DataFrame:
    """TAAS 좌표를 5186으로 변환해 최근접 교차로와 거리 계산."""
    tr = Transformer.from_crs("EPSG:5179", "EPSG:5186", always_xy=True)
    x, y = tr.transform(taas["x_crdnt"].values, taas["y_crdnt"].values)
    taas = taas.copy()
    taas["x86"], taas["y86"] = x, y
    cx = centers["cx"].values[None, :]
    cy = centers["cy"].values[None, :]
    dist = np.hypot(taas["x86"].values[:, None] - cx, taas["y86"].values[:, None] - cy)
    ni = dist.argmin(axis=1)
    taas["nearest"] = centers["intersection"].values[ni]
    taas["dist_m"] = dist.min(axis=1)
    return taas


def crash_counts(matched: pd.DataFrame, centers: pd.DataFrame) -> pd.DataFrame:
    """교차로별 사고 수 — 반경·심각도 조합별."""
    rows = []
    for inter in centers["intersection"]:
        r = {"intersection": inter}
        for rad in RADII:
            sub = matched[(matched["nearest"] == inter) & (matched["dist_m"] <= rad)]
            r[f"all_{int(rad)}m"] = len(sub)
            r[f"severe_{int(rad)}m"] = int(sub["acdnt_gae_dc"].isin(SEVERE).sum())
        rows.append(r)
    return pd.DataFrame(rows)


def conflict_rankings() -> pd.DataFrame:
    """상충 기반 위험 순위 재료: 고정 1.5s 상충률, 통합 q5 상충률(스윕 표 보간)."""
    rate = pd.read_csv("data/processed/transfer/sweep_rate_ttc.csv", index_col=0)
    rate.columns = [float(c) for c in rate.columns]
    thr = pd.read_csv("data/processed/thresholds/thresholds.csv")
    pooled_q5 = thr["ttc_q5"].median()                      # 통합(20곳 중앙값) 임계값
    near = min(rate.columns, key=lambda c: abs(c - pooled_q5))
    out = pd.DataFrame({"intersection": rate.index,
                        "rate_1.5s": rate[1.5].values,
                        f"rate_q5({near:.1f}s)": rate[near].values})
    return out, pooled_q5, near


def h6_tests(cc: pd.DataFrame, rank_df: pd.DataFrame) -> pd.DataFrame:
    """상충 순위 vs 사고 수 — Spearman·Kendall (+등급 전환 규칙 판정)."""
    m = cc.merge(rank_df, on="intersection")
    rows = []
    crash_cols = [f"{sev}_{int(rad)}m" for sev in ("severe", "all") for rad in RADII]
    for crash_col in crash_cols:
        med = m[crash_col].median()
        grade_mode = med < 3                                 # 사전 규칙: 중앙값<3이면 등급 전환
        for conf_col in [c for c in rank_df.columns if c != "intersection"]:
            rho, p_s = spearmanr(m[conf_col], m[crash_col])
            tau, p_k = kendalltau(m[conf_col], m[crash_col])
            rows.append({"crash": crash_col, "conflict": conf_col,
                         "n": len(m), "crash_median": med, "grade_mode": grade_mode,
                         "spearman": round(rho, 3), "p_spearman": round(p_s, 4),
                         "kendall": round(tau, 3), "p_kendall": round(p_k, 4)})
    return pd.DataFrame(rows), m


def grade_split(s: pd.Series) -> pd.Series:
    """값 내림차순으로 상(7)/중(6)/하(7) 등급 부여 (사전 규칙 7/6/7).
    동점은 평균 순위로 처리해 경계 동점의 자의성을 줄인다."""
    rk = s.rank(ascending=False, method="average")
    return pd.cut(rk, bins=[0, 7.5, 13.5, 20.5], labels=["상", "중", "하"])


def grade_agreement(cc: pd.DataFrame, rank_df: pd.DataFrame) -> pd.DataFrame:
    """사망+중상 희소 시(중앙값<3) 사전 규칙: 등급 일치도 분석."""
    m = cc.merge(rank_df, on="intersection")
    crash_col = f"severe_{int(RADIUS_MAIN)}m"
    rows = []
    for conf_col in [c for c in rank_df.columns if c != "intersection"]:
        g_conf = grade_split(m[conf_col])
        g_crash = grade_split(m[crash_col])
        exact = (g_conf == g_crash).mean()
        order = {"상": 0, "중": 1, "하": 2}
        diff = (g_conf.map(order).astype(float) - g_crash.map(order).astype(float)).abs()
        adjacent = (diff <= 1).mean()                       # 한 등급 이내 일치
        opposite = int(((g_conf == "상") & (g_crash == "하")).sum()
                       + ((g_conf == "하") & (g_crash == "상")).sum())
        rows.append({"conflict": conf_col, "crash": crash_col,
                     "exact_agree": round(exact, 3), "adjacent_agree": round(adjacent, 3),
                     "opposite_n": opposite,
                     "chance_exact": round((7/20)**2*2 + (6/20)**2, 3)})   # 무작위 기대 일치율
    return pd.DataFrame(rows)


def plots(taas_m, cc, m, outdir="outputs/taas"):
    os.makedirs(outdir, exist_ok=True)
    # 검증: 사고~최근접 교차로 거리 분포 (컷 골짜기 확인)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.hist(taas_m["dist_m"].clip(upper=500), bins=50, color="#4C78A8", edgecolor="white")
    for rad, ls in ((30, ":"), (50, "--"), (100, ":")):
        ax.axvline(rad, color="crimson", ls=ls, lw=1.2, label=f"{rad}m")
    ax.set_xlabel("사고 지점 ~ 최근접 교차로 중심 거리 (m, 500 초과는 500에 표시)")
    ax.set_ylabel("사고 수")
    ax.set_title("검증: 사고-교차로 거리 분포와 매칭 반경")
    ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "검증_거리분포.png"), dpi=120); plt.close(fig)
    # 연도별 심각도 추이
    ct = pd.crosstab(taas_m["acdnt_year"], taas_m["acdnt_gae_dc"])
    fig, ax = plt.subplots(figsize=(8, 4))
    bottom = np.zeros(len(ct))
    for col, c in (("사망사고", "#B22222"), ("중상사고", "#E45756"),
                   ("경상사고", "#F5B041"), ("부상신고사고", "#cccccc")):
        if col in ct:
            ax.bar(ct.index.astype(str), ct[col], bottom=bottom, color=c, label=col)
            bottom += ct[col].values
    ax.set_ylabel("사고 수"); ax.set_title("송도동 연도별 사고 (2020~2024, TAAS)")
    ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "분포_연도별사고.png"), dpi=120); plt.close(fig)
    # 상충 vs 사고 산점
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    xcol = [c for c in m.columns if c.startswith("rate_1.5")][0]
    ycol = f"severe_{int(RADIUS_MAIN)}m"
    ax.scatter(m[xcol], m[ycol], s=45, color="#4C78A8")
    for _, r in m.iterrows():
        ax.annotate(r["intersection"], (r[xcol], r[ycol]), fontsize=8,
                    xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("TTC<1.5s 상충률 (건/시간)")
    ax.set_ylabel(f"사망+중상 사고 수 (반경 {int(RADIUS_MAIN)}m, 5년)")
    ax.set_title("상충률 vs 사고이력 (교차로 20곳)")
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "산점_상충vs사고.png"), dpi=120); plt.close(fig)


def main():
    out = "data/processed/taas"
    os.makedirs(out, exist_ok=True)
    taas = pd.read_csv(TAAS_CSV, low_memory=False)
    centers = intersection_centers()
    print(f"TAAS {len(taas):,}건, 교차로 {len(centers)}곳")

    matched = match_crashes(taas, centers)
    matched.to_csv(os.path.join(out, "taas_matched.csv"), index=False, encoding="utf-8-sig")
    for rad in RADII:
        inb = (matched["dist_m"] <= rad).sum()
        print(f"  반경 {int(rad)}m 안 사고: {inb}건 ({inb/len(matched)*100:.1f}%)")

    cc = crash_counts(matched, centers)
    cc.to_csv(os.path.join(out, "intersection_crashes.csv"), index=False, encoding="utf-8-sig")
    print("\n=== 교차로별 사고 수 (기본: 사망+중상, 반경 50m) ===")
    print(cc[["intersection", f"severe_{int(RADIUS_MAIN)}m", f"all_{int(RADIUS_MAIN)}m"]]
          .sort_values(f"severe_{int(RADIUS_MAIN)}m", ascending=False).to_string(index=False))

    rank_df, pooled_q5, near = conflict_rankings()
    print(f"\n통합 q5 임계값: {pooled_q5:.3f}s (스윕 표 최근접 {near:.1f}s 사용)")
    tests, m = h6_tests(cc, rank_df)
    tests.to_csv(os.path.join(out, "h6_tests.csv"), index=False, encoding="utf-8-sig")
    print("\n=== H6 판정 (상충 순위 vs 사고 수) ===")
    print(tests.to_string(index=False))

    ga = grade_agreement(cc, rank_df)
    ga.to_csv(os.path.join(out, "h6_grades.csv"), index=False, encoding="utf-8-sig")
    print("\n=== H6 등급 분석 (사망+중상 희소 → 사전 규칙 상/중/하 7:6:7) ===")
    print(ga.to_string(index=False))

    plots(matched, cc, m)
    print(f"\n저장: {out}/, 그림: outputs/taas/")


if __name__ == "__main__":
    matplotlib.use("Agg")
    main()