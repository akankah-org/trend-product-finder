# -*- coding: utf-8 -*-
"""Monitor kesegaran data per tab (tanpa API, tanpa kuota).
Dipakai workflow harian: hitung item per sumber + umur meta.json,
cetak ringkasan untuk notif Telegram. Stale = umur > ambang.
"""
import datetime
import io
import json
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = pathlib.Path(__file__).resolve().parent
WEB = BASE / "web/data/products.json"
META = BASE / "web/data/meta.json"


def src(p):
    s = p.get("sinyal") or ""
    if "Google Dork" in s:
        u = p.get("affiliateUrl") or ""
        return "tiktok_by_google" if "tiktok.com" in u else "shopee_by_google"
    if "Shopee API" in s:
        return "shopee"
    if "IKLAN" in (p.get("kelas") or ""):
        return "ads" if "TikTok" in (p.get("marketplace") or "") or \
            "tiktok" in s.lower() else "shopee_ads"
    if (p.get("marketplace") or "") in ("TikTok", "TikTok Shop"):
        return "tiktok"
    return "google"


def main():
    prods = json.loads(WEB.read_text(encoding="utf-8"))
    meta = json.loads(META.read_text(encoding="utf-8"))
    tgl = meta.get("tanggal", "?")
    try:
        umur = (datetime.date.today() -
                datetime.datetime.strptime(tgl, "%Y%m%d").date()).days
    except Exception:
        umur = -1
    from collections import Counter
    c = Counter(src(p) for p in prods)
    baris = [f"radar {len(prods)} item, data {tgl} (umur {umur}h)"]
    for k, v in sorted(c.items()):
        baris.append(f"- {k}: {v}")
    baris.append("STALE!" if umur > 7 else "segar")
    print("\n".join(baris))


if __name__ == "__main__":
    main()
