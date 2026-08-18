# 프로젝트 배경 (새 세션 시작 시 필독)

이 폴더는 기존 "교통 관련 논문 작성" 폴더(TTC·PET 임계값 전이 가능성 분석)에서 **주제를 갈아엎고** 새로 시작하는 작업 폴더다. 사용자는 교통공학 전공 학부생, 첫 논문 준비 중.

## 지금까지의 경위

1. 원래 주제: "드론 궤적자료를 활용한 교차로 간 교통상충 임계값(TTC·PET)의 전이 가능성 분석" — 지도교수 미팅에서 진행.
2. **지도교수 피드백(미팅에서 전달받은 내용)**:
   - "전이 가능성" 주제는 힘들 것 같다 → 접기로 함
     - 이유(이미 검증됨): 유일한 직접 선례인 Arun et al.(2022, AAP)은 GPD 극값모형의 보정 파라미터(u)를 전이시킨 것으로, 이 연구가 쓰려던 "분위수 기반 조작적 임계값(하위 5%)"과 통계적 성격이 다름. Arun 2022는 후미추돌·TTC/MTTC 계열만 다루고 PET/횡단상충은 전혀 다루지 않음(PET 쪽은 전이 검증 선례가 사실상 없음). Arun 2022의 전이 검증도 2개 지점에서 "사고예측모형의 정확도" 수준에 그침.
   - 다만 **송도 드론 데이터셋 자체는 매우 좋은 데이터**이니 그대로 유지
   - **새 주제 도출 방법**: 송도 데이터셋을 만든 원 논문(Fonod et al. 2025)을 인용한 논문들을 전부 찾아서, 각 논문이 "무슨 연구를 했는지" 표로 정리 → 그 안에서 기존연구의 한계·부족한 점 또는 창의적으로 뽑아낼 수 있는 아이디어를 도출 → 새 주제로 잡아서 좋은 데이터(송도, 가능하면 다른 도시 데이터도)에 적용해 검증 → 확정되면 컨퍼밍(교수님 확인)
3. 이 과정에서 겸사겸사 확인한 것: 지도교수가 "교통상충기법(TCT)이 학생이 지어낸 용어 같다"고 지적했던 건에 대해서도 조사함 — 결론: TCT(Traffic Conflict Technique)는 1968년 Perkins & Harris(GM연구소)가 처음 정식화한 실존 용어이며, "교통상충기법"도 한국 교통공학계(대한교통학회지, 1999년 이수범·강인숙부터)에서 반복 사용된 실존 번역어. 다만 이 연구가 실제로 다루는 내용(TTC·PET 임계값 기반 자동판정)은 TCT의 역사적 원형(사람이 현장관측)보다는 SSM(Surrogate Safety Measures)에 더 정확히 대응함. **이건 부차적 확인사항이고 새 주제 도출과는 별개.**

## 원 논문 (모든 조사의 출발점)

**Fonod, R., Cho, H., Yeo, H., & Geroliminis, N. (2025).** "Advanced computer vision for extracting georeferenced vehicle trajectories from drone imagery." *Transportation Research Part C: Emerging Technologies*, vol.178, 105205. (arXiv:2411.02136)

- 저자: Robert Fonod, Nikolas Geroliminis — EPFL(스위스 로잔) Urban Transport Systems Lab / Haechan Cho(조해찬), Hwasoo Yeo(여화수) — KAIST(한국)
- 2022년 10월 4~7일 KAIST-EPFL 공동으로 송도국제업무지구에서 드론 10대로 20개 교차로 촬영(4K, 29.97fps, 고도 140~150m, 총 12TB)
- 자체 개발 CV 프레임워크 **"Geo-trax"**(앵커프리 YOLOv8 탐지 + BoT-SORT 추적 + 트랙기반 안정화 + 정사영상 기반 지리참조)를 이 실험에 적용·검증(계측 프로브 차량 센서데이터와 대조)
- 산출물: **Songdo Traffic**(궤적 약 70만 개, `data/raw/`에 원본 보관) + **Songdo Vision**(라벨링 이미지 약 30만 개 인스턴스) 데이터셋 공개
- "방법론 제안 + 송도실험으로 검증 + 데이터셋 공개"를 한 논문이 다 함 — 다른 데이터로 방법론만 만들고 나중에 남이 송도에 적용한 게 아님

