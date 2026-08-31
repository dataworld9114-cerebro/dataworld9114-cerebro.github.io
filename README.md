# 생명연 데이터 등록 인터랙티브 가이드 (탭 통합)

유전체·기능유전체·단백체 등 데이터 등록 가이드 HTML 5종을 **탭 하나로 묶어** 보고,
GitLab 에서 **버전을 관리**하기 위한 저장소입니다.

탭 순서는 아래와 같이 고정되어 있습니다 (`manifest.json` 배열 순서).

| # | 탭 | 파일 | 내용 |
|---|---|---|---|
| 1 | NGS 유전체 (KRA) | `docs/kra-ngs.html` | K-BDS KRA |
| 2 | 기능유전체 (KEA) | `docs/kea.html` | 기능유전체 |
| 3 | 염기서열 (KNA) | `docs/kna.html` | 유전체 데이터 등록 — 염기서열 |
| 4 | 유전체변이 (KVar) | `docs/kvar.html` | 유전체 변이 |
| 5 | 단백체 (KPOP) | `docs/kpop.html` | 단백체, KEA 형식 |

원본 HTML 은 **한 글자도 고치지 않고** 그대로 둡니다. 탭 화면은 각 문서를
`iframe` 으로 불러오기만 하므로, 문서 안의 스타일·스크립트가 서로 충돌하지 않습니다.
(예외: `kpop.html` 에 외부 도메인 `lc.getunicorn.org` 를 부르는 추적 스크립트 한 줄이
들어 있어 제거했습니다. 폐쇄망에서는 이 줄 때문에 로딩이 지연될 수 있습니다.)

## 구조

```
manifest.json          탭 목록·라벨·문서별 버전  ← 탭을 늘리거나 이름을 바꿀 때 여기만 수정
docs/*.html            원본 가이드 문서
tools/shell_template.html   탭 껍데기 템플릿
build.py               빌드 스크립트
tools/build_versions.py     버전별 사이트 빌드 (Pages 용)
tools/release.sh       러너 없이 배포본 만들기 (releases/ 에 보관)
.gitlab-ci.yml         GitLab CI 설정 (러너가 생기면 자동 동작)
.github/workflows/pages.yml   GitHub Pages 배포 설정
```

## 빌드

```bash
python3 build.py                 # public/ (사이트) + dist/ (단일 파일) 생성
python3 -m http.server -d public # http://localhost:8000 에서 확인
```

산출물은 두 가지입니다.

- **`public/`** — `index.html` + `docs/`. GitLab Pages나 사내 웹서버에 그대로 올립니다.
- **`dist/guide-<버전>.html`** — 문서 5종을 모두 품은 **단일 HTML**.
  파일 하나만 있으면 되므로 메일 첨부·USB·공유폴더로 배포해도 되고,
  더블클릭으로 오프라인에서 열립니다. Pages 를 못 쓰는 경우의 대안입니다.

## 문서 수정 절차

1. 브랜치 생성: `git checkout -b docs/kvar-2026-09`
2. `docs/*.html` 수정, `manifest.json` 의 해당 문서 `version`·`updated` 갱신
3. 푸시 → **Merge Request** 생성 → 리뷰 → 병합
   - MR 파이프라인의 `build_bundle` 아티팩트를 내려받으면 병합 전에 실물 확인 가능
4. 병합되면 Pages 최신본이 자동 갱신

## 버전 관리 규칙

- **일상 변경**은 커밋·MR 로만 관리합니다. GitLab 의 `Blame`/`History`/버전 비교
  기능으로 "누가 언제 어느 항목을 바꿨는지" 를 그대로 추적할 수 있습니다.
- **공식 배포본**은 태그로 고정합니다.

```bash
git tag -a v0.2 -m "KVar Part3 항목 추가"
git push origin v0.2
```

태그를 푸시하면

- `public/v/v0.2/` 경로에 그 시점 화면이 **영구 보존**되고 (탭 화면 우측 상단 *버전* 메뉴로 이동)
- 릴리스가 생성되며 단일 HTML 번들이 첨부됩니다.

기본값으로 최근 10개 태그를 보존합니다 (`tools/build_versions.py --keep`).

### 문서별 버전과 저장소 버전

