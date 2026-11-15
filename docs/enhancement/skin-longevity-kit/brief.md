# SKIN LONGEVITY READY KIT 상세 페이지

BIO ELIXIR와 SUN VEIL을 묶은 키트 상품의 상세 페이지를 만든다.
두 제품의 기존 상세를 편집해 합치고, 키트 전용 섹션을 새로 추가한다.

- 상태: 2026-11-14 개발 계획 수립 · 1차 구현 완료(확인 모드 375 · 768 · 1024 · 1280 · 1920px) — skin10 실제 반영 전
- 이미지 원본: [src/](src/) — 키트 컷(0554) · 엘릭서 컷(0266) · 선베일 컷(0029) · 임상 사진(S15 3장). `AYROW_0549.jpg`(쇼핑백과 함께 찍은 컷)는 시안에 쓰인 곳이 없어 아직 쓰지 않았다
- 기획 원문: [plan/](plan/) — 클라이언트 기획안(Notion 내보내기)과 첨부(결과보고서 PDF · 임상 원본 사진 · 예시 이미지)
- 결과물: `set/cafe24-admin/set-pdc.html` (조립: `tools/pdc-set/build.py`) · 스킨 레포 `pdc-set.css` · `pdc-set.js`
- 코딩 규칙: 스킨 레포 `docs/pdc-convention.md`

## 1. 목표

단순 할인 세트가 아니라 "왜 두 제품을 함께 써야 하는가"를 설득한다.
흐름은 **키트 소개 → 함께 쓰는 이유 → 병행 임상 결과 → 제품별 상세 → 브랜드 철학** 순서다.

## 2. 페이지 구성

| 순서 | 섹션 | 역할 | 디자인 | 구현 |
| --- | --- | --- | --- | --- |
| 0 | LAUNCH SPECIAL | 런칭 혜택 배너(11.15 – 11.30 · 500세트 한정 30% OFF) | 시안 00 | 신규 — 2026-11-15부터 1(KIT CONCEPT)과 2(TWO FORMS) 사이에 놓는다 · 런칭 기간이 끝나면 뺀다(`build.py --no-launch`) |
| 1 | KIT CONCEPT | 키트의 정체성 | 시안 01 | 신규 |
| 2 | TWO FORMS | 두 제품의 형태와 역할 | 시안 02 | 신규 |
| 3 | CLINICAL PROOF | 병행 사용 인체적용시험 | 시안 03 | 신규(엘릭서 임상 블록 재사용) · 요약표 포함(2026-11-14 한때 뺐다가 같은 날 되돌림) |
| 4 | BIO ELIXIR | 기존 상세 콘텐츠 | 기존 | 기존 섹션 선별 |
| 5 | SUN VEIL | 기존 상세 콘텐츠 | 기존 | 기존 섹션 선별 |
| 6 | THE KIT RITUAL · WHEREABLE BEAUTY™ | 사용 순서(LAYER. WEAR. GO.) → 브랜드 철학으로 마무리(2026-11-14 순서 바꿈) | **없음** | 기존 체계로 임시 구현 — 시안 필요 |
| 7 | FAQ | 키트 8문항 + 제품별 | 없음(기존 FAQ 모양) | 탭 3개: 키트 / 바이오 엘릭서 / 선베일 |

### 디자인 시안 (Figma, 데스크톱 1680px 기준)