파일 위치: `references/원논문_Fonod2025/04_Fonod_2025_송도데이터셋_arXiv.pdf`

## 이 원 논문을 인용한 45편(고유 43편 — 2026-08-13 확정, 중복 2쌍은 아래 PDF현황표 참고) 조사 결과 — 카테고리별

*"송도 데이터를 썼는가"는 부차적 정보일 뿐, 핵심은 "각 논문이 무슨 연구를 했는가"임(이 프레임으로 봐야 함 — 처음엔 "송도 미사용"을 필터처럼 잘못 취급했다가 정정함).*

**① 상충/안전(TTC·PET·DGT 지표 계산) — 2편**
- Espadaler-Clapés/Fonod/Barmpounakis/Geroliminis (2025, TR Part C, "TRIP") — 맨체스터 2개 교차로, TTC·PET 기반 안전-혼잡 모니터링 프레임워크. 파일: `references/TRIP_Espadaler2025/`
- Chen/Wu/Zheng 외 — FLUID (2025 arXiv / 2026 Scientific Data, 동일논문 버전차이) — 중국 쉬안청, TTC+자체정의 DGT(PET유사)지표, 임계값 TTC≤2.0s/DGT≤4.0s. Songdo Vision을 자기 탐지기 학습에만 활용.

**② 교통류/상태 예측 — 3편**
- Xiong/Fonod/Alahi/Geroliminis (2025, IEEE T-ITS) — HiMSNet, 드론+루프검지기 융합예측. 실제 드론데이터 아닌 자체 시뮬레이션(SimBarca, 바르셀로나) 사용.
- Xiong/Fonod/Geroliminis (2026) — 확률적예측(GMM), SimBarca+METR-LA/PEMS-Bay.
- Liu/Jin/Choi (2026, TR Part C) — PMA-Diffusion, 희소관측 기반 고속도로 교통상태추정.

**③ 차량 탐지·인식·재식별 기술 — 5편**
- Bi/Li/Zheng 외 (2025, Remote Sensing) — SPDC-YOLO, 드론이미지 소형객체탐지(교통안전 응용 포함)
- Zhang/Wang 외 (2025, Sensors) — DSCW-YOLO, 저고도 UAV 차량탐지
- Ye/Kyrkou (2026, IEEE T-ITS) — UAV 기반 차량탐지 리뷰
- **Tak/Fonod/Geroliminis (2026, Comm. Transportation) — 차량 재식별(ReID). 실제 송도데이터 사용 확인됨(10드론/20교차로). 외형특징+충격파이론 기반 이동시간모델 결합. mAP 0.949 vs 기존 0.769(36.8%개선).**
- Fan/Chen/Tian/Chen (2026) — 복잡 교통상황 특수차량탐지(CBAM)

**④ 자율주행 인식(perception) — 4편**
- Ma/Yao/Liu 외 (2026, TR Part C) — pseudo-LiDAR+VLM 3D객체주석
- Abdelfattah/Alahi (2026, TR Part C) — 자율주행 통합 스켈레톤표현학습
- Borhani/Mordan 외 (2026, arXiv) — PoseDriver, 다중카테고리 스켈레톤탐지
- Chang/Liu 외 (2026, TR Part C) — 도로변카메라 자율주행 시나리오데이터

