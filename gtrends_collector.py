"""Kolektor Google Trends (ID) — sumber tren independen, tanpa key.

  python gtrends_collector.py          # snapshot daily + keyword 7d
  python gtrends_collector.py --report # laporan growth vs snapshot lalu

Output: data/gtrends_YYYYMMDD_HHMMSS.json (append histori lokal).
Tool murni PC, tanpa repo.
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
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

KEYWORDS = ["gamis", "dress wanita", "blouse", "hijab", "kebaya",
            "batik", "tunik", "pashmina", "celana wanita", "rok",
            "baju kondangan", "dress korea"]
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
           "Accept-Language": "id-ID,id;q=0.9,en;q=0.8"}
SESS = None
JEDA = 8  # detik antar keyword (anti-429)


def _sess():
    global SESS
    if SESS is None:
        import requests as _rq
        SESS = _rq.Session()
        SESS.headers.update(HEADERS)
        try:
            SESS.get("https://trends.google.com", timeout=20)
        except Exception:
            pass
    return SESS


def _api(path, params):
    import time as _t
    r = _sess().get("https://trends.google.com/trends/api" + path,
                    params=params, timeout=30)
    if r.status_code == 429:
        _t.sleep(60)
        r = _sess().get("https://trends.google.com/trends/api" + path,
                        params=params, timeout=30)
    r.raise_for_status()
    return json.loads(r.text[5:])


def daily_id():
    """Endpoint daily mati (404 sejak 2026) -> kosong, andalkan keyword."""
    return []


def interest_7d(kws):
    """Batch <=5 keyword per request (hemat hit anti-429).
    Kembalikan {keyword: [{t, v}]}."""
    kws = list(kws)[:5]
    try:
        items = [{"keyword": k, "geo": "ID", "time": "now 7-d"}
                 for k in kws]
        exp = _api("/explore", {
            "hl": "id-ID", "tz": "-420",
            "req": json.dumps({"comparisonItem": items,
                               "category": 0, "property": ""})})
        widget = exp["widgets"][0]
        data = _api("/widgetdata/multiline",
                    {"hl": "id-ID", "tz": "-420",
                     "req": json.dumps(widget["request"]),
                     "token": widget["token"]})
        cols = None  # (tak dipakai; urutan value = urutan keyword)
        out = {}
        for idx, k in enumerate(kws):
            tl = data["default"]["timelineData"]
            out[k] = [{"t": p["time"], "v": p["value"][idx]} for p in tl]
        return out
    except Exception:
        return {}


def snapshot():
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    res = {"waktu": now, "daily": daily_id(), "keywords": {}}
    chunks = [KEYWORDS[i:i + 5] for i in range(0, len(KEYWORDS), 5)]
    for n, ch in enumerate(chunks):
        if n:
            import time as _t
            _t.sleep(25)
        got = interest_7d(ch)
        if not got:
            import time as _t2
            _t2.sleep(90)
            got = interest_7d(ch)
        for kw in ch:
            v = got.get(kw, [])
            res["keywords"][kw] = v
            print(("OK  " if v else "FAIL"), kw,
                  f"avg={sum(p['v'] for p in v) / len(v):.0f}" if v else "")
    path = os.path.join(DATA, f"gtrends_{now}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False)
    print("tersimpan:", path)
    return res


def report():
    files = sorted(f for f in os.listdir(DATA)
                   if f.startswith("gtrends_") and f.endswith(".json"))
    if len(files) < 2:
        print(f"butuh >=2 snapshot (ada {len(files)}). "
              "Jalankan lagi nanti untuk growth.")
        return
    a = json.load(open(os.path.join(DATA, files[-2]), encoding="utf-8"))
    b = json.load(open(os.path.join(DATA, files[-1]), encoding="utf-8"))
    print(f"{files[-2][:15]} -> {files[-1][:15]}")
    rows = []
    for kw in KEYWORDS:
        va = a["keywords"].get(kw) or []
        vb = b["keywords"].get(kw) or []
        if not va or not vb:
            continue
        ma = sum(p["v"] for p in va) / len(va)
        mb = sum(p["v"] for p in vb) / len(vb)
        g = (mb - ma) / ma * 100 if ma else 0
        rows.append((g, kw, ma, mb))
    for g, kw, ma, mb in sorted(rows, reverse=True):
        print(f"{g:+7.1f}%  {kw} ({ma:.0f} -> {mb:.0f})")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        report()
    else:
        snapshot()
