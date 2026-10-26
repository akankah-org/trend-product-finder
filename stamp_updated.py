# -*- coding: utf-8 -*-
"""Stempel 'updated' per produk -> hasil terbaru selalu di ATAS di web.

Masalah yang diselesaikan: `web/data/products.json` tidak punya penanda waktu
per produk, jadi web tidak tahu mana yang baru berubah. Modul ini menambah field
`updated` (ISO UTC) pada tiap item dengan cara membandingkan isi item dengan
versi sebelumnya:

  - item baru (id belum ada)        -> updated = waktu run
  - item lama yang isinya berubah   -> updated = waktu run
  - item lama yang isinya sama      -> updated lama dipertahankan
  - item lama tanpa 'updated'       -> pakai waktu commit terakhir (bukan waktu
                                       run), supaya run pertama tidak menandai
                                       SEMUA item sebagai 'baru'

Dipakai oleh penulis products.json (kolektor/manual), atau dari CLI:

    python stamp_updated.py          # stempel file yang ada sekarang

Catatan: field `updated` TIDAK masuk sidik pembanding (lihat KUNCI), jadi
menstempel berulang tidak membuat item dianggap "berubah" terus.
"""
import datetime
import json
import pathlib
import subprocess

BASE = pathlib.Path(__file__).resolve().parent
PJ = BASE / "web" / "data" / "products.json"

# Field yang dipakai untuk menilai "isinya berubah". 'updated' sengaja tidak ikut.
KUNCI = (
    "name", "sold", "price", "reviews", "rating", "g7", "g30",
    "growth7d", "growth30d", "likes", "ctr", "impr_num", "trend",
    "sinyal", "kelas", "shop", "marketplace", "affiliateUrl", "category",
)


def sidik(p):
    """Sidik isi produk (tanpa 'updated')."""
    return json.dumps([p.get(k) for k in KUNCI], ensure_ascii=False, sort_keys=True)


def sekarang():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _waktu_commit(ref="HEAD"):
    """Waktu commit terakhir yang menyentuh products.json (acuan run pertama)."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cI", ref, "--", "web/data/products.json"],
            cwd=str(BASE), capture_output=True, text=True, timeout=30,
        )
        iso = (out.stdout or "").strip()
        if iso:
            dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
            return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        pass
    return sekarang()


def stempel(prods, lama=None, waktu=None):
    """Beri/tahan field 'updated' pada setiap produk.

    prods : list produk yang akan ditulis
    lama  : isi products.json SEBELUM diubah (untuk pembanding)
    waktu : timestamp untuk item baru/berubah (default: sekarang UTC)
    """
    lama = lama or []
    dulu = {p.get("id"): p for p in lama if p.get("id")}
    w = waktu or sekarang()
    cadangan = _waktu_commit()
    stat = {"baru": 0, "ubah": 0, "tetap": 0, "waktu": w}
    for p in prods:
        o = dulu.get(p.get("id"))
        if o is None:
            p["updated"] = w
            stat["baru"] += 1
        elif sidik(p) != sidik(o):
            p["updated"] = w
            stat["ubah"] += 1
        else:
            p["updated"] = o.get("updated") or cadangan
            stat["tetap"] += 1
    return prods, stat


def urut(prods):
    """Urutkan: updated terbaru dulu (yang sama tetap urutan aslinya)."""
    return sorted(prods, key=lambda p: (str(p.get("updated") or ""),), reverse=True)


def _dari_git(ref="HEAD"):
    try:
        out = subprocess.run(
            ["git", "show", "%s:web/data/products.json" % ref],
            cwd=str(BASE), capture_output=True, text=True, encoding="utf-8", timeout=60,
        )
        if out.returncode == 0 and (out.stdout or "").strip():
            return json.loads(out.stdout)
    except Exception:
        pass
    return []


def main():
    if not PJ.exists():
        raise SystemExit("tidak ada %s" % PJ)
    prods = json.loads(PJ.read_text(encoding="utf-8-sig"))
    lama = _dari_git()
    prods, stat = stempel(prods, lama)
    prods = urut(prods)
    PJ.write_text(json.dumps(prods, ensure_ascii=False, indent=1), encoding="utf-8")
    print("stempel: {baru} baru, {ubah} berubah, {tetap} tetap @ {waktu}".format(**stat))
    print("total: %d item -> %s" % (len(prods), PJ))


if __name__ == "__main__":
    main()