**⑤ 차량/이용자 행동 예측·모델링 — 3편**
- Kim/Frossard/Geroliminis (2026, IEEE Trans) — 차선변경예측. **IEEE Xplore 완전 막힘, 내용 대부분 not_found.** 데이터 출처 불명.
- Mukbil/Kamalasanan/Müller 외 (2025, Springer) — 공유공간 자전거이용자 에이전트기반 시뮬레이션
- Lemonakis/Anagnostopoulos/Kehagia/Zorba (2026, Sustainability) — 그리스, 좌회전 궤적 곡률(RDP/CDP). TTC/PET를 의도적으로 배제하고 "기하학적 일관성" 관점 채택. Fonod 2025도 미인용(같은 드론궤적 연구인데도).

**⑥ 교차로·도로 운영지표 — 3편**
- Elmorsy/Hamad/Obaid (2026, IEEE, UAE 샤르자) — 회전교차로 대기길이·지체(예비단계 결과)
- Schöckel/Kessler/Bogenberger (2026, J. Cycling, 독일 뮌헨공대) — 자전거 대기열, Geo-trax 파이프라인 재사용(탐지기만 YOLO12s로 교체)
- García-González/Doval 외 (2026, IEEE) — 항공영상 기반 회전교차로 궤적추출

**⑦ 신규 유사 궤적데이터셋 구축(타 도시) — 2편**
- Rajput/Venkateshappa/Kanagaraj 외 (2026, TR Part C) — SPT, 인도 첸나이 무질서혼합교통. Fonod 2025 인용 확인(맥락 미확인, 접근막힘).
- Han/Ji/Qian 외 (2026, arXiv) — SWIFTraj, 중국 난징. **자체 프레임워크(OpenVTER) 사용, Fonod 방법론 미계승 — Songdo는 비교표 항목으로만 인용.**

**⑧ 혼잡진단·교통상태추정 응용 — 4편**
- Al-Hourani/Darwish/Talafha 외 (2026, IEEE) — 드론+VLM 기반 교통혼잡 진단
- Wang/Wang/Cui/Liao 외 (2026, arXiv) — ExpressMind, 고속도로운영용 멀티모달 LLM
- **Cho/Yeo (SSRN, 송도팀 본인) — 카메라 사각지대 교통상태추정(Swin Transformer+게이트합성곱). 시뮬레이션+미국 NGSIM 벤치마크 사용, 실제 송도데이터 미사용.**
- Barbour/Bunting/Gloudemans 외 (2025, IEEE) — LiDAR 기반 고속도로 회랑구간 지속모니터링

**⑨ 수요·연료·환경 추정 — 3편**
- Liu/Guarda/Niinuma/Qian (2026, TR Part C) — 위성이미지 기반 대규모 OD수요추정
- Qian/Zhang 외 (2026, TR Part C) — FAFGAN, 운전스타일 고려 도로단위 연료소비추정
- 저자미상 (2025, 한국대기환경학회지) — CCTV+이동센서 결합 대기질평가

**⑩ UAV 자체 운용(경로계획/관제) — 3편**
- **Xu/Geroliminis (2026, TR Part C, 송도팀 본인) — UAV 소포배달+도로모니터링 경로계획. ScienceDirect 완전 막힘. 자매논문(arXiv:2604.02471, 바르셀로나 사용)으로 미루어 송도 미사용 가능성 높음(확정 아님).**
- Ye/Kyrrou/Kolios (2026, IEEE) — 다중UAV 연속추적용 핸드오버 프레임워크
- Das/Dhamayanthi/Rajeswari (2026, AI Conference) — 다중에이전트 학습 기반 드론(비행체) 교통관리

**⑪ 궤적데이터 품질·이상탐지·인프라모니터링 — 4편**
- Cleju/Catargiu (2026, Sensors, 루마니아) — 고정카메라 기반 궤적 이상탐지(드론 아님)
- Pan/Sun/Ashoori/Zhao (2026, J. Transportation Eng.) — 위치데이터 품질평가 리뷰
- Conde Morales (2025, 스페인) — 도로공사현장 모니터링
- Tan (2026, 박사논문) — 신흥기술 통합 행동기반 도로성능평가 프레임워크

