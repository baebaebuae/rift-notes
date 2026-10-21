# RIFT NOTES

한국어·영어를 지원하는 리그 오브 레전드 챔피언 도감. 정적 HTML/CSS/JavaScript 사이트입니다.

## 기능

- 상단 버튼으로 한국어/영어 전환: 챔피언·스킬 탭·레벨·패치 필터 유지, 브라우저에 언어 기억
- `?lang=ko` / `?lang=en` 언어별 링크와 해당 언어의 공식 스킬 설명·패치 원문
- 한국어 피해량·계수 항목, 단위, 변형 스킬명 및 원문에 남은 영어 패치 문장 번역
- 기본 주소로 접속할 때 무작위 챔피언 표시, 챔피언별 공유 주소는 지정 챔피언 유지
- 공식 목록의 모든 챔피언 검색: 한국어, 영문, 초성 및 역할군 필터
- P/Q/W/E/R 설명, 랭크별 피해량·계수, 재사용 대기시간·소모량
- 레벨에 따른 기본 능력치 계산, 즐겨찾기, 챔피언별 공유 링크
- 공식 한국어 패치 노트를 챔피언별로 분리한 최신순 타임라인
- 변경 유형/시즌 필터, 이전 기록 페이지 확장, 공식 원문 링크
- 반응형 화면, 키보드 검색 단축키 `/`, 방향키/Enter 및 한글 조합 입력 지원
- 스킬 설명·수치 14px, 스킬 이름 17px, 긴 계수 줄바꿈
- 첫 랜덤 챔피언으로 뒤로 가기 복원, 모바일 검색 배경 닫기, 요청 시간 초과 및 재시도

## 중요한 데이터 구분

1. 기본 능력치, 스킬 설명, 재사용, 비용: Riot Data Dragon 16.21.1 (게임 패치 26.21).
2. 세부 계수: Meraki Analytics 전체 챔피언 스냅샷 15.15.1. 해당 공개 데이터의 갱신 지연 때문에, 검증되지 않은 값은 **25.15 보관본**으로 분명하게 표시합니다. 최신값으로 간주하면 안 됩니다.
3. `dist/data/verified.json`: 아리/럭스에 대해서 보관본 이후 공식 패치를 대조해 갱신한 수치. 버전이 일치할 때만 최신 검토 표시를 합니다.
4. Data Dragon의 모든 챔피언 `attackdamageperlevel`이 0인 결함을 확인했습니다. 이 항목은 Meraki 기본값과 이후 공식 능력치 변경을 적용한 별도 필드로 보완하며, 출처를 저장합니다. 확인할 수 없는 신규 챔피언 값은 0으로 가정하지 않습니다.
5. 패치 이력은 공식 문서에서 챔피언 이름이 있는 항목을 추출합니다. 일부 문서, 챔피언 이름이 없는 전역 변경, 별도 버그 수정, 다른 게임 모드, 초기 서비스 시기 기록은 포함되지 않을 수 있습니다. 실제 수집 범위와 누락 문서는 화면의 데이터 안내에 표시됩니다. 수치 증감에 의한 상/하향 분류는 실제 게임 영향과 다를 수 있습니다.
6. 현재 사이트는 수집 시점 스냅샷입니다. 자동 갱신 작업은 연결되어 있지 않습니다.

## 26.21 업데이트 (2026-10-21)

- 공식 한국어·영어 패치 노트의 소환사의 협곡 챔피언 25명, 변경 56개 반영.
- 스킬 카드에서 최신 패치 변경 수치를 먼저 표시하고, 해당 스킬의 25.15 보관 수치는 접어서 구분. 최신 검토는 변경된 항목에만 해당합니다.
- 173명 기본 능력치·설명·재사용·소모량을 공식 16.21.1로 갱신. 징크스 공격력 성장 3, 체력 610 등 대조.
- 다리우스 Q: 패치 노트는 9/8/7/6/4초, Data Dragon은 9/7.75/6.5/5.25/4초입니다. 화면은 패치 노트 수치를 우선하며 차이를 함께 안내합니다. 원본 데이터는 보존합니다.
- 아리·럭스는 26.21에 변경이 없음을 확인하고 검토 범위를 갱신.
- 이전 한글 기록에 잘못 연결됐던 아이템·룬·정글 및 다른 챔피언 항목 정리. 신 짜오 11.6의 중간 제목으로 인한 누락 수정.
- 매번 최신 버전 목록 및 최근 2개 패치 원문을 다시 확인하고, 브라우저의 JSON 캐시를 재검증합니다.