저장소 태그(`v0.2`)는 **전체 묶음**의 버전이고, `manifest.json` 의 `version` 은
**문서 하나하나**의 버전입니다. 탭 화면 상단 회색 줄에 문서별 버전·수정일이 표시되므로,
"KVar 만 0.3 으로 올라갔다" 같은 상황도 그대로 보여줄 수 있습니다.

## 열람 방법

| 상황 | 방법 |
|---|---|
| Pages 사용 가능 | `https://<그룹>.<pages도메인>/<프로젝트>/` — 팀 내부만 열려면 *Pages 액세스 제한* 을 켭니다 |
| Pages 없음 + Runner 있음 | 태그를 붙이면 파이프라인이 `dist/guide-v0.2.html` 을 만들고 만료 없이 보관합니다. 릴리스 페이지에서 내려받아 엽니다 |
| Pages 없음 + Runner 없음 | 각자 `python3 build.py` 를 돌리거나, 담당자가 만든 `guide-v0.2.html` 을 공유폴더에 올립니다 |
| 사내 웹서버 있음 | `public/` 을 그대로 복사하거나, CI 마지막 단계에서 rsync |

### 러너(CI)도 Pages 도 없을 때 — 현재 KBDS_INFO 환경

파이프라인이 돌지 않으므로 **담당자 한 명이 로컬에서 배포본을 만들어 커밋**합니다.
스크립트 한 줄이면 됩니다.

```bash
./tools/release.sh v0.2 "KVar Part3 항목 추가"
git push origin HEAD
git push origin v0.2
```

하는 일은 세 가지입니다.

1. `manifest.json` 의 `release` 를 새 버전으로 갱신
2. 단일 HTML 을 `releases/guide-v0.2.html` 로 생성 — **저장소에 함께 보관**됩니다
3. 커밋과 태그 생성 (푸시는 직접 확인 후)

팀원은 GitLab 에서 `releases/guide-v0.2.html` 파일 페이지의 **Download** 버튼으로 내려받아
더블클릭하면 됩니다. (저장소 화면에서 바로 열면 소스 코드로 보입니다 — 반드시 내려받아서 여세요.)

버전별 배포본이 `releases/` 에 그대로 쌓이므로, 과거 버전을 보려면 그 파일을 내려받으면 됩니다.
한 버전당 약 1.1&nbsp;MB 이므로 10개를 모아도 11&nbsp;MB 수준입니다.

푸시한 뒤 웹에서 **배포 &rsaquo; Releases &rsaquo; Create a new release** 로 그 태그를 골라 릴리스를
만들어 두면 배포 이력이 한눈에 정리됩니다 (러너 없이 웹 UI 만으로 됩니다).

### Pages 가 없을 때

`.gitlab-ci.yml` 맨 위 `PAGES_ENABLED: "false"` 가 기본값이라 **아무것도 고칠 필요 없이** 그대로 씁니다.
`pages` 잡은 실행되지 않고, 커밋·MR·태그·되돌리기 같은 버전 관리는 전부 그대로 동작합니다.
과거 버전은 `/v/<tag>/` URL 대신 **태그별 릴리스에 첨부된 단일 HTML** 이 대신합니다.

나중에 Pages 가 열리면 프로젝트 &rsaquo; 설정 &rsaquo; CI/CD &rsaquo; 변수에서 `PAGES_ENABLED` 를 `true` 로
바꾸기만 하면 됩니다. 파일 수정은 필요 없습니다.

> GitLab 저장소에서 HTML 파일을 눌러 보는 방식은 동작하지 않습니다. GitLab 은
> 보안상 저장소 안의 HTML 을 렌더링하지 않고 소스 코드로만 보여줍니다.
> 반드시 Pages·웹서버·단일 파일 중 하나를 거쳐야 합니다.

## GitHub 에서 쓰려면

`index.html` 은 이미 만들어집니다. 저장소에 없는 이유는 **빌드 결과물**이기 때문입니다 —
`python3 build.py` 를 돌리면 `public/index.html` 이 생기고, 그 파일이 탭 화면입니다.
GitHub Pages 에는 이 `public/` 을 올립니다.

### 설정 순서

