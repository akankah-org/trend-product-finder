# -*- coding: utf-8 -*-
"""Langkah 2: dork google-search74 per kategori naik -> hasil per kat."""
import io
import json
import re
import sys
import time

import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HOST = "google-search74.p.rapidapi.com"
KEY = open("E:/opencode/_rap74.key", encoding="utf-8").read().strip() \
    if __import__("os").path.exists("E:/opencode/_rap74.key") else ""
BASE = "E:/trend product finder"

KATEGORI = {
    "batik": "batik viral",
    "rok": "rok wanita viral",
    "celana-wanita": "celana wanita viral",
    "tunik": "tunik viral",
    "pashmina": "pashmina viral",
}
SITES = {"shopee": "site:shopee.co.id", "tiktok": "site:tiktok.com"}
H = {"X-RapidAPI-Key": KEY, "X-RapidAPI-Host": HOST}


def dork(q, limit=30):
    r = requests.get(f"https://{HOST}/", headers=H,
                     params={"query": q, "limit": limit,
                             "gl": "id", "hl": "id"}, timeout=45)
    if r.status_code != 200:
        print("  !", r.status_code, str(r.text)[:120])
        return []
    return (r.json() or {}).get("results") or []


out = {}
used = 0
for kat, kw in KATEGORI.items():
    out[kat] = []
    for site, d in SITES.items():
        q = f"{d} {kw}"
        res = dork(q)
        used += 1
        print(f"[{used}] {kat:14s} {site:7s} -> {len(res)}")
        for it in res:
            u = it.get("url", "")
            if not u.startswith("http"):
                continue
            out[kat].append({
                "site": site, "url": u,
                "name": (it.get("title") or "")[:140],
                "desc": (it.get("description") or "")[:300],
                "pos": it.get("position"),
            })
        time.sleep(1.2)

json.dump(out, open(BASE + "/data/_dork74.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for k, v in out.items():
    print(f"{k:14s} total {len(v)}")
print("pakai request:", used)