**⑫ 저속자율차 규제기반 안전성평가 — 1편**
- Vass/Donà/Mattas 외 (2025, TR Part C, EU 공동연구센터) — 저속자율차 EU규제 적합성 평가. ScienceDirect 접근 실패로 TTC/PET 정량계산 여부 미확정(참고문헌 구성상 규제/시험프로토콜 기반일 가능성 높음, 확정 아님).

**⑬ 다중도시 드론실험 개관 — 1편**
- Barmpounakis/Espadaler-Clapés/Tsitsokas/Mordan/Geroliminis (2025, Drones) — 5개도시(송도Vision 포함) 개관, 정량분석 아님

**⑭ 교통과 무관 — 4편**
- Wang/Li (2025), Chen/Jian 외 (2026) — 송전선 절연체 결함탐지 2건
- Elchik/Hudson/Buckland 외 (2026, Mammal Review) — 대형포유류 모니터링
- Muthugala/Yunpeng (2025) — 생성AI 기반 일반 항공이미지 이상탐지

## 45편 PDF 확보 현황 (2026-08-13 세션에서 완료 — 구글 스칼라 인용목록 순서 기준 번호)

**출처**: 사용자가 직접 구글 스칼라(본인 한남대 계정 로그인 상태) cited-by 페이지에서 1~5페이지 전체를 복붙해서 준 45개 항목 목록이 ground truth. `references/` 폴더의 파일번호는 전부 이 순서(1~45) 기준. 스칼라 원본과 대조가 필요하면 사용자가 그 링크로 재확인 가능.

**중복 2건**: 11번=16번(FLUID, Scientific Data 정식판 vs arXiv 프리프린트), 19번=30번(PMA-Diffusion, TR Part C 정식판 vs arXiv 프리프린트) — 같은 논문이 버전 다르게 두 번 인용됨. 각각 정식판 쪽에 실제 파일을 넣고 반대쪽엔 "중복" 표시만 해둠.

