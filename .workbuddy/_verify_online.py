# -*- coding: utf-8 -*-
import json, re, urllib.request, urllib.error, datetime

BASE = "https://93e14aa60a70466f9fe608234a38925e.app.workbuddy.host/"


def get(path):
    req = urllib.request.Request(
        BASE + path,
        headers={"User-Agent": "wb", "Cache-Control": "no-cache"},
    )
    try:
        r = urllib.request.urlopen(req, timeout=45)
        return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return type(e).__name__, str(e)


today = datetime.datetime.now().strftime("%Y-%m-%d")

st, body = get("data.js")
print("== online data.js ==")
print("HTTP        :", st, "| bytes:", len(body))
def parse(src):
    payload = src.split("=", 1)[1].strip().rstrip(";").strip()
    obj, _end = json.JSONDecoder().raw_decode(payload)
    return obj


obj = parse(body)
print("date        :", obj["date"], "| match today:", obj["date"] == today)
print("updateTime  :", obj["updateTime"])
print("updateTs    :", obj["updateTs"])
print("total       :", obj["total"])
print("ai_news     :", len(obj["ai_news"]))
print("tech_news   :", len(obj["tech_news"]))

st2, sw = get("service-worker.js")
print("== online service-worker.js ==")
print("HTTP        :", st2)
print("CACHE       :", (re.search(r"opc-v\d+", sw) or ["?"])[0])

st3, idx = get("index.html")
print("== online index.html ==")
print("HTTP        :", st3, "| bytes:", len(idx))
print("title hit   :", "一人公司工作台" in idx)

# 本地一致性核对
loc = parse(open("data.js", encoding="utf-8").read())
print("== local vs online ==")
print("identical   :", loc == obj)
