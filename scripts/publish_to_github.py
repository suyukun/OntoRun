#!/usr/bin/env python3
"""Publish OntoRun's curated public content to GitHub via the Git Data API.

WHY this exists:
  - github.com's git smart-HTTP is unreachable from some networks (e.g. China),
    while api.github.com works reliably -> push via the Git Data API instead.
  - The public repo carries ONLY our own systematic content (whitelist below):
    no scraped/copied material (Palantir docs, B站 notes, other projects), no
    internal handoffs, and never any secrets. The whitelist is the single
    source of truth for "what is public".

USAGE:
  python scripts/publish_to_github.py             # push current whitelisted files
  python scripts/publish_to_github.py --dry-run   # show what would be pushed, push nothing
  python scripts/publish_to_github.py -m "msg"    # custom commit message
  python scripts/publish_to_github.py --repo suyukun/OntoRun

TOKEN: env GITHUB_TOKEN, else ~/.dsh/.credentials.yaml -> GITHUB_TOKEN
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# WHITELIST MANIFEST — the single source of truth for what goes public.
# Edit this (not random dirs) when deciding what should be on GitHub.
# ---------------------------------------------------------------------------
EXACT_FILES = {
    "README.md", "LICENSE", ".gitignore",
    "requirements.txt", "pyproject.toml",
    "方向与战略_v0.2.md",
    "docs/白皮书_v0.1.md", "docs/技术方案_v0.1.md",
    "docs/演示脚本_v0.1.md", "docs/learn-in-public_v0.1.md",
    "docs/试用与成果导览_v0.1.md",
    "research/palantir-ontology.md",
    "data/seed_retail_source.py",
    "scripts/gen_agent_tools_golden.py",
    "scripts/publish_to_github.py",
    "scripts/run_gates.sh",
    ".github/workflows/ci.yml",
}
DIR_PREFIXES = ("src/", "web/", "tests/")


def is_public(path: str) -> bool:
    return path in EXACT_FILES or any(path.startswith(d) for d in DIR_PREFIXES)


# High-confidence secret patterns: abort the push if any public file matches.
SECRET_PATTERNS = [
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "GitHub PAT"),
    (re.compile(r"gho_[A-Za-z0-9]{20,}"), "GitHub OAuth token"),
    (re.compile(r"ghs_[A-Za-z0-9]{20,}"), "GitHub server token"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI/DeepSeek-style API key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY"), "private key"),
]

DEFAULT_REPO = "suyukun/OntoRun"


def resolve_token() -> str:
    tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if tok:
        return tok
    path = os.path.expanduser("~/.dsh/.credentials.yaml")
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            d = yaml.safe_load(f) or {}
        tok = d.get("GITHUB_TOKEN", "").strip()
        if tok:
            return tok
    except Exception as e:  # noqa: BLE001
        print(f"warn: could not read {path}: {e}", file=sys.stderr)
    sys.exit("ERROR: no GITHUB_TOKEN (set env GITHUB_TOKEN or ~/.dsh/.credentials.yaml)")


def req(token: str, method: str, url: str, payload=None, retries=6):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Authorization": "token " + token, "Accept": "application/vnd.github+json"}
    last = None
    for i in range(retries):
        try:
            r = urllib.request.Request(url, data=data, method=method, headers=headers)
            with urllib.request.urlopen(r, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:300]
            if e.code == 404:
                return {"_404": body}
            last = "HTTP " + str(e.code) + " " + body
        except Exception as e:  # noqa: BLE001
            last = repr(e)
        time.sleep(3 * (i + 1))
    raise RuntimeError(f"request failed {method} {url}: {last}")


def tracked_files():
    out = subprocess.check_output(["git", "ls-files", "-s", "-z"])
    files = []
    for rec in out.split(b"\x00"):
        if not rec:
            continue
        text = rec.decode("utf-8")
        meta, path = text.split("\t", 1)
        files.append((meta.split()[0], path))
    return files


def scan_for_secrets(files):
    bad = []
    for _, path in files:
        with open(path, "rb") as f:
            raw = f.read()
        text = None
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            pass
        if text is None:
            continue
        for rx, name in SECRET_PATTERNS:
            if rx.search(text):
                bad.append((path, name))
    return bad


def create_blobs(token, api, files):
    blob_sha = {}
    start = time.time()
    for i, (mode, p) in enumerate(files):
        with open(p, "rb") as f:
            raw = f.read()
        try:
            content = raw.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            content = base64.b64encode(raw).decode()
            encoding = "base64"
        r = req(token, "POST", api + "/git/blobs", {"content": content, "encoding": encoding})
        blob_sha[p] = r["sha"]
        if (i + 1) % 100 == 0:
            print(f"  blobs {i + 1}/{len(files)} ({int(time.time() - start)}s)", flush=True)
    return blob_sha


def build_tree(token, api, files, blob_sha):
    children = defaultdict(list)
    dirs = set()
    for mode, p in files:
        parts = p.split("/")
        fmode = "100755" if mode == "100755" else "100644"
        children["/".join(parts[:-1])].append((parts[-1], fmode, blob_sha[p]))
        for i in range(1, len(parts)):
            dirs.add("/".join(parts[:i]))
    tree_sha = {}

    def get_or_create(dirpath):
        if dirpath in tree_sha:
            return tree_sha[dirpath]
        entries = []
        for name, fmode, sha in children.get(dirpath, []):
            entries.append({"path": name, "mode": fmode, "type": "blob", "sha": sha})
        for sub in sorted(dirs):
            parent = "/".join(sub.split("/")[:-1])
            if parent == dirpath:
                entries.append({"path": sub.split("/")[-1], "mode": "040000",
                                "type": "tree", "sha": get_or_create(sub)})
        r = req(token, "POST", api + "/git/trees", {"tree": entries})
        tree_sha[dirpath] = r["sha"]
        return r["sha"]

    return get_or_create("")


def main():
    ap = argparse.ArgumentParser(description="Publish OntoRun curated content to GitHub")
    ap.add_argument("--dry-run", action="store_true", help="list what would be pushed, push nothing")
    ap.add_argument("-m", "--message", default=None, help="commit message (default: sync message)")
    ap.add_argument("--repo", default=DEFAULT_REPO, help=f"owner/repo (default: {DEFAULT_REPO})")
    args = ap.parse_args()

    token = resolve_token()
    api = "https://api.github.com/repos/" + args.repo

    all_files = tracked_files()
    public = [(m, p) for (m, p) in all_files if is_public(p)]
    private = sorted(p for (m, p) in all_files if not is_public(p))
    print(f"tracked={len(all_files)}  public={len(public)}  private={len(private)}")

    if args.dry_run:
        print("\nPUBLIC (would push):")
        for _, p in sorted(public):
            print("  " + p)
        print(f"\nPRIVATE (never pushed): {len(private)} files")
        for p in private[:15]:
            print("  " + p)
        if len(private) > 15:
            print(f"  ... and {len(private) - 15} more")
        return 0

    secrets = scan_for_secrets(public)
    if secrets:
        for path, name in secrets:
            print(f"ABORT: secret pattern ({name}) in {path}", file=sys.stderr)
        sys.exit("Refusing to push: potential secrets found. Fix and retry.")

    # current remote HEAD (bootstrap if the repo is empty)
    head_resp = req(token, "GET", api + "/git/ref/heads/main")
    if "_404" in head_resp or "object" not in head_resp:
        print("repo has no main ref -> bootstrapping with README via Contents API")
        readme = "README.md"
        with open(readme, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        req(token, "PUT", api + "/contents/README.md",
            {"message": "chore: bootstrap repo with README", "content": b64})
        head_resp = req(token, "GET", api + "/git/ref/heads/main")
    head = head_resp["object"]["sha"]
    print("remote head:", head)

    print(f"creating {len(public)} blobs ...")
    blob_sha = create_blobs(token, api, public)
    print("building tree ...")
    root = build_tree(token, api, public, blob_sha)
    print("root tree:", root)

    # skip if tree unchanged vs remote head
    head_commit = req(token, "GET", api + "/git/commits/" + head)
    if head_commit.get("tree", {}).get("sha") == root:
        print("nothing to push: public tree already matches remote HEAD")
        return 0

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    name = subprocess.check_output(["git", "config", "user.name"], text=True).strip() or "suyukun"
    email = subprocess.check_output(["git", "config", "user.email"], text=True).strip() or "smashup@163.com"
    who = {"name": name, "email": email, "date": now}
    msg = args.message or f"sync: update public repo ({len(public)} files, {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')})"
    r = req(token, "POST", api + "/git/commits",
            {"message": msg, "tree": root, "parents": [head], "author": who, "committer": who})
    commit = r["sha"]
    print("commit:", commit)

    req(token, "PATCH", api + "/git/refs/heads/main", {"sha": commit, "force": True})
    print("ref updated: refs/heads/main ->", commit)

    tree = req(token, "GET", api + f"/git/trees/{commit}?recursive=1")
    total = len([t for t in tree.get("tree", []) if t["type"] == "blob"])
    print(f"VERIFIED: {total} files live on https://github.com/{args.repo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
