"""Kolektor Lapis 3: Relu Shopee API via RapidAPI (BELUM terverifikasi!).

JANGAN pakai produksi sebelum --test 200 OK.
  python relu_shopee.py --test     # 1 req validasi (butuh RELU_KEY+HOST)

Guard: 8/hari dari jatah 10/hari (credential/usage_relu.json).
Fungsi: search produk, seller details, (flash sale menyusul).
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

BATAS_HARIAN = 8


def cred():
    d = {}
    for line in open(os.path.join(CRED, "relu_shopee.txt"),
                     encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    if not d.get("RELU_KEY") or not d.get("RELU_HOST"):
        raise SystemExit("isi RELU_KEY + RELU_HOST di credential/relu_shopee.txt")
    return d


def _counter_path():
    return os.path.join(CRED, "usage_relu.json")


def pakai(n=1):
    p = _counter_path()
    try:
        u = json.load(open(p, encoding="utf-8"))
    except Exception:
        u = {}
    hari = datetime.datetime.now().strftime("%Y-%m-%d")
    if u.get(hari, 0) + n > BATAS_HARIAN:
        raise SystemExit(
            f"budget harian habis ({u.get(hari, 0)}/{BATAS_HARIAN}). Stop.")
    u[hari] = u.get(hari, 0) + n
    json.dump(u, open(p, "w", encoding="utf-8"))
    return u[hari]


def call(path, params, key, host):
    """GET dengan token+url sebagai query param (sesuai docs Relu)."""
    q = dict(params or {})
    q.setdefault("token", key)
    r = requests.get(f"https://{host}{path}", params=q,
                     headers={"X-RapidAPI-Key": key,
                              "X-RapidAPI-Host": host},
                     timeout=120)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    if "--test" not in sys.argv:
        print("Belum ada mode produksi. Verifikasi dulu: --test")
        raise SystemExit(1)
    c = cred()
    print("coba seller-details (1 req)...")
    print("CATATAN: path endpoint pasti menyusul dari tab Endpoints.")
    print("Isi ROUTE_test di bawah setelah baca dashboard, lalu --test lagi.")
