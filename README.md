# 다수 교차로에서 TTC·PET 임계값의 전이 가능성 분석

인천 송도 20개 교차로의 드론 차량궤적(Songdo Traffic)으로, **한 곳에서 정한 상충 판정 임계값을 다른 교차로와 다른 날짜에 가져다 써도 같은 판정을 만드는지**를 검증한다. 나아가 임계값이 가려낸 위험 교차로가 실제 사고가 많았던 교차로와 일치하는지를 사고이력 자료(TAAS)로 확인한다.

- [연구계획서](연구계획_교통상충_TTC_PET_임계값_전이성.md) — 주제·문제제기·연구질문·목표·가설·선행연구
- [연구방법·데이터 상세](연구방법_데이터_상세.md) — 산출 방법·검증 설계·**가설 판정 기준**·착수 전 확인
- [메인 논문 방법론 정리](references/methodology/) — 논문별 방법론과 수식
- 풀페이퍼 초안 목표: 2026-07-24

## 검증 두 층
- **일관성** — 여러 교차로에서 정한 임계값을 남겨둔 교차로·날짜에 적용해도 판정이 유지되는가 (RQ1~RQ5, 궤적 자료)
- **타당성** — 임계값이 가려낸 위험 교차로가 사고가 많았던 교차로와 일치하는가 (RQ6, TAAS 대조)

## 데이터
원자료는 용량 때문에 저장소에 포함하지 않는다. 아래 스크립트로 내려받으면 `data/raw/`에 저장된다.

```bash
python src/01_download_data.py data/raw
```

- **Songdo Traffic v2** (CC BY 4.0): https://zenodo.org/records/17924857 — 85개 파일 14.23GB (`sample_videos.zip`은 분석에 불필요하여 제외)
- 데이터 논문: Fonod, R., Cho, H., Yeo, H., & Geroliminis, N. (2025). *Transportation Research Part C, 178*, 105205
- **TAAS** 사고이력은 수동 조회 (2020~2024, 교차로 반경 50m 기본)

참고문헌 PDF도 저작권 때문에 저장소에서 제외한다. 서지정보는 상세 문서 8절 참조.

## 폴더 구조
```text
├─ data/                    (git 제외)
│  ├─ raw/                  Zenodo 원본 ZIP
│  ├─ interim/              압축 해제 CSV
│  └─ processed/            상충 사건테이블 등
├─ references/              (PDF는 git 제외)
│  ├─ core_papers/          메인 논문 3편 + 데이터 설명서
│  ├─ supporting/           인용용 보조 문헌
│  ├─ classics/             개념 원전
│  └─ methodology/          논문별 방법론 정리 (MD)
├─ src/                     실행 .py (파이프라인)
│  ├─ 01_download_data.py      Zenodo 다운로드
│  ├─ 02_extract.py            ZIP → CSV 압축 해제
│  ├─ 03_session_table.py      세션 세그먼트·유효 관측시간 전수 실측
│  └─ check_missing.py         컬럼별 결측 전수 스캔
├─ notebook/                탐색·시각화 .ipynb
│  └─ TAAS_accident_codex.ipynb  TAAS 사고 크롤러 (RQ6, 마지막 단계)
└─ outputs/                 그림·표
```

## 핵심 설계
- TTC는 추종 상충 전용, PET는 교차·회전 상충 전용 (신호현시 정보 부재 대응)
- 세션은 연속 관측이 아니라 호버링 구간의 묶음 — 파일 15분 중 유효 관측 3~4분, 교차로 하루당 약 35분. **노출량 분모는 실측 관측시간**
- 검증: LOIO 20-fold(공간) + forward-chaining 3회(시간) + 교차로 내 잡음 바닥 + 쌍별 380회(보조)
- 사전 지정 주분석: TTC 1.5초, 분위수 p=5%. **PET는 통용 대표값이 확인되지 않아 스윕 곡선 전체를 결과로 제시**
- 가설 판정 기준은 분석 착수 전 확정 (상세 문서 5절)
