# 변경 이력

형식: `버전 (날짜) — 변경 요약`. 태그를 붙일 때마다 맨 위에 한 줄씩 추가합니다.

## v0.1.1 (2026-08-31)

- 탭 순서 확정: NGS(KRA) → 기능유전체(KEA) → 염기서열(KNA) → 유전체변이(KVar) → 단백체(KPOP)
- 빌드 시 탭 순서 출력 및 `manifest.json` 검증 추가 (id 중복·누락 파일 차단)

## v0.1 (2026-08-31)

- 최초 구성. 가이드 5종(KNA·KRA·KVar·KEA·KPOP)을 탭 하나로 통합
- 단일 HTML 번들 빌드 추가 (`dist/guide-v0.1.html`)
- `docs/kpop.html` 의 외부 추적 스크립트(`lc.getunicorn.org`) 제거
