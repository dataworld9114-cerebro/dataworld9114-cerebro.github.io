#!/usr/bin/env bash
# 러너(CI) 없이 배포본을 만드는 스크립트.
#
#   ./tools/release.sh v0.2 "KVar Part3 항목 추가"
#
# 하는 일
#   1) manifest.json 의 release 를 새 버전으로 갱신
#   2) 단일 HTML 을 releases/guide-<버전>.html 로 생성 (저장소에 함께 보관)
#   3) 커밋 · 태그까지 만들고, 마지막에 푸시 명령을 안내
#
# 푸시는 자동으로 하지 않는다. 내용을 확인한 뒤 직접 푸시할 것.

set -euo pipefail
cd "$(dirname "$0")/.."

VERSION="${1:-}"
MESSAGE="${2:-}"

if [[ -z "$VERSION" ]]; then
  echo "사용법: ./tools/release.sh <버전> [설명]"
  echo "예)     ./tools/release.sh v0.2 \"KVar Part3 항목 추가\""
  exit 1
fi
if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]; then
  echo "오류: 버전은 v0.2 또는 v0.2.1 형식으로 적어주세요. (입력값: $VERSION)"
  exit 1
fi
if git rev-parse "$VERSION" >/dev/null 2>&1; then
  echo "오류: 태그 $VERSION 이 이미 있습니다."
  exit 1
fi
if [[ -n "$(git status --porcelain -- docs manifest.json)" ]]; then
  echo "안내: docs/ 또는 manifest.json 에 커밋하지 않은 변경이 있습니다. 이번 배포본에 함께 포함됩니다."
fi

MESSAGE="${MESSAGE:-$VERSION 배포}"

python3 - "$VERSION" <<'PY'
import io, json, sys
version = sys.argv[1]
m = json.load(io.open('manifest.json', encoding='utf-8'))
m['release'] = version
io.open('manifest.json', 'w', encoding='utf-8').write(
    json.dumps(m, ensure_ascii=False, indent=2) + "\n")
print(f"manifest.json release → {version}")
PY

mkdir -p releases
python3 build.py --skip-site --dist releases

BUNDLE="releases/guide-${VERSION}.html"
[[ -f "$BUNDLE" ]] || { echo "오류: $BUNDLE 이 생성되지 않았습니다."; exit 1; }

git add manifest.json docs "$BUNDLE"
git commit -m "release ${VERSION}: ${MESSAGE}"
git tag -a "$VERSION" -m "$MESSAGE"

cat <<EOF

배포본이 준비되었습니다.
  파일 : $BUNDLE  ($(du -h "$BUNDLE" | cut -f1))
  태그 : $VERSION

아래 명령으로 올리세요.
  git push origin HEAD
  git push origin $VERSION

푸시 후 GitLab 웹에서
  배포(Deploy) > Releases > Create a new release 로 태그 $VERSION 을 선택해
  릴리스를 만들어 두면 배포 이력이 한눈에 정리됩니다.
EOF
