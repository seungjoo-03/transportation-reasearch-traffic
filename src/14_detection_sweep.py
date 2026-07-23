# -*- coding: utf-8 -*-
"""탐지층 파라미터 격자 민감도 (ε × 최소 지속): 사건 정의가 결론을 좌우하는가.

06의 두 탐지층 파라미터를 격자로 흔들어 핵심 판정(임계값 범위·H3·H4)이
유지되는지 확인한다. 기본값(ε=0.1 m/s, 3샘플)은 물리 근거로 사전 지정된 값이며,
본 격자는 그 선택의 검증이지 최적값 탐색이 아니다.

  ε(접근 판정 문턱) ∈ {0.05, 0.1, 0.2} m/s × 최소 지속 ∈ {2, 3, 4}샘플 = 9조합

요령: 게이트를 가장 느슨하게(ε=0, 지속 1) 한 번만 800세션을 돌려 표본을 만들고,
9조합은 그 표본을 ddot(<-ε) 필터 후 재사건화한다 — 각 조합을 따로 돌린 것과
수학적으로 동일(다른 게이트는 불변이므로). 인공물 필터(중심거리<1m)는 표본
수준에서 적용. PET 채널은 ε·지속과 무관하므로 재계산하지 않는다.

1단계(생성, ~2-3h): 세션별 느슨한 TTC 표본 → 9조합 사건화 → 조합별 사건표 저장
2단계(판정, 수 분): 조합별 교차로 임계값(q5) 범위, 잡음바닥(B=50) 대비 LOIO
   H3 초과 곳 수, H4 Wilcoxon → detection_sweep_judgment.csv

출력: data/processed/detection_sweep/events_eps{ε}_run{r}.csv (9개),
      data/processed/stats/detection_sweep_judgment.csv
사용: python src/14_detection_sweep.py            (생성+판정)
      python src/14_detection_sweep.py judge      (판정만 재실행)
"""
import glob
import importlib.util
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("c06", os.path.join(_here, "06_conflicts.py"))
c06 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(c06)

GRID_EPS = [0.05, 0.10, 0.20]
GRID_RUN = [2, 3, 4]
OUT_DIR = "data/processed/detection_sweep"
P = 0.05
TRAIN_DATES = ["2022-10-04", "2022-10-05", "2022-10-06"]
TEST_DATE = "2022-10-07"
SEED = 20260723
B_NF = 50
USECOLS = ["Vehicle_ID", "Local_Time", "Local_X", "Local_Y"]


def eventize_fast(s: pd.DataFrame) -> pd.DataFrame:
    """벡터화 사건화: (sub,surr) 연속 kbin 구간 → run별 표본수·최소TTC."""
    s = s.sort_values(["sub", "surr", "kbin"])
    new = ((s["sub"].values != np.roll(s["sub"].values, 1))
           | (s["surr"].values != np.roll(s["surr"].values, 1))
           | (s["kbin"].values != np.roll(s["kbin"].values, 1) + 1))
    new[0] = True
    run = np.cumsum(new)
    g = pd.DataFrame({"run": run, "ttc": s["ttc"].values}).groupby("run")["ttc"]
    return pd.DataFrame({"n_samples": g.size(), "min_ttc": g.min()})


def _work(f: str) -> dict:
    """세션 하나: 느슨한 게이트 표본 → 9조합 사건 min_ttc 목록."""
    stem = os.path.basename(f)[:-4]
    date, inter, sess = stem.rsplit("_", 2)
    df = pd.read_csv(f, usecols=USECOLS, low_memory=False)
    c06.EPS_CLOSING = 0.0                       # 느슨한 기저 게이트 (ddot<0)
    d5 = c06.to_5hz(df)
    ts = c06.ttc_samples(d5)
    ts = ts[ts["dist"] >= 1.0]                  # 인공물 필터(중복검출) 표본 수준 적용
    out = {}
    for eps in GRID_EPS:
        sub = ts[ts["ddot"] < -eps]
        if sub.empty:
            for r in GRID_RUN:
                out[(eps, r)] = np.empty(0, dtype=np.float32)
            continue
        ev = eventize_fast(sub)
        ev = ev[ev["min_ttc"] <= c06.TTC_EVENT_CAP]
        for r in GRID_RUN:
            out[(eps, r)] = ev.loc[ev["n_samples"] >= r, "min_ttc"].to_numpy(dtype=np.float32)
    return {"stem": stem, "inter": inter, "date": date, "sess": sess, "events": out}