- 00 LAUNCH SPECIAL — [node 6328-1702](https://www.figma.com/design/tuPYxWFruFfgQFpTsxot6P/AYROW-Set-%E1%84%89%E1%85%A1%E1%86%BC%E1%84%89%E1%85%A6%E1%84%91%E1%85%A6%E1%84%8B%E1%85%B5%E1%84%8C%E1%85%B5--1-?node-id=6328-1702&t=7PXUtuxyoAGgWPGI-4) (2026-11-14 추가)
- 01 KIT CONCEPT · 02 TWO FORMS — [node 6323-120](https://www.figma.com/design/HyLNf8Sumwbmkl4uBGKNUR/AYROW-Set-%E1%84%89%E1%85%A1%E1%86%BC%E1%84%89%E1%85%A6%E1%84%91%E1%85%A6%E1%84%8B%E1%85%B5%E1%84%8C%E1%85%B5?node-id=6323-120&t=bLJBo8gscSrBr2vb-4)
- 03 CLINICAL PROOF — [node 6303-120](https://www.figma.com/design/HyLNf8Sumwbmkl4uBGKNUR/AYROW-Set-%E1%84%89%E1%85%A1%E1%86%BC%E1%84%89%E1%85%A6%E1%84%91%E1%85%A6%E1%84%8B%E1%85%B5%E1%84%8C%E1%85%B5?node-id=6303-120&t=bLJBo8gscSrBr2vb-4)

### 다섯 가지 결과 요약("다섯 가지 지표로 확인한 변화")

키트 상세에서는 보여 주지 않는다. 기존 단품 상세의 해당 섹션에서 보여 주는 방향이다(2026-11-14 전달받음).
마크업은 `tools/pdc-set/sections/_clinical-summary.html`에 따로 두었다. 어느 단품의 어느 섹션에 넣을지는 미정이다(§4).

### 기존 콘텐츠 선별 (기획안 §04 기준)

기획안이 적은 항목만 남긴다. 문구 · 마크업은 원본 그대로 쓴다.

| 제품 | 남기는 섹션 | 빼는 섹션 |
| --- | --- | --- |
| BIO ELIXIR | hero(구간 표지) · concentrate(2026-11-15에 되살림) · clinical · origin(STECHA™) · botanical(74+4) · ltve · harmony(Reverse AG Code™) | ritual(Whereable Beauty — 6번 섹션이 대신한다) · usage(사용방법 — 2026-11-14에 뺌) |
| SUN VEIL | hero(구간 표지) · film-membrane(필름 vs 나노 섬유) · film-membrane-standard · how-it-works · how-it-bonds · reverse-ag-code-formula · proven-data · makeup-routine | how-to-use(사용 방법 — 2026-11-14에 뺌) · membrane-intro · problem · film-membrane-pain · film-membrane-choice · at-a-glance · why-intro · why-highlight |

- 제품 Hero는 기획안 목록에 없지만 구간 표지로 남긴다(2026-11-13 결정: 엘릭서 → 선베일 전환을 제품 표지로 잇는다).
- `build.py --full`로 빼는 섹션까지 모두 실은 판을 만들 수 있다(길이 비교용).

## 3. 시안을 체계에 맞추는 방법

시안은 스킨 디자인 시스템을 정확히 따르지 않는다. 아래처럼 맞춘다.

| 시안 | 구현 |
| --- | --- |
| 글꼴 Noto Sans KR · Inter · Suisse Int'l **Trial** | 스킨 글꼴(Pretendard · Suisse Int'l)과 타이포 클래스(`heading-*` · `body-*` · `type-display`) |
| 글자 크기 48 · 42 · 40 · 35 · 32 · 25 · 22 … | 가장 가까운 스킨 타이포 단계로 맞춤 |
| 색 `#0077bf` | `--pdc-accent` |
| 배경 `#ebf2fe` · 탭 `#e3ecfb` · 선택 탭 `#f8f3a3` | 엘릭서 임상 띠(`pdc-clinical--sv`)가 쓰는 값 그대로 |
| 무도포 `#73b58f` · 보조 글자 `#6187a6` · `#6b96b8` · `#d3d2d2` | 스킨 token에 있으면 그것, 없으면 `--pdc-set-*` 블록 변수 |
| 모서리 24px · 카드 여백 | `--pdc-radius` · `--pdc-card-pad` |
| 절대 좌표 배치 | grid / flex. 콘텐츠 폭은 `container--md` |
| 그래프 · 전후 비교 · VIEW THE STUDY | 엘릭서의 `pdc-chart` · `pdc-elixir-compare` · `pdc-disclosure` · `pdc-study` 재사용 |
| 임상 항목 탭 | 세트 탭 동작(`data-pdc-set-tabs`)에 `pdc-set-clinical__tab` 모양. 엘릭서 시점 탭(`pdc-timepoints`)은 자동 재생 · 시점 전용 계산이 묶여 있어 쓰지 않음 |
| 그래프 선 2개(병행 · 무도포) · 원형 수치 | 엘릭서에 없어 `pdc-set-*`로 추가 |
| 데스크톱 시안만 있음 | 1023px 이하: 컨셉 · 두 형태 · 그래프 카드를 한 칸으로. 767px 이하: 임상 사진을 한 줄에 하나, 수치를 제목 아래로 |
| 배너 배경 `#faf2ae` · 강조 `#802727` | `--primitive-creme` · `--primitive-merlot` |

## 4. 확인이 필요한 내용

### 디자인이 필요한 곳

1. **WHEREABLE BEAUTY™ (THE KIT RITUAL — LAYER. WEAR. GO.)** — 시안이 없다. 기획안은 "두 제품을 함께 쓰는 순서가 읽히도록 이미지 크기와 배치를 조정"하라고 하는데, 어떤 컷을 쓸지와 2분할 비율은 디자인 판단이 필요하다. 지금은 TWO FORMS의 카드 구성을 빌려 임시로 구현한다.
2. ~~LAUNCH SPECIAL 배너~~ — 2026-11-14 시안을 받아 구현했다.
3. **모바일 · 태블릿 화면** — 시안이 데스크톱뿐이다. 00–03 모두 기존 섹션의 접는 방식을 따랐다. 03의 수분 손실 그래프는 가로로 긴 비율이라 좁은 화면에서 높이가 낮아져, 1023px 이하에서는 같은 값을 좁은 화면 비율(468×292)로 다시 그린 그래프를 보여 준다(2026-11-14).
4. ~~**그래프 값 라벨 겹침**~~ — 해결(2026-11-14): 값이 거의 같은 두 시점은 라벨 두 개를 선이 지나지 않는 쪽에 두 줄로 쌓고, 마지막 시점은 선이 들어오는 반대쪽에 둔다. 시안의 라벨 위치(선 위아래)와는 다르다.
5. ~~임상 사진 해상도~~ — 2026-11-14 원본(`src/임상실험/`, 951×401)을 받아 부위별 401px 정사각으로 다시 만들었다.
6. **색소침착** — 요약표의 한 줄뿐이고 이미지가 없다. 기획안은 "보조 임상 이미지"를 요구한다(원본 사진은 `plan/`에 있음). 넣으려면 탭이나 카드 자리가 필요하다.
7. **피부결 임상 이미지** — 기획안은 "임상 이미지 + 수치"인데 시안은 그래프만 있다.

### 기획안과 시안이 다른 곳 (시안을 따름)

| 항목 | 기획안 | 시안 |
| --- | --- | --- |
| KIT CONCEPT 국문 메인 카피 | "스킨 롱제비티, 케어에서 보호까지." | 없음 |
| TWO FORMS 번호 라벨 | 01 / CONCENTRATE · 02 / WELLNESS PATCH | 01 / CARE · 02 / PROTECTION |
| 임상 머리말 | TWO WEEKS. FIVE RESULTS. | Clinically Tested · 2 Weeks / "자외선 노출로 손상된 피부, 2주 후의 변화" |
| 임상 탭 | 구분 없음 | 01 자극받은 피부 진정 · 02 수분 손실 회복 · 03 거친 피부결 개선(피부결 + 보습 카드) |

### 문구 · 데이터

- 시안의 수치 22개(개선율 4개 · 그래프 값 18개)는 결과보고서와 일치한다(2026-11-14 대조).
- 선베일 두께 표기: 키트 문구는 "4μm", 기존 선베일 상세는 "0.004mm". 같은 값이지만 한 페이지에 두 표기가 나온다.
- 임상 사진의 부위 라벨: 시안은 "컨센트레이트+패치"(시험 표기)인데, 그래프 범례와 맞춰 "병행 사용"으로 적었다. 확인이 필요하다.
- 다섯 가지 결과 요약을 넣을 단품 상세와 섹션(엘릭서 임상? 선베일 Proven Data?) — 단품 상세는 판매 중인 페이지라 정해지면 따로 작업한다.
- 런칭 배너의 "30% OFF = 런칭 기념 20% + 회원 추가 10%"는 시안 문구 그대로다. 실제 할인 계산(중복 적용 시 28%)과 표기가 맞는지 확인이 필요하다.
- ~~임상 머리말 "다섯 가지 피부 지표"와 보이는 지표 수(4개)의 어긋남~~ — 요약표를 되돌려 다섯 지표가 모두 보인다(해결 2026-11-14).
- 수분 손실량 124.573%는 100%를 넘는 회복률이다. 각주("자외선 노출로 증가한 수분 손실량의 회복률")는 요약표에 있다(요약표를 되돌림 2026-11-14). 탭 02 카드에도 같은 설명을 넣을지는 확인한다.
- 키트 상품 이름: "에이로우 스킨 롱제비티 레디 키트"(138,900원)로 본다.

### 이번 범위 밖

- Related Products(단품 ↔ 키트 상호 노출): 상세 내용이 아니라 스킨 · 관리자 설정이다.
- 키트 상품용 JSON-LD · 숨김 h1.
- 이미지의 CDN 업로드(`/web/src/set/`) — 4장 참고.

## 5. 개발 계획

| 단계 | 내용 | 산출물 |
| --- | --- | --- |
| 0 | 00 LAUNCH SPECIAL | `pdc-launch` |
| 1 | 이미지 준비 — 시안의 키트 · 제품 컷 3장, 임상 사진 6장, 배너 아이콘을 크롭 · 압축 | 스킨 레포 `src/set/` |
| 2 | 01 KIT CONCEPT · 02 TWO FORMS | `pdc-set-concept` · `pdc-set-forms` |
| 3 | 03 CLINICAL PROOF — 대표 수치 카드 → 탭 3개(진정 사진 / 수분 손실 그래프 / 피부결 · 보습 그래프) → VIEW THE STUDY | `pdc-set-clinical` + 엘릭서 임상 블록 |
| 4 | 기존 콘텐츠 선별 반영 | `build.py` |
| 5 | WHEREABLE BEAUTY™ 임시 구현 | `pdc-set-ritual` |
| 6 | FAQ — 키트 8문항 탭 추가 | `build.py` |
| 7 | 확인 — 375 · 768 · 1024 · 1280 · 1920px, 탭 · 그래프 · 비교 슬라이더 동작 | `tools/pdc-compare` |
| 8 | 규칙 문서 등록부 · 작업 기록 갱신 | `pdc-convention.md` · `docs/changelog` |

0–8단계는 2026-11-14에 마쳤다. 남은 일:

1. 이미지 10개를 CDN `/web/src/set/`에 올린다(파일은 스킨 레포 `src/set/`). 올리기 전에는 실제 페이지에서 키트 이미지가 보이지 않는다.
2. skin10 반영 확인 — `pdc-set.css` 업로드, 관리자에 `set-pdc.html` 붙여 넣기 → 실제 페이지에서 탭 · 그래프 그리기 · 비교 슬라이더 · 움직임 확인.
3. §4의 확인 사항 반영(Whereable Beauty 시안 · 문구 확인).

### 구현 메모

- 세트 전용 마크업은 `tools/pdc-set/sections/`의 HTML 조각으로 두고 `build.py`가 조립한다. 제품 섹션은 지금처럼 원본에서 그대로 꺼낸다.
- 03의 탭은 `pdc-set.js`의 탭 동작을 쓴다(FAQ 탭과 같은 코드, 자동 재생 없음). 그래프 그리기 · 값 라벨 크기 맞춤 · 비교 슬라이더는 `pdc-elixir.js`가 루트 전체에서 찾아 맡는다(`svg.pdc-chart` · `[data-pdc-compare]`).
- 키트 FAQ는 엘릭서 FAQ 블록(`pdc-faq`)을 쓰므로 `<div class="pdc--elixir pdc-set__group">` 안에 둔다.
- 스킨 token(`css/core/`)은 참조만 한다. 없는 값은 `pdc-set.css`의 블록 변수로 둔다.
- 이미지 주소는 CDN 절대경로(`…/web/src/set/…`)로 적는다. 파일은 스킨 레포 `src/set/`에 두며, 실제 반영 전에 `/web/src/set/`에 올려야 한다.
