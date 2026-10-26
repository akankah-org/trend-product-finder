# -*- coding: utf-8 -*-
"""Tambah produk untuk kategori baru, lalu TANDAI sumbernya.

Dua jalur:
  1) API marketplace (SocialCrawl / TikTok Shop)
       python tambah_kategori.py tiktok "tas selempang" "Tas Wanita"
  2) Google dork (RapidAPI google-search74)
       python tambah_kategori.py dork-shopee "blouse kemeja kaos wanita" "Atasan Wanita"

Penanda sumber ditulis di field `sinyal` dan `sumber`:
  - hasil API   -> sumber = "api"        (di web: flag "API")
  - hasil dork  -> sumber = "by google"  (di web: flag "BY GOOGLE")

Aman diulang: id/url yang sudah ada dilewati, dan `updated` diisi lewat
stamp_updated supaya item baru otomatis naik ke atas.
"""
import datetime
import io
import json
import os
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = pathlib.Path(__file__).resolve().parent
PJ = BASE / "web" / "data" / "products.json"
CRED = BASE / "credential"

from stamp_updated import stempel, urut  # noqa: E402

TGL = datetime.datetime.now().strftime("%Y%m%d")
DORK_HOST = "google-search74.p.rapidapi.com"


def kunci(nama, variabel):
    """Ambil kunci dari env atau credential/<nama>.txt (tanpa mencetak nilainya)."""
    v = os.environ.get(variabel)
    if v:
        return v.strip()
    p = CRED / nama
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            if ln.startswith(variabel + "="):
                return ln.split("=", 1)[1].strip()
    return ""


def api_socialcrawl(path, params):
    key = kunci("socialcrawl.txt", "SOCIALCRAWL_KEY")
    if not key:
        raise SystemExit("SOCIALCRAWL_KEY tidak ada")
    qs = urllib.parse.urlencode(params)
    req = urllib.request.Request("https://www.socialcrawl.dev" + path + "?" + qs,
                                 headers={"x-api-key": key})
    return json.load(urllib.request.urlopen(req, timeout=180))


def tiktok(query, kategori, maks=20):
    d = api_socialcrawl("/v1/tiktokshop/search", {"query": query, "region": "ID"})
    items = (d.get("data") or {}).get("items", [])
    return items[:maks]


def dork(query, limit=30):
    key = kunci("_rap74.key", "RAPIDAPI_KEY")
    if not key and (pathlib.Path("D:/opencode/_rap74.key")).exists():
        key = pathlib.Path("D:/opencode/_rap74.key").read_text(encoding="utf-8").strip()
    if not key:
        raise SystemExit("kunci RapidAPI google-search74 tidak ada")
    qs = urllib.parse.urlencode({"query": query, "limit": limit, "gl": "id", "hl": "id"})
    req = urllib.request.Request("https://%s/?%s" % (DORK_HOST, qs),
                                 headers={"X-RapidAPI-Key": key,
                                          "X-RapidAPI-Host": DORK_HOST,
                                          "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                                                         "Chrome/130.0 Safari/537.36"),
                                          "Accept": "application/json"})
    r = urllib.request.urlopen(req, timeout=60)
    if r.status != 200:
        raise SystemExit("dork gagal: HTTP %s" % r.status)
    return (json.loads(r.read().decode()) or {}).get("results") or []


def simpan(products, lama, tambah):
    products, st = stempel(products, lama)
    products = urut(products)
    PJ.write_text(json.dumps(products, ensure_ascii=False, indent=1), encoding="utf-8")
    print("  +%d item | total %d | stempel: %d baru, %d berubah"
          % (tambah, len(products), st["baru"], st["ubah"]))


def jalur_tiktok(query, kategori, maks):
    products = json.loads(PJ.read_text(encoding="utf-8-sig"))
    lama = json.loads(json.dumps(products))
    ada = {p.get("id") for p in products}
    items = tiktok(query, kategori, maks)
    n = 0
    for it in items:
        p = it.get("product", {})
        pid = "sc-%s" % p.get("id")
        if not p.get("id") or pid in ada:
            continue
        harga = (p.get("price") or {}).get("current")
        rating = (p.get("rating") or {}).get("average")
        products.append({
            "id": pid,
            "name": (p.get("title") or "")[:140],
            "price": harga,
            "sold": p.get("sold_count"),
            "reviews": p.get("reviews_count"),
            "rating": rating,
            "image": (p.get("image_urls") or [None])[0],
            "marketplace": "TikTok",
            "kelas": "PRODUK TIKTOK SHOP",
            "shop": p.get("seller"),
            "affiliateUrl": p.get("url"),
            "g7": None, "g30": None,
            "category": kategori,
            "kategori": kategori,
            "sumber": "api",
            "sinyal": "TikTok Shop ID via SocialCrawl (%s) [API]" % TGL,
        })
        ada.add(pid)
        n += 1
    simpan(products, lama, n)


def jalur_dork_shopee(query, kategori, maks):
    products = json.loads(PJ.read_text(encoding="utf-8-sig"))
    lama = json.loads(json.dumps(products))
    ada_id = {p.get("id") for p in products}
    ada_url = {p.get("url") or p.get("affiliateUrl") for p in products}
    slug = re.sub(r"[^a-z0-9]+", "-", kategori.lower()).strip("-")
    hasil = dork("site:shopee.co.id " + query)
    n = 0
    for it in hasil:
        u = it.get("url") or ""
        # hanya halaman PRODUK (bukan halaman search/list/kategori)
        if not re.search(r"-i\.\d+\.\d+", u) and "/product/" not in u:
            continue
        if not u.startswith("http") or u in ada_url:
            continue
        name = re.sub(r"\s+", " ", (it.get("title") or "")).strip()
        if not name:
            continue
        i = 0
        while "gd-up-%s-%d" % (slug, i) in ada_id:
            i += 1
        _id = "gd-up-%s-%d" % (slug, i)
        products.append({
            "id": _id,
            "name": name[:140],
            "url": u,
            "affiliateUrl": u,
            "category": kategori,
            "kategori": kategori,
            "marketplace": "Shopee",
            "shop": "-",
            "price": None, "rating": None, "reviews": None, "sold": None,
            "growth7d": None, "growth30d": None, "trend": None,
            "kelas": "UP-TREND GOOGLE",
            "sumber": "by google",
            "sinyal": "Google Dork site:shopee.co.id [%s] (%s) [by Google]" % (kategori, TGL),
            "link_note": "Hasil Google (bukan API Shopee) - cek manual sebelum dipakai",
        })
        ada_id.add(_id)
        ada_url.add(u)
        n += 1
        if n >= maks:
            break
    simpan(products, lama, n)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    mode, q, kat = sys.argv[1], sys.argv[2], sys.argv[3]
    maks = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    if mode == "tiktok":
        jalur_tiktok(q, kat, maks)
    elif mode == "dork-shopee":
        jalur_dork_shopee(q, kat, maks)
    else:
        raise SystemExit("mode harus: tiktok | dork-shopee")
