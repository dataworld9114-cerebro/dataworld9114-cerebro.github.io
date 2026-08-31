#!/usr/bin/env python3
"""
생명연 데이터 등록 가이드 — 탭 통합 화면 빌드 스크립트

두 가지 산출물을 만든다.
  1) site   : public/  (index.html + docs/*.html)  — GitLab Pages / 웹서버용
  2) bundle : dist/guide-<release>.html            — 문서 5종을 모두 품은 단일 HTML
              (Pages가 없거나, 오프라인/메일 배포가 필요할 때)

사용 예)
  python3 build.py                                   # 둘 다 생성
  python3 build.py --self v0.1 --versions v0.1,v0.2  # 버전 선택 메뉴 포함
  python3 build.py --skip-bundle
"""

import argparse
import base64
import json
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "tools" / "shell_template.html"
MANIFEST = ROOT / "manifest.json"
KST = timezone(timedelta(hours=9))


def version_links(self_name: str, tags: list[str]) -> list[dict]:
    """버전 선택 메뉴 항목. self_name 이 'latest' 면 루트 빌드, 아니면 public/v/<tag>/ 빌드."""
    at_root = self_name == "latest"
    items = [{
        "label": "최신 (main)",
        "href": "./" if at_root else "../../",
        "current": at_root,
    }]
    for t in tags:
        items.append({
            "label": t,
            "href": (f"v/{t}/" if at_root else f"../{t}/"),
            "current": (not at_root and t == self_name),
        })
    return items


def render(manifest: dict, mode: str, self_name: str, tags: list[str]) -> str:
    tpl = TEMPLATE.read_text(encoding="utf-8")

    docs = []
    for d in manifest["docs"]:
        docs.append({
            "id": d["id"],
            "label": d["label"],
            # site 모드는 상대경로 그대로, bundle 모드는 파일 경로를 쓰지 않는다
            "file": ("docs/" + Path(d["file"]).name) if mode == "site" else "",
            "version": d.get("version", ""),
            "updated": d.get("updated", ""),
            "note": d.get("note", ""),
        })

    cfg = {
        "site_title": manifest["site_title"],
        "release": manifest.get("release", ""),
        "mode": mode,
        "self": self_name,
        "built_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M KST"),
        "versions": version_links(self_name, tags),
        "docs": docs,
    }

    embedded = ""
    if mode == "bundle":
        parts = []
        for d in manifest["docs"]:
            raw = (ROOT / d["file"]).read_bytes()
            b64 = base64.b64encode(raw).decode("ascii")
            parts.append(
                f'<script type="text/plain" id="src-{d["id"]}">{b64}</script>'
            )
        embedded = "\n".join(parts)

    return (tpl
            .replace("{{SITE_TITLE}}", manifest["site_title"])
            .replace("{{CONFIG_JSON}}", json.dumps(cfg, ensure_ascii=False))
            .replace("{{EMBEDDED_DOCS}}", embedded))


def build_site(manifest: dict, out: Path, self_name: str, tags: list[str]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    docs_out = out / "docs"
    docs_out.mkdir(exist_ok=True)
    for d in manifest["docs"]:
        shutil.copy2(ROOT / d["file"], docs_out / Path(d["file"]).name)
    (out / "index.html").write_text(
        render(manifest, "site", self_name, tags), encoding="utf-8")
    print(f"[site]   {out}/index.html  (문서 {len(manifest['docs'])}종)")


def build_bundle(manifest: dict, out_dir: Path, self_name: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    rel = manifest.get("release", "dev") if self_name == "latest" else self_name
    path = out_dir / f"guide-{rel}.html"
    path.write_text(render(manifest, "bundle", self_name, []), encoding="utf-8")
    print(f"[bundle] {path}  ({path.stat().st_size/1024/1024:.2f} MB)")
    return path


def validate(manifest: dict) -> None:
    """manifest.json 실수를 빌드 전에 잡는다. 탭 순서도 함께 출력한다."""
    docs = manifest.get("docs") or []
    if not docs:
        raise SystemExit("오류: manifest.json 의 docs 배열이 비어 있습니다.")

    problems, seen_id, seen_file = [], set(), set()
    for i, d in enumerate(docs, 1):
        for key in ("id", "label", "file"):
            if not d.get(key):
                problems.append(f"{i}번째 항목에 '{key}' 가 없습니다.")
        did, dfile = d.get("id"), d.get("file")
        if did in seen_id:
            problems.append(f"id 가 중복됩니다: '{did}' (탭 링크 #{did} 가 충돌합니다)")
        seen_id.add(did)
        if dfile in seen_file:
            problems.append(f"같은 파일이 두 번 등록되었습니다: '{dfile}'")
        seen_file.add(dfile)
        if dfile and not (ROOT / dfile).exists():
            problems.append(f"파일이 없습니다: '{dfile}' (docs/ 에 넣으셨나요?)")

    if problems:
        raise SystemExit("manifest.json 확인이 필요합니다:\n  - " + "\n  - ".join(problems))

    order = "  →  ".join(f"{i}.{d['label']}" for i, d in enumerate(docs, 1))
    print(f"[탭 순서] {order}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="public", help="site 출력 디렉터리")
    ap.add_argument("--dist", default="dist", help="bundle 출력 디렉터리")
    ap.add_argument("--self", dest="self_name", default="latest",
                    help="'latest' 또는 이 빌드가 대표하는 태그명")
    ap.add_argument("--versions", default="",
                    help="선택 메뉴에 넣을 태그 목록 (쉼표 구분, 최신순)")
    ap.add_argument("--skip-bundle", action="store_true")
    ap.add_argument("--skip-site", action="store_true")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate(manifest)
    tags = [t.strip() for t in args.versions.split(",") if t.strip()]

    if not args.skip_site:
        build_site(manifest, Path(args.out), args.self_name, tags)
    if not args.skip_bundle:
        build_bundle(manifest, Path(args.dist), args.self_name)


if __name__ == "__main__":
    main()
