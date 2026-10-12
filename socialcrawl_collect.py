# -*- coding: utf-8 -*-
"""Kolektor TikTok Shop via SocialCrawl (pengganti Apify).

Aturan biaya: search murah (~1 kredit/query); detail 1 kredit/biji (maks 25).
Guard: berhenti bila sisa < 35 (cukup 1 run mingguan ~30).
Jadwal: 1x/minggu. Key: credential/socialcrawl.txt + GH secret.
"""
import datetime
import io
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = pathlib.Path(__file__).resolve().parent
HOST = 'https://www.socialcrawl.dev'
TERMS = ['gamis', 'dress kondangan', 'kemeja wanita', 'blouse wanita',
         'abaya']
MAX_DETAIL = 25
MIN_BALANCE = 35

import os

key = os.environ.get("SOCIALCRAWL_KEY") or [l.split('=', 1)[1].strip() for l in
       (BASE / 'credential/socialcrawl.txt').read_text(
           encoding='utf-8').splitlines()
       if l.startswith('SOCIALCRAWL_KEY=')][0]


def api(path, params):
    qs = urllib.parse.urlencode(params)
    req = urllib.request.Request(f'{HOST}{path}?{qs}',
                                 headers={'x-api-key': key})
    return json.load(urllib.request.urlopen(req, timeout=180))


def balance():
    return (api('/v1/credits/balance', {}).get('data') or {}).get(
        'balance', 0)


def main():
    bal = balance()
    print(f'saldo: {bal}')
    if bal < MIN_BALANCE:
        raise SystemExit(f'BERHENTI: saldo < {MIN_BALANCE}')
    seen, semua = {}, []
    for q in TERMS:
        d = api('/v1/tiktokshop/search', {'query': q, 'region': 'ID'})
        for it in (d.get('data') or {}).get('items', []):
            p = it.get('product', {})
            if p.get('id') and p['id'] not in seen:
                seen[p['id']] = True
                semua.append(p)
        print(f'{q}: sisa {d.get("credits_remaining")}')
    semua.sort(key=lambda p: (p.get('reviews_count') or 0), reverse=True)
    for p in semua[:MAX_DETAIL]:
        try:
            d = api('/v1/tiktokshop/product',
                    {'product_id': p['id'], 'region': 'ID'})
            det = d.get('data') or {}
            prod = det.get('product', det) if isinstance(det, dict) else {}
            for k in ('units_sold', 'sold_count', 'lifetime_units_sold'):
                if prod.get(k) is not None:
                    p['enrich_' + k] = prod.get(k)
        except Exception as e:
            print('enrich gagal', p.get('id'), str(e)[:70])
            time.sleep(10)
    snap = {'waktu': datetime.datetime.now().strftime('%Y%m%d_%H%M%S'),
            'region': 'ID', 'items': semua}
    (BASE / f"data/socialcrawl_shop_{snap['waktu']}.json").write_text(
        json.dumps(snap, ensure_ascii=False), encoding='utf-8')
    WEB = BASE / 'web/data/products.json'
    prods = json.loads(WEB.read_text(encoding='utf-8'))
    prods = [x for x in prods if not str(x.get('id', '')).startswith('sc-')]
    for p in semua:
        sold = (p.get('enrich_units_sold') or p.get('enrich_sold_count')
                or p.get('enrich_lifetime_units_sold'))
        price = (p.get('price') or {}).get('current')
        rating = (p.get('rating') or {}).get('average')
        prods.append({
            'id': f"sc-{p.get('id')}",
            'name': p.get('title'), 'price': price,
            'sold': sold, 'reviews': p.get('reviews_count'),
            'rating': rating, 'image': (p.get('image_urls') or [None])[0],
            'marketplace': 'TikTok', 'kelas': 'PRODUK TIKTOK SHOP',
            'shop': p.get('seller'), 'affiliateUrl': p.get('url'),
            'g7': None, 'g30': None,
            'sinyal': f"TikTok Shop ID via SocialCrawl ({snap['waktu'][:8]})",
        })
    WEB.write_text(json.dumps(prods, ensure_ascii=False, indent=1),
                   encoding='utf-8')
    print(f'masuk: {len(semua)} | web: {len(prods)} | saldo: {balance()}')


if __name__ == '__main__':
    main()
