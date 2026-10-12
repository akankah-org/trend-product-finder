"""Kolektor TikTok Trends via RapidAPI JNX (10/bln! hemat).

  python tiktok_rapid.py --once [--region ID]

Budget: 8/10 per bulan (credential/usage_tiktok.json).
Sumber autofocus: hashtag trending + views (BUKAN produk langsung;
produk/toko butuh pencarian lanjutan).
"""
import datetime
import json
import os
import sys

try:
    import requests
except ImportError:
    sys.exit("butuh requests: pip install requests")

BASE = os.path.dirname(os.path.abspath(__file__))
CRED = os.path.join(BASE, "credential")
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

BATAS_BULANAN = 8
HOST = "real-time-tiktok-analytics-viral-trends-api.p.rapidapi.com"
ROUTE = "/api/v1/tiktok/trends"


def key():
    k = os.environ.get("RAPIDAPI_KEY", "")
    if not k:
        for line in open(os.path.join(CRED, "rapidapi_shopee.txt"),
                         encoding="utf-8"):
            if line.startswith("RAPIDAPI_KEY="):
                k = line.strip().split("=", 1)[1]
    assert k and not k.startswith("ISI"), "RAPIDAPI_KEY kosong"
    return k


def pakai(n=1):
    p = os.path.join(CRED, "usage_tiktok.json")
    try:
        u = json.load(open(p, encoding="utf-8"))
    except Exception:
        u = {}
    bln = datetime.datetime.now().strftime("%Y-%m")
    if u.get(bln, 0) + n > BATAS_BULANAN:
        raise SystemExit(f"budget habis ({u.get(bln, 0)}/{BATAS_BULANAN})")
    u[bln] = u.get(bln, 0) + n
    json.dump(u, open(p, "w", encoding="utf-8"))
    return u[bln]


def fetch(region="ID"):
    k = key()
    r = requests.get(f"https://{HOST}{ROUTE}",
                     params={"country": region},
                     headers={"X-RapidAPI-Key": k,
                              "X-RapidAPI-Host": HOST},
                     timeout=150)
    r.raise_for_status()
    pakai(1)
    return r.json()


def snapshot(region="ID"):
    d = fetch(region)
    items = d.get("data", [])
    out = {"waktu": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
           "region": region, "items": items}
    p = os.path.join(DATA, f"tiktok_{out['waktu']}.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(items)} hashtag | tersimpan: {p}")
    for h in items[:10]:
        print(f"  #{h.get('Rank')} {h.get('Hashtag')} "
              f"({h.get('Country')}) views={h.get('Video Views')}")


if __name__ == "__main__":
    reg = "ID"
    for i, a in enumerate(sys.argv):
        if a == "--region" and i + 1 < len(sys.argv):
            reg = sys.argv[i + 1]
    snapshot(reg)
