# TTC 1.5초 임계값의 출처 (검증 완료)

문헌 워크플로우(13개 에이전트, 원문 인용·반증 검증)로 확인. 서론 §2 근거.

## 한 줄
1.5초는 van der Horst(1990)가 **교차로 접근부에서 실제 관측한 임계 TTC** → Gettman & Head(FHWA-RD-03-050, 2003)가 상충 판정 컷오프로 인용·정당화 → **SSAM 소프트웨어(2008)가 기본값(최대 TTC=1.5초, PET=5초)으로 하드코딩**해 무료 배포하면서 전 세계가 상속. **합의된 표준이 아니라 최빈·관례값.**

## 검증된 경로 (원문 확인, 확실도 높음)
1. **기원** — van der Horst 1990(Delft 박사논문): 교차로 접근부 임계 TTC ≈1.5초 (저속이라 낮음)
2. **채택** — FHWA-RD-03-050 Ch.7 알고리즘: `If TTC < TTC_upper_limit (user-determined, e.g., 1.5 s), keep event`. 정당화 근거는 **사고 데이터가 아니라 행동관측**(AICC 차량추종 실험 + van der Horst).
   - https://www.fhwa.dot.gov/publications/research/safety/03050/07.cfm
   - https://ntlrepository.blob.core.windows.net/lib/38000/38000/38015/FHWA-RD-03-050.pdf (각주 9, 참고문헌 85)
3. **편재화** — SSAM 사용자매뉴얼(FHWA-HRT-08-050, 2008): 기본 최대 TTC=1.5초, PET=5초.
   - https://www.fhwa.dot.gov/publications/research/safety/08050/08050.pdf
   - 2차 확인: https://www.diva-portal.org/smash/get/diva2:926089/FULLTEXT01.pdf

## 반드시 지킬 서술 (검증에서 걸러진 것 — 쓰면 반증당함)
- ✗ "근거 없는 임의값" → **반증됨.** Gettman & Head가 관측치로 정당화함(사고데이터가 아닐 뿐). 세부 심각도 구간(0.5/1.0초)만 명시 근거 부재.
- ✗ "운전자 반응시간에서 나온 값" → 부정확. SSAM 논거는 "교차로 저속". 반응시간 계보는 Hayward(1972).
- ✗ "스웨덴/Hydén 전통이 1.5초 TTC 표준을 만듦" → 부정확. 스웨덴 상충기법(TCT)은 TA+CS 사용. "1.5"라는 숫자는 Hydén(1977) TA<1.5초로 먼저 존재했으나 그건 **TA지 TTC 아님**.
- ✓ **정확한 서술**: "특정 맥락(교차로 저속·차-차)의 관측값이 소프트웨어 기본값을 통해 맥락 불문 상속된다. 후속연구가 자기 맥락 적합성을 재검증하지 않는 경우가 흔하다(Arun 2021)."

## 후속연구: 복사 vs 재도출 (혼재 — 우리는 재도출 진영)
- **복사(재정당화 없음)**: 미국 NJ Glassboro(Jalayer 2022), 크로아티아 Rijeka 회전(Klobučar 2025), 한국 합류부(Woo 2025), 이탈리아 회전(Tesoriere 2018)
- **재도출(맥락 조정)**: 미국 보행자 2.7초(Wu/Radwan), 인도 Bhopal 1.15초, 중국 상하이 0.97/1.51/2.09초, 이라크 Hilla 1.5~1.8초
- **리뷰**: Arun 2021(AAP 153:106016, 549편) — *"often chosen arbitrarily ... without justification for their suitability for the context"*, 한 좁은 맥락(신호교차로 후미추돌)에서도 TTC **0.5~6.0초**. Johnsson 2018(Transport Reviews) — 임계값이 *"chosen based on the observation of cars"*, van der Horst 1991 귀속. 문헌 명시: **"no standard."**

## 원문 미확보 — 나중에 확보 (서론 인용 시 필요)
- **van der Horst 1990 박사논문** — 실측 최소 TTC ≈1.1초 수치 **미검증**(접근 실패). 인용 시 주의.
- Arun 2021 AAP — 오픈액세스: https://eprints.qut.edu.au/209080/1/76392506.pdf
- Johnsson 2018 Transport Reviews / Gettman & Head 2003(위 URL로 확보 가능)
- 해외 사례논문들(위 목록) — 서론 "복사 vs 재도출" 대비용 인용 후보

## 우리 연구와의 연결
1.5초를 도구 세팅대로 받지 않고 궤적 데이터로 곳마다 재도출 → "한 곳 값이 다른 곳에서도 판정을 유지하나(맥락 상속 가정)"를 검증. 이 검증이 §2 문제의식의 핵심.