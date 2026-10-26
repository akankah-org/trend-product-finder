"""Jembatan: snapshot gtrends -> sinyal_search per kategori di MVP.

Jujur: ini SINYAL SEARCH per kategori, BUKAN growth produk.
Jalankan tiap ada snapshot baru, lalu refresh browser MVP.
"""
import datetime
import json
import os

from stamp_updated import stempel

BASE = os.path.dirname(os.path.abspath(__file__))
MVP = 'E:/trend product finder/web/data'
MAP = {'gamis': 'Gamis', 'dress wanita': 'Dress', 'dress korea': 'Dress',
       'blouse': 'Blouse', 'hijab': 'Hijab', 'pashmina': 'Hijab',
       'kebaya': 'Kebaya'}

snaps = sorted(f for f in os.listdir(os.path.join(BASE, 'data'))
               if f.startswith('gtrends_') and f.endswith('.json'))
if not snaps:
    raise SystemExit('belum ada snapshot gtrends')
d = json.load(open(os.path.join(BASE, 'data', snaps[-1]), encoding='utf-8'))
cat = {}
for kw, pts in d.get('keywords', {}).items():
    if kw in MAP and pts:
        avg = sum(p['v'] for p in pts) / len(pts)
        cat.setdefault(MAP[kw], []).append(avg)
sinyal = {c: round(sum(v) / len(v)) for c, v in cat.items()}

prods = json.load(open(os.path.join(MVP, 'products.json'), encoding='utf-8'))
lama = json.loads(json.dumps(prods))  # snapshot sebelum diubah (pembanding stempel)
for p in prods:
    p['sinyal_search'] = sinyal.get(p.get('category'), None)
prods, _st = stempel(prods, lama)
json.dump(prods, open(os.path.join(MVP, 'products.json'), 'w',
                      encoding='utf-8'), ensure_ascii=False, indent=1)
meta = {'tanggal': d.get('waktu', '')[:8],
        'sumber': 'sinyal search Google Trends ID per kategori (bukan growth produk)'}
json.dump(meta, open(os.path.join(MVP, 'meta.json'), 'w', encoding='utf-8'),
          ensure_ascii=False)
print('sinyal:', sinyal)
print('meta:', meta['tanggal'], '-', meta['sumber'][:40])
