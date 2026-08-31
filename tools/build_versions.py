#!/usr/bin/env python3
"""
버전별 사이트 빌드 (GitLab Pages용).

  public/            ← 기본 브랜치(main)의 최신 내용
  public/v/<tag>/    ← 태그별 과거 버전 (v* 태그)
  public/versions.json

각 태그는 git worktree 로 따로 꺼내 그 시점의 build.py 로 빌드하므로,
과거 버전은 당시 화면 그대로 보존된다.

  python3 tools/build_versions.py --out public --keep 10
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAG_GLOB = "v*"


def sh(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(args, cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def tags(keep: int) -> list[str]:
    out = sh("git", "tag", "--list", TAG_GLOB, "--sort=-v:refname")
    found = [t for t in out.splitlines() if t.strip()]
    return found[:keep]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="public")
    ap.add_argument("--keep", type=int, default=10, help="유지할 과거 버전 개수")
    args = ap.parse_args()

    out = (ROOT / args.out).resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    tag_list = tags(args.keep)
    ver_arg = ",".join(tag_list)
    print(f"과거 버전 태그: {tag_list or '(없음)'}")

    # 1) 최신(main)
    subprocess.run([sys.executable, "build.py",
                    "--out", str(out), "--dist", str(ROOT / "dist"),
                    "--self", "latest", "--versions", ver_arg],
                   cwd=ROOT, check=True)

    # 2) 태그별
    for tag in tag_list:
        dest = out / "v" / tag
        with tempfile.TemporaryDirectory() as tmp:
            wt = Path(tmp) / "wt"
            sh("git", "worktree", "add", "--detach", str(wt), tag)
            try:
                if not (wt / "build.py").exists():
                    print(f"  ! {tag}: build.py 없음 — 건너뜀")
                    continue
                subprocess.run([sys.executable, "build.py",
                                "--out", str(dest), "--skip-bundle",
                                "--self", tag, "--versions", ver_arg],
                               cwd=wt, check=True)
            finally:
                subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                               cwd=ROOT, check=False)

    (out / "versions.json").write_text(
        json.dumps({"latest": "main", "tags": tag_list},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"완료: {out}")


if __name__ == "__main__":
    main()