1. GitHub 에 새 저장소를 만들고 이 파일들을 푸시합니다.
2. 저장소 **Settings › Pages › Build and deployment › Source** 를 **GitHub Actions** 로 지정합니다.
3. 끝입니다. `.github/workflows/pages.yml` 이 이미 들어 있어, `main` 에 푸시하면 자동 배포됩니다.

주소는 `https://<계정>.github.io/<저장소>/` 이고, 과거 버전은 `/v/v0.1/` 로 남습니다.
GitLab 쪽 설정(`.gitlab-ci.yml`)과 공존하므로 둘 다 두어도 서로 간섭하지 않습니다.

> **주의:** Pages 소스를 `main` 브랜치의 `/docs` 폴더로 고르면 안 됩니다.
> 이 저장소의 `docs/` 는 빌드 결과가 아니라 **원본 가이드 문서** 폴더라서,
> 그렇게 하면 탭 화면 없이 개별 문서만, 그것도 `index.html` 이 없어 404 가 납니다.
> 반드시 **GitHub Actions** 를 고르세요.

### 공개 범위 — 먼저 확인할 것

GitHub Pages 로 올린 사이트는 **주소를 아는 사람이면 누구나 볼 수 있습니다.**

| 플랜 | 가능 여부 |
|---|---|
| Free | 공개(public) 저장소에서만 Pages 사용 가능 |
| Pro · Team | 비공개(private) 저장소에서도 Pages 사용 가능. 단 **사이트는 여전히 공개** |
| Enterprise Cloud | 사이트 접근을 조직 구성원으로 제한 가능 |

기관 내부 문서라면 이 점을 먼저 정리해야 합니다. 저장소를 비공개로 두어도 Pages 주소는
열려 있다는 것이 핵심입니다.

## 탭 추가하기

1. HTML 파일을 `docs/` 에 넣습니다. (파일명은 소문자·영문으로: `docs/kmap.html`)
2. `manifest.json` 의 `docs` 배열에 **원하는 자리**에 한 항목을 끼워 넣습니다.
3. `python3 build.py` 로 확인하고 커밋 → 푸시. 끝입니다.

```json
{ "id": "kmap", "label": "대사체 (KMAP)", "file": "docs/kmap.html",
  "version": "v0.1", "updated": "2026-09-15", "note": "대사체 데이터 등록" }
```

| 필드 | 뜻 |
|---|---|
| `id` | 탭 링크 주소(`#kmap`). 영문 소문자, 중복 불가. 한 번 정하면 바꾸지 않는 게 좋습니다 (공유된 링크가 깨집니다) |
| `label` | 탭에 보이는 이름 |
| `file` | `docs/` 아래 경로 |
| `version` / `updated` | 화면 상단 회색 줄에 표시되는 **문서별** 버전·수정일 |
| `note` | 그 옆에 붙는 한 줄 설명 (생략 가능) |

## 탭 순서

**`manifest.json` 의 `docs` 배열에 적힌 순서가 그대로 탭 순서입니다.** 이름순·파일명순으로
자동 정렬하지 않으므로, 배열의 항목 순서만 바꾸면 원하는 순서가 고정됩니다.

빌드하면 확정된 순서를 출력해 주므로 커밋 전에 눈으로 확인할 수 있습니다.

```
$ python3 build.py
[탭 순서] 1.NGS 유전체 (KRA)  →  2.기능유전체 (KEA)  →  3.염기서열 (KNA)  →  4.유전체변이 (KVar)  →  5.단백체 (KPOP)
```

`id` 중복, 빠진 파일, 같은 파일 중복 등록은 빌드가 오류로 잡아내고 멈추므로,
잘못된 상태가 Pages 에 배포되지 않습니다.

> 탭 이름·`id` 는 K-BDS 서브 저장소 코드를 그대로 쓰는 것을 권합니다.
> 대사체는 **KMAP**(Korea Metabolomics data repository, `https://kbds.re.kr/KMAP`) 입니다.

## 참고

- 탭 상태는 주소의 `#kvar` 로 남습니다. 특정 탭을 바로 여는 링크를 공유할 수 있습니다.
- 문서는 탭을 처음 누를 때 불러옵니다(지연 로딩). 5종을 모두 열어도 브라우저 부담이 적습니다.
