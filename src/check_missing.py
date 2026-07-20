# -*- coding: utf-8 -*-
"""컬럼별 결측을 20개 교차로 800개 CSV 전수로 스캔한다.

질문: 결측이 Vehicle_Speed·Road_Section에만 있나? 모든 파일인가 특정 파일인가?
컬럼마다 (a) 전체 결측률(가중), (b) 파일별 결측률의 최소/중앙/최대,
(c) 결측이 하나라도 있는 파일 수, (d) 전부 결측인 파일 수를 낸다.

출력 (data/processed/):
  missing_by_column.csv  컬럼 17개 한 줄씩 (요약)
  missing_by_file.csv    파일 800개 × 컬럼별 결측률

사용: python src/check_missing.py [입력=data/interim] [출력=data/processed]
"""
import glob
import os
import sys

import numpy as np
import pandas as pd


def main() -> None:
    src = sys.argv[1] if len(sys.argv) > 1 else "data/interim"
    out = sys.argv[2] if len(sys.argv) > 2 else "data/processed"
    os.makedirs(out, exist_ok=True)

    files = sorted(glob.glob(os.path.join(src, "*", "*.csv")))
    print(f"CSV {len(files)}개 결측 스캔 시작", flush=True)

    per_file = []       # 파일별 결측률 (컬럼별)
    null_sum = None     # 컬럼별 결측 셀 수 누적
    rows_sum = 0        # 전체 행 수 누적

    for i, f in enumerate(files, 1):
        df = pd.read_csv(f, low_memory=False)
        n = len(df)
        nulls = df.isna().sum()                 # 컬럼별 결측 셀 수
        rate = (nulls / n) if n else nulls * 0.0

        rec = {"file": os.path.basename(f)[:-4], "rows": n}
        rec.update({c: round(float(rate[c]), 6) for c in df.columns})
        per_file.append(rec)

        null_sum = nulls if null_sum is None else null_sum.add(nulls, fill_value=0)
        rows_sum += n
        if i % 100 == 0 or i == len(files):
            print(f"  {i}/{len(files)}", flush=True)

    fdf = pd.DataFrame(per_file)
    fdf.to_csv(os.path.join(out, "missing_by_file.csv"), index=False, encoding="utf-8-sig")

    cols = [c for c in fdf.columns if c not in ("file", "rows")]
    summary = []
    for c in cols:
        s = fdf[c].fillna(0.0)               # 그 파일에 컬럼이 없으면 0 취급
        summary.append({
            "column": c,
            "overall_null_pct": round(100 * float(null_sum[c]) / rows_sum, 2),
            "file_min_pct": round(100 * float(s.min()), 2),
            "file_median_pct": round(100 * float(s.median()), 2),
            "file_max_pct": round(100 * float(s.max()), 2),
            "n_files_any_null": int((s > 0).sum()),
            "n_files_all_null": int((s >= 0.999999).sum()),
        })
    sdf = pd.DataFrame(summary).sort_values("overall_null_pct", ascending=False)
    sdf.to_csv(os.path.join(out, "missing_by_column.csv"), index=False, encoding="utf-8-sig")

    print("\n=== 컬럼별 결측 요약 (전체 결측률 내림차순) ===")
    print(sdf.to_string(index=False))
    print(f"\n총 행 수: {rows_sum:,}")
    print(f"저장: {out}/missing_by_column.csv, {out}/missing_by_file.csv")


if __name__ == "__main__":
    main()