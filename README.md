# RIFT NOTES

한국어·영어를 지원하는 리그 오브 레전드 챔피언 도감. 정적 HTML/CSS/JavaScript 사이트입니다.

## 기능

- 상단 버튼으로 한국어/영어 전환: 챔피언·스킬 탭·레벨·패치 필터 유지, 브라우저에 언어 기억
- `?lang=ko` / `?lang=en` 언어별 링크와 해당 언어의 공식 스킬 설명·패치 원문
- 한국어 피해량·계수 항목, 단위, 변형 스킬명 및 원문에 남은 영어 패치 문장 번역
- 기본 주소로 접속할 때 무작위 챔피언 표시, 챔피언별 공유 주소는 지정 챔피언 유지
- 공식 목록의 모든 챔피언 검색: 한국어, 영문, 초성 및 역할군 필터
- P/Q/W/E/R 설명, 랭크별 피해량·계수, 재사용 대기시간·소모량
- 패시브 문장형 상세 설명: 피해량·계수·중첩·발동 조건·대상별 예외를 한영으로 표시, 숫자 강조 및 긴 설명 펼치기
- 레벨에 따른 기본 능력치 계산, 즐겨찾기, 챔피언별 공유 링크
- 공식 한국어 패치 노트를 챔피언별로 분리한 최신순 타임라인
- 변경 유형/시즌 필터, 이전 기록 페이지 확장, 공식 원문 링크
- 반응형 화면, 키보드 검색 단축키 `/`, 방향키/Enter 및 한글 조합 입력 지원
- 스킬 설명 14px·상세 수치 15px (모바일 14px), 스킬 이름 17px, 긴 계수 줄바꿈
- 첫 랜덤 챔피언으로 뒤로 가기 복원, 모바일 검색 배경 닫기, 요청 시간 초과 및 재시도

## 26.22 업데이트 (2026-11-07 검토)