| # | 제목(축약) | 저자 | 게재처 | 상태 |
|---|---|---|---|---|
| 1 | SPDC-YOLO | Bi/Li/Zheng 외 | Remote Sensing 2025 | ✅ `01_Bi_2025_...pdf` |
| 2 | TRIP(안전혼잡모니터링) | Espadaler-Clapés 외 | TR Part C 2025 | ✅ `TRIP_Espadaler2025/` 폴더(기존) |
| 3 | Multi-Source/HiMSNet | Xiong/Fonod/Alahi/Geroliminis | IEEE T-ITS 2025 | ✅ `03_Xiong_2025_...pdf` |
| 4 | UAV 경로계획 | Xu/Geroliminis | TR Part C 2026 | ✅ `04_Xu_2026_...pdf` |
| 5 | SPT(첸나이) | Rajput 외 | TR Part C 2026 | ✅ `05_Rajput_2026_...pdf` |
| 6 | Vehicle Detection Review | Ye/Kyrkou | IEEE T-ITS 2026 | ⚠️초록만(IEEE·도서관 둘다 없음) |
| 7 | 3D object annotation(pseudo-LiDAR+VLM) | Ma/Yao 외 | TR Part C 182:105429, 2026 | ✅ `07_Ma_2026_...pdf` |
| 8 | 5도시 개관 | Barmpounakis 외 | Drones 2025 | ✅ `08_Barmpounakis_2025_...pdf` |
| 9 | Large Mammal Monitoring | Elchik 외 | Mammal Review 2026 | ✅ `09_Elchik_2026_...pdf` |
| 10 | TRS-YOLO(절연체) | Wang/Li | J.Real-Time Image Proc. 2025 | ⚠️초록만(도서관엔 있으나 기관접속 미확보) |
| 11 | FLUID(정식판) | Chen 외 | Scientific Data 2026 | ✅ `11_Chen_2026_...pdf` |
| 12 | Vehicle ReID | Tak/Fonod/Geroliminis | Comm.Transportation Res. 2026 | ✅ `12_Tak_2026_...pdf` — **송도데이터 실사용 확인** |
| 13 | DSCW-YOLO | Zhang/Wang 외 | Sensors 2025 | ✅ `13_Zhang_2025_...pdf` |
| 14 | Unified skeleton | Abdelfattah/Alahi | TR Part C 190:105753, 2026 | ✅ `14_Abdelfattah_2026_...pdf` |
| 15 | 저속자율차 안전성 | Vass 외 | TR Part C 2025 | ✅ `15_Vass_2025_...pdf` |
| 16 | FLUID(arXiv, =11번 중복) | Chen 외 | arXiv 2025 | ✅ `16_Chen_2025_...pdf` |
| 17 | FAFGAN | Qian/Zhang 외 | TR Part C 186:105629, 2026 | ✅ `17_Qian_2026_...pdf` |
| 18 | 로드사이드카메라 시나리오데이터 | Chang/Liu 외 | TR Part C 191:105845, 2026 | ✅ `18_Chang_2026_...pdf` |
| 19 | PMA-Diffusion(정식판) | Liu/Jin/Choi | TR Part C 190:105801, 2026 | ✅ `19_Liu_2026_...pdf` |
| 20 | Unveiling Stochasticity(GMM) | Xiong/Fonod/Geroliminis | TR Part C 2026 | ✅ `20_Xiong_2026_...pdf` |
| 21 | OD수요추정(위성이미지) | Liu/Guarda/Niinuma/Qian | TR Part C 186:105615, 2026 | ✅ `21_Liu_2026_...pdf`(arXiv, 인용은 TR Part C로) |
| 22 | SWIFTraj Dataset Part I | Han/Ji/Qian 외 | arXiv:2602.22563, 2026 | ✅ `22_Han_2026_...pdf` |
| 23 | 차선변경예측(LC-DiTiNet) | Kim/Frossard/Geroliminis | IEEE T-ITS 2026 | ⚠️초록만(IEEE·도서관 둘다 없음) |
| 24 | 좌회전곡률(RDP/CDP) | Lemonakis 외 | Sustainability 18:6974, 2026 | ✅ `24_Lemonakis_2026_...pdf` |
| 25 | 드론교통관제(멀티에이전트RL) | Das/Dhamayanthi/Rajeswari 외 | IEEE AIEI 2026 | ⚠️초록만(IEEE) |
| 26 | 궤적이상탐지 | Cleju/Catargiu | Sensors 26:3027, 2026 | ✅ `26_Cleju_2026_...pdf` |
| 27 | 자전거대기열 | Schöckel/Kessler/Bogenberger | J.Cycling 2026 | ✅ `27_Schockel_2026_...pdf` |
| 28 | 위치데이터품질리뷰(PCLD) | Pan/Sun/Ashoori/Zhao/Darzi | J.Transportation Eng. 2026 | ⚠️초록만(ASCE, 도서관엔 뜨나 다운 안됨) |
| 29 | SIDF-YOLO(절연체) | Chen/Jian 외 | J.Real-Time Image Proc. 2026 | ⚠️초록만(기관접속 필요) |
| 30 | PMA-Diffusion(arXiv, =19번 중복) | Liu/Jin/Choi | arXiv:2512.06183, 2025 | ✅ `30_Liu_2025_...pdf` |
| 31 | 캘리포니아 속도탐지 | Ataee Naeini 외 | ISVC2025/arXiv:2506.11239 | ⚠️초록만(arXiv 무료지만 파일 10MB초과로 자동수집 실패) |
| 32 | ExpressMind(고속도로LLM) | Z.Wang/Y.Wang/Yu/Cui/Liao/C.Wang/Tian/Tong | arXiv:2603.16495, 2026 | ✅ `32_Wang_2026_...pdf` |
| 33 | 멀티UAV 핸드오버 | Ye/Kyrkou/Kolios | arXiv:2605.15779, ICUAS2026 | ✅ `33_Ye_2026_...pdf` |
| 34 | 자전거 ABM(공유공간) | Mukbil/Kamalasanan/Müller/Friedrich | PRIMA2025(Springer LNCS) | ⚠️초록만(기관접속 필요) |
| 35 | LiDAR 회랑 지속모니터링 | Barbour/Bunting/Gloudemans/Sprinkle | IEEE2025(내슈빌 120일) | ⚠️초록만(IEEE) |
| 36 | UAV 회전교차로 대기·지체 | Elmorsy/Hamad/Obaid | ICAISET2026 | ⚠️초록만(IEEE·도서관 둘다 없음) |
| 37 | PoseDriver(스켈레톤탐지) | Borhani/Mordan 외 | arXiv:2603.23215, 2026 | ✅ `37_Borhani_2026_...pdf` |
| 38 | 회전교차로 궤적추출(8곳) | García-González/Doval 외 | IEEE2026 | ⚠️초록만(IEEE) |
| 39 | 도로공사현장 모니터링 | Conde Morales | UVigo 박사논문 2025 | ✅ `39_CondeMorales_2025_...pdf` |
| 40 | TrajVLM(혼잡원인진단) | Al-Hourani/Darwish/Talafha 외 | IEEE2026 | ⚠️초록만(IEEE) — **★송도 트래픽 신호교차로 1곳 실제 evaluation 사용 확인(3조건 ablation)** |
| 41 | 이상탐지(생성AI, unCLIP) | Muthugala/Yunpeng | IEEE2025 | ⚠️초록만(IEEE, 도서관엔 있으나 연결 불가) |
| 42 | 특수차량탐지(CBAM) | Fan/Chen/Tian/Chen 외 | SPIE2026 | ⚠️초록만(기관접속 필요) |
| 43 | 도로성능평가(행동기반) | Tony Tan(지도:Yichang James Tsai) | Georgia Tech 석사논문 2026 | ⚠️ProQuest 10p 미리보기만(2장 2.3절 컷오프, 본론없음) — GT 자체리포지토리(repository.gatech.edu)에 추후 게재 가능성, 아직 못 찾음 |
| 44 | 카메라 사각지대 상태추정 | Cho·Yeo(송도팀 본인) | SSRN 프리프린트(미심사) | ✅ `44_Cho_Yeo_...pdf` |
| 45 | 동적주제도 생성 프로세스 | 김지은·윤준희 | 대한공간정보학회지 33(특별):33-39, 2025 | ✅ `45_김지은윤준희_2025_...pdf` |