## 데이터 재수집

Python 3와 `beautifulsoup4`가 필요합니다. API 키를 사용하지 않습니다.

```bash
python -m pip install -r requirements.txt
python scripts/collect_data.py
python scripts/fetch_assets.py
python scripts/collect_english.py
python scripts/build_localization.py
```

`RIFT_CACHE`로 다운로드 임시 캐시 경로를 지정할 수 있습니다. 각 챔피언 JSON에 현재 공식 데이터 URL, 보관본 URL, 버전, 패치 이력을 남깁니다. 재수집 후 `verified.json`의 버전/각 수치는 반드시 재검토해야 합니다. 수집기는 검증값을 자동으로 최신이라고 바꾸지 않습니다. 새 패치가 추가되면 URL 형식과 HTML 파싱 결과도 검토해야 합니다. 영어 수집기는 한국어 목록에 저장된 버전을 사용하며, 영어와 한국어 문서의 수집 범위·기록 수는 다를 수 있습니다. `scripts/locales/ko-exact.json` 및 번역 생성기의 용어 사전도 신규 항목에 맞게 검토해야 합니다. 번역은 표시 문구에만 적용하고 원본 계수와 출처는 유지합니다.

## 검증

```bash
node --check dist/app.js
# jsdom 설치 경로를 RIFT_JSDOM으로 전달하거나 Node가 모듈을 찾을 수 있도록 설치
RIFT_JSDOM=/absolute/path/to/jsdom node scripts/verify.cjs
RIFT_JSDOM=/absolute/path/to/jsdom node scripts/verify_localization.cjs
python scripts/verify_data.py
# 26.21 스냅샷 대조 (다음 패치 작업 시 기대값도 갱신)
RIFT_JSDOM=/absolute/path/to/jsdom node scripts/verify_latest_patch.cjs
```

173명 전체의 양 언어 렌더링, 수치 동일성, 번역 누락, 검색·필터·능력치, 랜덤 시작과 공유 주소, 언어 선택 저장과 전환 상태, 뒤로/앞으로 가기, 한글 조합 입력, 모바일 검색, 네트워크 지연·실패·시간 초과를 DOM 기반으로 테스트합니다. 26.21 업데이트에서 실제 Chromium 미리보기로 최신 수치 카드, 보관본 구분 및 한영 전환을 확인했습니다. 모바일 동작은 DOM 테스트로 확인했습니다. 외부 스킬 아이콘/일부 챔피언 배경과 Google Fonts는 네트워크에 의존하며 시스템 폰트 대체를 제공합니다. 챔피언 목록 이미지와 기본 아리 배경은 배포 파일에 포함됩니다.

## 구성

- `dist/index.html`, `dist/styles.css`, `dist/app.js`: 화면과 동작
- `dist/data/*.json`: 한국어 데이터, 검토 수치 및 한국어 번역 사전
- `dist/data/en/*.json`: 같은 버전의 공식 영문 챔피언 데이터 및 영문 패치 기록
- `scripts/collect_english.py`: 영어 데이터 수집 및 챔피언 항목·추가 패치 날짜 검증
- `scripts/build_localization.py`, `scripts/locales/ko-exact.json`: 한국어 표시 번역과 영문 검토 수치 생성
- `dist/data/patches.json`: 문서별 수집 결과
- `scripts/collect_data.py`: 공식 데이터 및 패치 수집/정규화
- `scripts/fetch_assets.py`: 공식 이미지 저장
- `.openai/hosting.json`: 정적 배포 설정

## 출처와 권리

게임 데이터와 이미지: Riot Games Data Dragon / League of Legends 공식 패치 노트.
세부 계수 보관본: Meraki Analytics `lolstaticdata` 및 League of Legends Wiki 기여자. 관련 Wiki 데이터는 CC BY-SA 3.0에 따라 출처와 변경 여부를 표시합니다. 사이트 하단에 Riot 비공식 팬 도구임을 표시합니다.
