# -*- coding: utf-8 -*-
"""通过 GitHub REST API 建仓 / 传文件 / 开 Pages / 触发流水线"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

OWNER = "cp6661"
REPO = "opc-workbench"
BRANCH = "main"
ROOT = r"D:/workbuddy 对话/一人公司工作台"

TEXT_FILES = [
    "index.html",
    "word-quiz.html",
    "data.js",
    "data.json",
    "manifest.json",
    "service-worker.js",
    "offline.html",
    "build_offline.py",
    "knowledge.json",
    "sync_data.py",
    ".github/workflows/daily-update.yml",
    ".github/workflows/sync-from-live.yml",
]
BIN_FILES = ["icon-192.png", "icon-512.png"]

T = os.environ["GH_TOKEN"]
HDR = {
    "Authorization": "Bearer " + T,
    "User-Agent": "wb",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def api(path, method="GET", data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        "https://api.github.com" + path, data=body, method=method, headers=HDR
    )
    try:
        raw = urllib.request.urlopen(req, timeout=60).read()
        return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return {"__err__": e.code, "body": e.read().decode("utf-8", "replace")[:500]}


def ensure_repo():
    r = api("/repos/%s/%s" % (OWNER, REPO))
    if "__err__" not in r:
        print("仓库已存在：", r["full_name"])
        return
    r = api("/user/repos", "POST", {
        "name": REPO,
        "description": "一人公司工作台 · 移动端 PWA（每日 08:00 自动更新）",
        "private": False,
        "auto_init": False,
    })
    if "__err__" in r:
        print("建仓失败：", r)
        sys.exit(1)
    print("仓库已创建：", r["full_name"], r.get("html_url"))


def put_file(p, msg):
    """用 contents API 写文件（空仓库也能用，会自动创建默认分支）"""
    full = os.path.join(ROOT, p.replace("/", os.sep))
    with open(full, "rb") as f:
        raw = f.read()
    b64 = base64.b64encode(raw).decode()
    path = "/repos/%s/%s/contents/%s" % (OWNER, REPO, p)
    exist = api(path + "?ref=" + BRANCH)
    data = {"message": msg, "content": b64, "branch": BRANCH}
    if "__err__" not in exist and isinstance(exist, dict) and exist.get("sha"):
        data["sha"] = exist["sha"]
    r = api(path, "PUT", data)
    if "__err__" in r:
        print("  ✗", p, r)
        return False
    print("  +", p, len(raw), "bytes")
    return True


def upload():
    ok = True
    for p in TEXT_FILES + BIN_FILES:
        ok = put_file(p, "初始化：一人公司工作台 + 每日 08:00 自动更新流水线") and ok
    if not ok:
        sys.exit(1)
    api("/repos/%s/%s" % (OWNER, REPO), "PATCH", {"default_branch": BRANCH})


def pages():
    r = api("/repos/%s/%s/pages" % (OWNER, REPO))
    if "__err__" not in r:
        print("Pages 已启用：", r.get("html_url"), "build_type=", r.get("build_type"))
        if r.get("build_type") != "workflow":
            api("/repos/%s/%s/pages" % (OWNER, REPO), "PUT", {"build_type": "workflow"})
        return
    r = api("/repos/%s/%s/pages" % (OWNER, REPO), "POST",
            {"build_type": "workflow", "source": {"branch": BRANCH, "path": "/"}})
    print("Pages 开启结果：", r if "__err__" in r else "OK " + str(r.get("html_url")))


def dispatch():
    r = api("/repos/%s/%s/actions/workflows/daily-update.yml/dispatches" % (OWNER, REPO),
            "POST", {"ref": BRANCH})
    print("触发流水线：", "OK" if "__err__" not in r else r)


if __name__ == "__main__":
    ensure_repo()
    upload()
    pages()
    dispatch()
    time.sleep(8)
    runs = api("/repos/%s/%s/actions/runs?per_page=1" % (OWNER, REPO))
    if runs.get("workflow_runs"):
        w = runs["workflow_runs"][0]
        print("最新运行：", w["status"], w["conclusion"], w.get("html_url"))
