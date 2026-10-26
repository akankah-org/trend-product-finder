# -*- coding: utf-8 -*-
"""Langkah 3: merge _dork74.json -> products.json (cap 10/kat/market)."""
import io
import json
import re
import sys

from stamp_updated import stempel

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "E:/trend product finder"
PJ = BASE + "/web/data/products.json"
products = json.load(open(PJ, encoding="utf-8"))
lama = json.loads(json.dumps(products))  # snapshot sebelum merge (pembanding stempel)
dork = json.load(open(BASE + "/data/_dork74.json", encoding="utf-8"))
MOV = {"shopee": "Shopee", "tiktok": "TikTok"}
TGL = "15 Okt"

existing_urls = {p.get("url") or p.get("affiliateUrl") for p in products}
existing_ids = {p.get("id") for p in products}
added = 0
for kat, items in dork.items():
    cap = {"shopee": 0, "tiktok": 0}
    n = 0
    for it in items:
        s = it["site"]
        if cap[s] >= 10:
            continue
        if it["url"] in existing_urls:
            continue
        name = re.sub(r"\s+", " ", it["name"]).strip()
        if not name:
            continue
        _id = f"gd-up-{kat}-{n}"
        while _id in existing_ids:
            n += 1
            _id = f"gd-up-{kat}-{n}"
        products.append({
            "id": _id,
            "name": name[:140],
            "url": it["url"],
            "affiliateUrl": it["url"],
            "category": kat,
            "kategori": kat,
            "marketplace": MOV[s],
            "shop": "-",
            "price": None,
            "rating": None,
            "reviews": None,
            "sold": None,
            "growth7d": None,
            "growth30d": None,
            "trend": None,
            "kelas": "UP-TREND GOOGLE",
            "sinyal": f"Google Dork site:{'shopee.co.id' if s=='shopee' else 'tiktok.com'} [{kat}] ({TGL})",
            "link_note": "Naik di Google Trends 7d — urutan Google, bukan angka penjualan",
        })
        existing_urls.add(it["url"])
        existing_ids.add(_id)
        cap[s] += 1
        n += 1
        added += 1

products, _st = stempel(products, lama)
json.dump(products, open(PJ, "w", encoding="utf-8"), ensure_ascii=False,
          indent=1)
print("total produk:", len(products), "| tambah:", added,
      "| stempel:", _st["baru"], "baru,", _st["ubah"], "berubah")