- 소환사의 협곡 챔피언 14명의 공식 변경 44건을 한국어·영어 패치 기록에 반영했습니다. 멜의 패시브부터 궁극기까지 개편 수치를 적용하고, 피해 합계처럼 이전 식에서 계산하던 값도 갱신했습니다.
- 챔피언 173명의 능력치·스킬 설명·재사용 대기시간·소모량 기준은 Data Dragon 16.22.1입니다. 멜 W의 마나 소모량은 패치 노트의 100/80/60/40/0을 표시합니다.
- 쉬바나 26.6 개편과 로크 26.13 출시의 독립 섹션을 복원했습니다. 쉬바나의 패시브 중첩 조건, 엘리스 Q의 대몬스터 최대 피해, 니달리 R의 사냥 표식 초기화 조건 등을 보완했습니다.
- 스킬 카드에는 설명·발동 조건·적용 수치만 표시합니다. 패치별 변경과 공식 원문은 챔피언 아래의 패치 기록에 있습니다.
- 사용한 두 언어의 버전별 championFull.json 보관본은 원본 형식, 버전, 173명 명단과 Git blob을 확인했습니다. [보관본 커밋](https://github.com/noxelisdev/LoL_DDragon/commit/dc04342110a9e0d7f76ffc844475070317015216) · [한국어 패치 노트](https://www.leagueoflegends.com/ko-kr/news/game-updates/league-of-legends-patch-26-22-notes/) · [영어 패치 노트](https://www.leagueoflegends.com/en-us/news/game-updates/league-of-legends-patch-26-22-notes/)

## 누적 패치 반영 (2026-10-27 검토)

- 25.16부터 26.21까지 한국어·영어 공식 패치 노트를 재수집해 173명, P/Q/W/E/R 865개 항목에 연결했습니다. 26.21의 10월 22일 바루스 추가 패치도 포함합니다.
- 상세 수치·조건 2,071행: 공식 변경 436행, 변경 반영 계산값 472행, 기존 자료 1,163행. 검토 원본에 각 행의 출처를 기록했습니다.
- 피해량뿐 아니라 패시브 문장, 발동 조건, 재사용, 소모량, 대상별 피해 배율을 대조했습니다. 미스 포츈 패시브의 총 공격력 50~100%, 미니언 25~50%는 후속 변경을 찾지 못한 기존 자료로 유지합니다.
- 자료 부족·원문 충돌이 남은 43개 스킬은 검토 원본에 `partial`로 기록했습니다. 쉬바나 개편, 멜 Q 합계, 올라프 Q 랭크 누락, 티모 E 지속 피해 계수 등은 임의로 완성하지 않습니다.
- 추가 패치의 h4 챔피언 제목과 인라인 스킬 표기를 수집합니다. 일반 협곡 데이터에 다른 모드·아이템·정글 항목이 섞이지 않도록 경계를 수정했습니다.

## 데이터 구분과 한계

1. 현재 기본 능력치와 공식 요약: Riot Data Dragon 16.22.1 (게임 패치 26.22).
2. 상세 계수의 출발점: Meraki Analytics 보관본. 이미지 경로의 `15.15.1`은 모든 수치가 25.15에서 검증됐다는 뜻이 아닙니다. 후속 공식 변경을 적용했더라도 변경되지 않은 기존 값의 정확성을 모두 보장하지 않습니다.
3. 각 챔피언 JSON의 `details`는 검토한 통합 표시 자료입니다. `patch`는 공식 변경값, `derived`는 기존 식에 변경을 적용한 계산값, `baseline`은 기존 자료입니다. 원래 `formulas`는 보존합니다. 예전 `verified.json`은 하위 호환을 위한 대체 표시 자료입니다.
4. Data Dragon 공격력 성장값이 0으로 제공된 문제는 보관본과 이후 공식 변경으로 보완합니다. 확인할 수 없는 신규 챔피언은 성장값 미제공으로 표시합니다. 레벨 계산은 1~18이며 역할군 퀘스트 등 게임 내 추가 효과는 포함하지 않습니다.
5. 이전 패치의 능력치와 현재 공식 데이터가 충돌하는 6개 필드는 현재 Data Dragon을 유지하고 `statConflicts`와 화면 안내로 남깁니다. 다리우스 Q 재사용은 최신 패치의 9/8/7/6/4초를 표시합니다. 사거리 25000은 전역으로 단정하지 않습니다.
6. 패치 이력은 챔피언 섹션 기준입니다. 챔피언 이름이 없는 전역 변경, 별도 버그 수정, 다른 모드, 초기 서비스 기록은 빠질 수 있습니다. 실제 문서 수·실패 목록은 데이터 안내에 표시합니다. 수치 증감에 의한 상/하향 분류는 실제 게임 영향과 다를 수 있습니다.
7. 사이트는 수집 시점의 정적 스냅샷이며 자동 갱신은 연결되어 있지 않습니다.

## 데이터 재수집

Python 3와 `beautifulsoup4`가 필요합니다. API 키를 사용하지 않습니다.

```bash
python -m pip install -r requirements.txt
python scripts/collect_data.py
python scripts/fetch_assets.py
python scripts/collect_english.py
python scripts/build_localization.py
# 26.21까지 검토된 그룹을 재생성한 후 후속 공식 변경과 통합
python scripts/reconciled/build_group_1.py
python scripts/reconciled/build_group_2.py
python scripts/reconciled/build_group_3.py
python scripts/reconciled/build_group_4.py
python scripts/reconciled/build_group_5.py
python scripts/build_reconciled.py
```

`RIFT_CACHE`로 다운로드 임시 캐시 경로를 지정할 수 있습니다. 각 챔피언 JSON에 현재 공식 데이터 URL, 보관본 URL, 버전, 패치 이력을 남깁니다. 재수집 후 모든 변경 수치를 재검토해야 합니다. `scripts/reconciled/source-revisions.json`은 검토한 KO/EN 입력의 지문을 고정합니다. 입력이 바뀌면 `build_reconciled.py`가 거부합니다. 새 패치를 실제로 검토한 후에만 버전·날짜·생성기를 갱신하고 `python scripts/build_reconciled.py --record-review`로 검토 지문을 기록합니다. 26.22 변경과 과거 누락 사항의 검토 원본은 `scripts/reconciled/updates-26.22.json`에 있습니다. `RIFT_REFRESH_FROM=25.15`로 해당 패치 이후 문서를 재수집할 수 있습니다. 수집기는 검증값을 자동으로 최신이라고 바꾸지 않습니다. 새 패치가 추가되면 URL 형식과 HTML 파싱 결과도 검토해야 합니다. 영어 수집기는 한국어 목록에 저장된 버전을 사용하며, 영어와 한국어 문서의 수집 범위·기록 수는 다를 수 있습니다. `scripts/locales/ko-exact.json` 및 번역 생성기의 용어 사전도 신규 항목에 맞게 검토해야 합니다. 번역은 표시 문구에만 적용하고 원본 계수와 출처는 유지합니다.

## 검증

검증 의존성은 고정된 lockfile로 설치할 수 있습니다.

```bash
npm ci --prefix .github/ci
export RIFT_JSDOM="$PWD/.github/ci/node_modules/jsdom"
```

```bash
node --check dist/app.js
# jsdom 설치 경로를 RIFT_JSDOM으로 전달하거나 Node가 모듈을 찾을 수 있도록 설치
RIFT_JSDOM=/absolute/path/to/jsdom node scripts/verify.cjs
RIFT_JSDOM=/absolute/path/to/jsdom node scripts/verify_localization.cjs
python scripts/verify_data.py
# 26.21 추가 패치 및 26.22 스냅샷 대조
RIFT_JSDOM=/absolute/path/to/jsdom node scripts/verify_latest_patch.cjs
```

173명 전체의 양 언어 렌더링, 수치 동일성, 번역 누락, 검색·필터·능력치, 랜덤 시작과 공유 주소, 언어 선택 저장과 전환 상태, 뒤로/앞으로 가기, 한글 조합 입력, 모바일 검색, 네트워크 지연·실패·시간 초과를 DOM 기반으로 테스트합니다. 누적 업데이트의 실제 Chromium 미리보기로 수치·출처 카드와 한영 전환을 확인했습니다. 모바일 동작은 DOM 테스트로 확인했습니다. 외부 스킬 아이콘/일부 챔피언 배경과 Google Fonts는 네트워크에 의존하며 시스템 폰트 대체를 제공합니다. 챔피언 목록 이미지와 기본 아리 배경은 배포 파일에 포함됩니다.

## GitHub 자동 검증 및 웹 배포

공개 사이트는 https://rift-notes.khboy7777.chatgpt.site 에서 제공합니다. 별도로 **Vercel의 GitHub 연결**에 사용할 정적 배포 설정도 포함되어 있습니다. 현재 계정에서는 비공개 저장소의 GitHub Pages 사용이 지원되지 않아, Pages 배포 작업은 제거했습니다.

최초 연결은 저장소 소유자의 Vercel 계정에서 진행합니다.

1. [Vercel 새 프로젝트](https://vercel.com/new)에서 GitHub 계정을 연결합니다.
2. `baebaebuae/rift-notes`를 선택해 **Import**합니다. 목록에 없다면 GitHub 연동에 이 저장소의 접근을 허용합니다.
3. Root Directory는 저장소 루트(`./`)로 두고 **Deploy**합니다. `vercel.json`에 프레임워크(Other), 설치 명령, 검증 명령, 배포 폴더(`dist`)가 지정되어 있습니다.
4. 배포가 성공하면 Vercel 프로젝트에서 실제 웹 주소와 Production Branch가 `main`인지 확인합니다.

연결 이후에는 `main`에 코드를 반영할 때 Vercel이 자동으로 웹 검증을 실행하고, 성공한 `dist`만 배포합니다. PR에는 별도 미리보기를 생성할 수 있습니다. 실제 주소는 Vercel의 배포 결과에서 확인하며, 설정 파일을 추가하는 것만으로 계정 연결이나 첫 배포가 완료되지는 않습니다. 별도 서버나 저장소에 넣을 배포용 API 키는 필요하지 않습니다.

`.github/workflows/ci.yml`은 `main` 반영과 PR에서 Python 데이터 검증 및 `scripts/verify_web.sh`의 DOM·한영 전환·미리보기·패치 검증을 실행합니다. Vercel도 같은 웹 검증 스크립트를 사용하며, 실패하면 해당 배포가 중단됩니다.

Vercel의 설치·검증 단계를 로컬에서 재현하려면 다음 명령을 실행합니다.

```bash
npm ci --prefix .github/ci --no-audit --no-fund
bash scripts/verify_web.sh
```

로컬에서 같은 배포 디렉터리를 확인하려면 `python -m http.server 8000 --directory dist`를 사용합니다. 배포 시 데이터 재수집은 실행하지 않습니다.

## 파일 구성

- `dist/index.html`, `dist/styles.css`, `dist/app.js`: 화면과 동작
- `dist/data/*.json`: 한국어 데이터, 검토 수치 및 한국어 번역 사전
- `dist/data/en/*.json`: 같은 버전의 공식 영문 챔피언 데이터 및 영문 패치 기록
- `scripts/build_reconciled.py`, `scripts/reconciled/`, `scripts/reconcile_stats.py`: 누적 변경·계산·출처 검토와 표시 데이터 생성
- `scripts/collect_english.py`: 영어 데이터 수집 및 챔피언 항목·추가 패치 날짜 검증
- `scripts/build_localization.py`, `scripts/locales/ko-exact.json`: 한국어 표시 번역과 영문 검토 수치 생성
- `dist/data/patches.json`: 문서별 수집 결과
- `scripts/collect_data.py`: 공식 데이터 및 패치 수집/정규화
- `scripts/fetch_assets.py`: 공식 이미지 저장
- `.openai/hosting.json`: 정적 배포 설정

## 출처와 권리

게임 데이터와 이미지: Riot Games Data Dragon / League of Legends 공식 패치 노트.
세부 계수 보관본: Meraki Analytics `lolstaticdata` 및 League of Legends Wiki 기여자. 관련 Wiki 데이터는 CC BY-SA 3.0에 따라 출처와 변경 여부를 표시합니다. 사이트 하단에 Riot 비공식 팬 도구임을 표시합니다.
