"""Viewer snapshot trends -> view.html (buka di browser)."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
files = sorted(f for f in os.listdir(DATA)
               if f.startswith("gtrends_") and f.endswith(".json"))
if not files:
    raise SystemExit("belum ada snapshot")
d = json.load(open(os.path.join(DATA, files[-1]), encoding="utf-8"))
rows = []
for kw, pts in d.get("keywords", {}).items():
    avg = sum(p["v"] for p in pts) / len(pts) if pts else 0
    mx = max((p["v"] for p in pts), default=0)
    rows.append((avg, kw, mx, len(pts)))
rows.sort(reverse=True)
tr = "\n".join(
    f"<tr><td>{kw}</td><td>{avg:.0f}</td><td>{mx}</td>"
    f"<td>{'█' * min(int(avg / 2), 40)}</td></tr>"
    for avg, kw, mx, n in rows)
html = f"""<!DOCTYPE html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tren 7d ({d.get('waktu', '')})</title>
<style>body{{font-family:sans-serif;background:#0d1117;color:#c9d1d9;padding:20px}}
table{{border-collapse:collapse;width:100%;max-width:640px}}
td,th{{border:1px solid #30363d;padding:6px 10px;text-align:left;font-size:14px}}
th{{color:#8b949e}}</style></head><body>
<h2>Minat 7 hari — {d.get('waktu', '')}</h2>
<table><tr><th>Keyword</th><th>Avg</th><th>Max</th><th>Bar</th></tr>{tr}</table>
</body></html>"""
p = os.path.join(BASE, "view.html")
open(p, "w", encoding="utf-8").write(html)
print("view.html siap")
