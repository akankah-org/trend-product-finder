"""Kolektor Shopee via RapidAPI Syphoon (route: POST /).

  python shopee_rapid.py --once     # 1x snapshot semua target
  python shopee_rapid.py --test     # 1 req contoh (validasi pipa)

Target: targets.json [{label, shop_id, item_id}]
Budget: BUDGET_BULANAN (default 60/100) via credential/usage.json.
Aturan akurasi: field terpercaya SAJA (review_count, stock ada/tak,
listing); sold/harga = simpan + flag tak-terverifikasi.
"""
import datetime
import json
import os
import sys

try:
    import requests
except ImportError:
    sys.exit("butuh requests: pip install requests")

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
del _s


def aman(s, n=50):
    return str(s or "?")[:n].encode("ascii", "replace").decode()

BASE = os.path.dirname(os.path.abspath(__file__))
CRED = os.path.join(BASE, "credential")
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

BUDGET_BULANAN = 40  # plan BASIC: 50/bln hard limit (sisakan buffer)


def cred():
    d = {}
    for line in open(os.path.join(CRED, "rapidapi_shopee.txt"),
                     encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    assert d.get("RAPIDAPI_KEY"), "RAPIDAPI_KEY kosong di credential file"
    d.setdefault("RAPIDAPI_HOST", "shopee-scraper1.p.rapidapi.com")
    d.setdefault("ROUTE", "/")
    return d


def usage():
    p = os.path.join(CRED, "usage.json")
    try:
        u = json.load(open(p, encoding="utf-8"))
    except Exception:
        u = {}
    bln = datetime.datetime.now().strftime("%Y-%m")
    return u.get(bln, 0), p, bln, u


def pakai(n=1):
    used, p, bln, u = usage()
    if used + n > BUDGET_BULANAN:
        raise SystemExit(
            f"budget habis: {used}/{BUDGET_BULANAN}/bln. Naikkan manual bila perlu.")
    u[bln] = used + n
    json.dump(u, open(p, "w", encoding="utf-8"))
    return used + n


def fetch(shop_id, item_id, key, host, route="/", domain="shopee.co.id"):
    r = requests.post(
        f"https://{host}{route}",
        headers={"X-RapidAPI-Key": key, "X-RapidAPI-Host": host,
                 "Content-Type": "application/json"},
        json={"url": (f"https://{domain}/api/v4/pdp/get_pc"
                      f"?shop_id={shop_id}&item_id={item_id}")},
        timeout=120)
    r.raise_for_status()
    return r.json()


def ekstrak(d):
    """Hanya field terpercaya + flag. mentah disimpan terpisah bila perlu."""
    it = (d.get("data") or {}).get("item", {})
    rv = (d.get("data") or {}).get("product_review", {})
    sh = (d.get("data") or {}).get("shop_detailed", {}) or {}
    rc = rv.get("rating_count") or []
    return {
        "title": it.get("title"),
        "shop": sh.get("name"),
        "price_min": it.get("price_min"),
        "price_max": it.get("price_max"),
        "price_flag": "tak-terverifikasi (beda IP/negara)",
        "rating_star": (it.get("item_rating") or {}).get("rating_star"),
        "review_count": rv.get("total_rating_count"),
        "rating_dist": rc,
        "sold": None,
        "sold_flag": "null di API (jangan pakai untuk velocity)",
        "stock_ada": True,
        "image": it.get("image"),
    }


def snapshot():
    c = cred()
    tg = [x for x in json.load(open(os.path.join(BASE, "targets.json"), encoding="utf-8"))
          if x.get("shop_id") and x.get("item_id")]
    if not tg:
        print("targets.json kosong. Isi dulu [{label, shop_id, item_id}].")
        return
    pakai(len(tg))
    out = {"waktu": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
           "items": []}
    import time as _t
    for n, t in enumerate(tg):
        if n:
            _t.sleep(10)
        try:
            d = fetch(t["shop_id"], t["item_id"], c["RAPIDAPI_KEY"],
                      c["RAPIDAPI_HOST"], c.get("ROUTE", "/"),
                      t.get("domain", "shopee.co.id"))
            e = ekstrak(d)
            e["label"] = t.get("label", "")
            e["shop_id"] = t["shop_id"]
            e["item_id"] = t["item_id"]
            out["items"].append(e)
            print("OK  ", aman(e["label"] or e["title"], 40))
        except Exception as e:
            print("FAIL", t.get("label"), str(e)[:100])
    p = os.path.join(DATA, f"shopee_{out['waktu']}.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    print("tersimpan:", p)


if __name__ == "__main__":
    if "--test" in sys.argv:
        c = cred()
        d = fetch(1462742, 963359618, c["RAPIDAPI_KEY"],
                  c["RAPIDAPI_HOST"], c.get("ROUTE", "/"), "shopee.tw")
        it = (d.get("data") or {}).get("item", {})
        print("TEST OK:", aman((it.get("title") or "?"), 50))
        pakai(1)
    else:
        snapshot()
