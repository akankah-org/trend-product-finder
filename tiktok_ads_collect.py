# -*- coding: utf-8 -*-
"""Kolektor IKLAN TikTok (Creative Center Top Ads -> produk Shop).

Status: TERTUNDA — kredit Apify habis (sisa $0.000785 per 2026-10-08).
Script menolak jalan bila sisa kredit < $1.00 (cek /users/me dulu).

Setelah top-up, jalankan:
  python tiktok_ads_collect.py --max 30

Alir:
  1. azzouzana Top Ads (region ID, semua kategori) -> iklan + landing page.
  2. Ambil product_url (tiktok/tokopedia) -> herus13 product_urls (ID).
  3. Merge ke web/data/products.json: marketplace TikTok,
     kelas 'IKLAN TOKO', sinyal 'TikTok Ads (terjual N, CTR x%)'.
Tab web: 'Sedang Diiklankan' (source ads), sorting sold desc.
"""
import datetime
import io
import json
import pathlib
import sys
import time
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = pathlib.Path(__file__).resolve().parent
CRED = BASE / 'credential'
ADS_ACTOR = 'azzouzana~tiktok-creative-center-top-ads-scraper'
SHOP_ACTOR = 'herus13~tiktok-shop-scraper'
MIN_CREDIT_USD = 1.00


def token():
    for ln in (CRED / 'apify.txt').read_text(encoding='utf-8').splitlines():
        if ln.startswith('APIFY_TOKEN='):
            return ln.split('=', 1)[1].strip()
    raise SystemExit('token tak ketemu')


def api(base, method, path, tok, data=None):
    req = urllib.request.Request(
        base + path, data=json.dumps(data).encode() if data else None,
        method=method,
        headers={'Content-Type': 'application/json',
                 'Authorization': f'Bearer {tok}'})
    return json.load(urllib.request.urlopen(req, timeout=120))


def credit_left(tok):
    u = api('https://api.apify.com/v2', 'GET', '/users/me', tok)
    d = u.get('data', u)
    usage = d.get('usage') or {}
    try:
        return float(usage.get('totalLimitUsd', 0)) - float(
            usage.get('totalUsageUsd', 0))
    except (TypeError, ValueError):
        return 0.0


def wait_run(tok, rid, tries=30):
    for _ in range(tries):
        time.sleep(10)
        d = api('https://api.apify.com/v2/acts/' + ADS_ACTOR,
                'GET', f'/runs/{rid}', tok)['data']
        if d['status'] in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
            return d['status']
    return 'TIMEOUT'


def main():
    mx = 30
    if '--max' in sys.argv:
        mx = int(sys.argv[sys.argv.index('--max') + 1])
    tok = token()
    sisa = credit_left(tok)
    print(f'sisa kredit: ${sisa:.4f}')
    if sisa < MIN_CREDIT_USD:
        raise SystemExit(
            f'BERHENTI: kredit < ${MIN_CREDIT_USD:.2f} — top-up dulu.')
    print('KOLEKTOR IKLAN: tulis input final setelah probe pertama ID '
          f'(max {mx}). Status: menunggu kredit + skema terkonfirmasi.')
    print('Langkah: Top Ads ID -> landing product_url -> herus13 '
          'product_urls ID -> merge kelas IKLAN TOKO.')


if __name__ == '__main__':
    main()