**⚠️초록만인 15편(6,10,23,25,28,29,31,34,35,36,38,40,41,42,43)의 한글 번역 초록 전문은 이번 세션 대화 기록에 있음 — 다음 세션에서 필요하면 사용자에게 재요청하거나 대화기록 참조.**

**작업 중 알게 된 기술적 제약(다음 세션 참고)**:
- MDPI 저널 PDF/페이지는 Claude의 웹조회 도구가 403으로 차단됨(오픈액세스인데도) — 링크만 전달하고 사용자가 직접 받아야 함
- IEEE Xplore는 초록 페이지조차 418로 차단됨 — 사용자가 화면 텍스트를 직접 복붙해줘야 함
- 구글 스칼라 결과 페이지 직접 스크래핑은 부정확할 수 있음(특히 한국어 제목에서 같은 페이지를 4번 조회해서 4번 다른 결과가 나온 적 있음) — 애매하면 사용자가 직접 복붙 확인 권장, DBpia 등 원문 페이지 직접조회가 더 정확했음
- arXiv PDF는 대체로 잘 받아지지만 10MB 넘으면 자동수집 실패(SWIFTraj, 캘리포니아속도탐지 등) — 이 경우도 링크 전달 방식

## 폴더 구조

```
(송도) 교통 연구 논문/
├── data/raw/                              ← 원본 궤적데이터(14GB, zip 80개)
├── references/
│   ├── 원논문_Fonod2025/                   ← 원 논문(Fonod 2025)
│   ├── TRIP_Espadaler2025/                 ← Espadaler 2025 원문+한글번역(=2번)
│   └── 01~45번 PDF (30개, 상세는 위 표) ← 원논문을 인용한 45편, 구글스칼라 순서 번호
└── 초안/ITS 초안.hwp                       ← ITS 학회 참고자료(구 폴더에서 이전)
```

