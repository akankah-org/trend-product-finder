"""Kolektor TikTok via Apify parseforge (token di credential/apify.txt).

  python tiktok_apify.py --test   # 1 keyword, sedikit hasil
  python tiktok_apify.py --kw hijab,gamis --max 20 --region ID
"""
import datetime
import json
import os
import sys
import time
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
CRED = os.path.join(BASE, "credential")
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)
ACTOR = "parseforge~tiktok-scraper"


def key():
    for line in open(os.path.join(CRED, "apify.txt"), encoding="utf-8"):
        if line.startswith("APIFY_TOKEN="):
            v = line.strip().split("=", 1)[1]
            assert v and not v.startswith("ISI"), "token kosong"
            return v
    raise SystemExit("token tak ketemu")


def api(method, path, data=None, tok=""):
    base = ("https://api.apify.com/v2/datasets/" if path.startswith("/ds:")
            else f"https://api.apify.com/v2/acts/{ACTOR}")
    if path.startswith("/ds:"):
        path = path[4:]
    sep = "&" if "?" in path else "?"
    req = urllib.request.Request(
        base + path
        + (f"{sep}token={tok}" if method == "GET" else ""),
        data=json.dumps(data).encode() if data else None,
        method=method, headers={"Content-Type": "application/json"})
    if method != "GET":
        req.add_header("Authorization", f"Bearer {tok}")
    return json.load(urllib.request.urlopen(req, timeout=120))


def run(keywords, maks=10, region="ID"):
    tok = key()
    body = {"keywords": keywords, "hashtags": [],
            "maxResults": maks,
            "resultsPerPage": maks, "proxyCountryCode": region,
            "region": region}
    run = api("POST", "/runs", body, tok)["data"]
    rid, did = run["id"], run["defaultDatasetId"]
    print("run:", rid)
    for _ in range(30):
        time.sleep(10)
        st = api("GET", f"/runs/{rid}", None, tok)["data"]["status"]
        if st in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            print("status:", st)
            break
    else:
        print("TIMEOUT tunggu; cek manual:", rid)
        return []
    items = api("GET", f"/ds:{did}/items?limit={maks}&clean=true",
                None, tok)
    items = items if isinstance(items, list) else items.get("items", [])
    out = {"waktu": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
           "region": region, "run": rid, "items": items}
    p = os.path.join(DATA, f"tiktok_apify_{out['waktu']}.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(items)} video | tersimpan: {p}")
    for v in items[:5]:
        cap = (v.get('text') or v.get('description') or '')[:90]
        cap = cap.encode('ascii', 'replace').decode()
        print(f"  @{v.get('authorUsername', '?')} "
              f"f={v.get('authorFollowers', '?')} "
              f"| play={v.get('playCount')} like={v.get('likeCount')}")
        print(f"    {cap}")
    return items


if __name__ == "__main__":
    if "--test" in sys.argv:
        run(["hijab"], maks=5)
    else:
        kw, mx, rg = ["hijab"], 10, "ID"
        for i, a in enumerate(sys.argv):
            if a == "--kw" and i + 1 < len(sys.argv):
                kw = sys.argv[i + 1].split(",")
            if a == "--max" and i + 1 < len(sys.argv):
                mx = int(sys.argv[i + 1])
            if a == "--region" and i + 1 < len(sys.argv):
                rg = sys.argv[i + 1]
        run(kw, mx, rg)