def generate():
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join("data/interim", "*", "*.csv")))
    print(f"탐지층 격자 생성: 세션 {len(files)}개, 조합 {len(GRID_EPS)*len(GRID_RUN)}개", flush=True)
    from concurrent.futures import ProcessPoolExecutor
    acc = {k: [] for k in [(e, r) for e in GRID_EPS for r in GRID_RUN]}
    with ProcessPoolExecutor(max_workers=4) as ex:
        for i, res in enumerate(ex.map(_work, files, chunksize=2), 1):
            for key, arr in res["events"].items():
                if len(arr):
                    acc[key].append(pd.DataFrame({
                        "intersection": res["inter"], "date": res["date"],
                        "session": res["sess"], "min_ttc": arr}))
            if i % 50 == 0 or i == len(files):
                print(f"  {i}/{len(files)}", flush=True)
    for (eps, r), lst in acc.items():
        df = pd.concat(lst, ignore_index=True)
        df.to_csv(os.path.join(OUT_DIR, f"events_eps{eps:.2f}_run{r}.csv"),
                  index=False, encoding="utf-8-sig")
        print(f"  eps={eps:.2f}, run={r}: {len(df):,}건 저장", flush=True)


def q_at(s, p=P):
    return s.quantile(p) if len(s) >= 20 else np.nan


def judge():
    rows = []
    rng_master = np.random.default_rng(SEED)
    for eps in GRID_EPS:
        for r in GRID_RUN:
            f = os.path.join(OUT_DIR, f"events_eps{eps:.2f}_run{r}.csv")
            d = pd.read_csv(f)
            d["sess_key"] = d["date"] + "_" + d["session"]
            q = d.groupby("intersection")["min_ttc"].apply(q_at)
            # 잡음 바닥 (반분할 B=50)
            rng = np.random.default_rng(rng_master.integers(1e9))
            nf = {}
            for inter, sub in d.groupby("intersection"):
                sess = np.asarray(sub["sess_key"].unique(), dtype=object)
                if len(sess) < 4:
                    continue
                shifts = []
                for _ in range(B_NF):
                    rng.shuffle(sess)
                    h = len(sess) // 2
                    qa = q_at(sub[sub["sess_key"].isin(sess[:h])]["min_ttc"])
                    qb = q_at(sub[sub["sess_key"].isin(sess[h:])]["min_ttc"])
                    if pd.notna(qa) and pd.notna(qb):
                        shifts.append(abs(qa - qb))
                if shifts:
                    nf[inter] = float(np.quantile(shifts, 0.95))
            # LOIO (훈련 3일 → 시험일)
            train = d[d["date"].isin(TRAIN_DATES)]
            test = d[d["date"] == TEST_DATE]
            q_tr = train.groupby("intersection")["min_ttc"].apply(q_at)
            pooled_err, local_err, exceed, n = [], [], 0, 0
            for X in q_tr.index:
                own = q_at(test.loc[test["intersection"] == X, "min_ttc"])
                if pd.isna(own) or pd.isna(q_tr[X]) or X not in nf:
                    continue
                pe = abs(q_tr.drop(index=X).median() - own)
                le = abs(q_tr[X] - own)
                pooled_err.append(pe)
                local_err.append(le)
                exceed += pe > nf[X]
                n += 1
            try:
                pval = wilcoxon(local_err, pooled_err, alternative="less").pvalue
            except ValueError:
                pval = np.nan
            rows.append({"eps": eps, "min_run": r, "n_events": len(d),
                         "q5_min": round(float(q.min()), 3), "q5_max": round(float(q.max()), 3),
                         "q5_range": round(float(q.max() - q.min()), 3),
                         "h3_exceed": f"{exceed}/{n}",
                         "h3_supported": bool(exceed > n / 2),
                         "h4_med_local": round(float(np.median(local_err)), 3),
                         "h4_med_pooled": round(float(np.median(pooled_err)), 3),
                         "h4_p": round(float(pval), 5),
                         "is_main": (eps == 0.10 and r == 3)})
    res = pd.DataFrame(rows)
    os.makedirs("data/processed/stats", exist_ok=True)
    res.to_csv("data/processed/stats/detection_sweep_judgment.csv",
               index=False, encoding="utf-8-sig")
    print("\n=== 탐지층 격자 판정 (9조합) ===")
    print(res.to_string(index=False))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "judge":
        judge()
    else:
        generate()
        judge()