옛 폴더(`c:\Users\USER\Documents\교통 관련 논문 작성\`)에는 `.claude`, `.git`, `src/`(TTC·PET 계산 파이프라인 코드, 01~16번 py 스크립트)만 남아있음 — "전이가능성" 주제의 파이프라인 코드로, 새 주제가 상충/안전 계열(카테고리①)로 정해지면 재활용 가능성 있음.

## 지켜야 할 규칙 (사용자가 명시적으로 요청함)

- **절대 금지**: 사용자가 새 주제를 정하는 과정에서 임의로 추론을 삽입하거나 방향을 대신 정하지 말 것. 사실관계 정리·표 작성까지만 하고, 최종 주제 선택은 사용자와 지도교수의 몫.
- **절대 금지(2026-08-13 추가 확인)**: 옛 폴더(`교통 관련 논문 작성`, TTC·PET 전이가능성 주제)의 내용을 이 폴더로 절대 끌어오지 말 것. 코드 재활용 "가능성"을 언급하는 것조차 방향을 흐릴 수 있으니, 사용자가 먼저 요청하기 전엔 옛 폴더 내용을 꺼내지 않는다.
- **절대 금지(2026-08-13 추가 확인)**: 사용자는 이미 새 주제를 정하기까지의 방향성을 어느 정도 잡아두고 있음. Claude가 임의로 추론하거나 새로운 방향/아이디어를 삽입해서 그 방향성을 흐리게 하는 것 금지. 사용자가 먼저 자기 방향을 제시하면 그 틀 안에서 사실관계 정리·검증만 지원할 것.
- 확인 안 된 내용은 반드시 "not_found"로 명시, 추측 금지.
- "없다"보다 "확인되지 않았다"로 표현(단정 피하기).
- 이 폴더에 종합/요약 문서를 새로 저장하는 것 자체는 이번엔 사용자가 명시적으로 요청한 것(세션 연속성 목적) — 다만 논문 본문에 들어갈 완성된 문서를 대신 써주는 건 별개 문제이니 주의.

## 다음 할 일

1. ~~막힌 논문 PDF 확보~~ — **2026-08-13 세션에서 완료.** 45편 중 30편 원문 확보, 15편은 초록까지 확보(위 표 참고). 이 이상은 유료/기관접속 벽이라 사용자가 개별적으로 더 뚫지 않는 한 여기가 한계.
2. **(다음 시작할 것)** 45편 각각에 대해 "원논문의 무엇을 인용했는가 / 무슨 연구를 했는가"를 정식 표로 정리 — 컬럼: 번호, 영문원제(한글번역), 상태, 게재처, 연구내용 요약, 원논문 인용맥락(데이터? 방법론Geo-trax? 단순언급?), 카테고리. 기존 ①~⑭ 카테고리 분류(위 섹션)를 새 45번 체계에 맞게 재대조하면서 진행.
3. 카테고리별로 저자가 스스로 명시한 한계점(limitations)·future work 뽑아서 정리 — **Claude는 사실 추출만, 이 목록 보고 새 주제 아이디어를 뽑는 건 순전히 사용자·교수님 몫(절대 규칙, 위 참고).**
4. 새 주제 정해지면 그에 맞는 폴더 구조·코드 재활용 여부 정리, 카테고리 기준으로 45번 파일 번호 재정렬.

**참고할 실마리**: 12번(ReID)·40번(TrajVLM)이 지금까지 확인된 것 중 송도 데이터를 실제 evaluation에 쓴 흔치 않은 사례. 40번은 신호교차로 1곳만 썼는데 방법론 검증(3조건 ablation) 목적이라 표본 하나로도 논리적으로 문제없다는 게 세션 중 나온 논의였음(단, 이것도 사용자 판단 존중 — Claude가 방향 제안한 것 아님).
