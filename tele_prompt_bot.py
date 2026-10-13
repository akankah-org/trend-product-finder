# -*- coding: utf-8 -*-
"""Bot Telegram Prompt (MENU DULU, isi user yang kelola).
Menu: Prompt TikTok | Prompt Shopee. Lihat/tambah/ubah/rename/hapus.
Password 777: /pass 777 buka sesi 30 mnt (tiap perintah ubah wajib sesi).
Hanya ID pemilik (tele_guard). Polling, stdlib saja, jalan di PC.
Data: data/tele_prompts.json (TERPISAH dari localStorage web).
Jalan: python tele_prompt_bot.py   (berhenti: Ctrl+C)
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from tele_guard import check, is_allowed

STORE = os.path.join(BASE, "data", "tele_prompts.json")
PWD = "777"
SESI_MENIT = 30
sesi = {}  # chat_id -> epoch unlock


def tokens():
    toks = {}
    try:
        for ln in open(os.path.join(BASE, "credential",
                                    "telegram_bots.txt"),
                       encoding="utf-8"):
            if "=" in ln:
                k, v = ln.strip().split("=", 1)
                toks[k.strip()] = v.strip()
    except Exception:
        pass
    toks.setdefault("FASHION_RADAR_BOT", os.environ.get("FASHION_BOT", ""))
    toks.setdefault("TELEGRAM_CHAT_ID",
                    os.environ.get("TELEGRAM_CHAT_ID", "8772898381"))
    return toks


TOK = tokens()
BOT = TOK["FASHION_RADAR_BOT"]
CHAT = TOK["TELEGRAM_CHAT_ID"]
API = f"https://api.telegram.org/bot{BOT}"


def call(method, **kw):
    data = urllib.parse.urlencode(kw).encode()
    req = urllib.request.Request(API + "/" + method, data=data)
    return json.load(urllib.request.urlopen(req, timeout=30))


def kirim(chat, text, tombol=None):
    kw = {"chat_id": chat, "text": text}
    if tombol:
        kw["reply_markup"] = json.dumps(
            {"keyboard": tombol, "resize_keyboard": True})
    return call("sendMessage", **kw)


def load():
    try:
        d = json.load(open(STORE, encoding="utf-8"))
        d.setdefault("tiktok", [])
        d.setdefault("shopee", [])
        return d
    except Exception:
        return {"tiktok": [], "shopee": []}


def save(d):
    json.dump(d, open(STORE, "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)


def unlocked(chat):
    return time.time() - sesi.get(str(chat), 0) < SESI_MENIT * 60


MENU = [[{"text": "Prompt TikTok"}], [{"text": "Prompt Shopee"}]]
KIND = {"Prompt TikTok": "tiktok", "Prompt Shopee": "shopee"}


def daftar(kind):
    d = load()[kind]
    if not d:
        return ("Daftar %s kosong.\nTambah: /add %s | Judul | isi prompt" %
                (kind, kind))
    return "\n".join(f"{i + 1}. {q['t']}" for i, q in enumerate(d)) + \
        "\n\nLihat isi: /lihat %s <no>" % kind


def cmd(kind, args, chat):
    d = load()
    lst = d[kind]
    if not args:
        return daftar(kind)
    sub = args[0].lower()
    if sub == "lihat" and len(args) >= 2:
        try:
            q = lst[int(args[1]) - 1]
            return f"{q['t']}\n\n{q['x']}"
        except (ValueError, IndexError):
            return "Nomor tak ada."
    if sub in ("add", "tambah") and len(args) >= 2:
        if not unlocked(chat):
            return "Kunci dulu: /pass 777"
        rest = " ".join(args[1:])
        if "|" not in rest:
            return "Format: /add %s | Judul | isi" % kind
        _, t, x = rest.partition("|")
        # format: /add KIND | Judul | isi  -> args[0]=add, args[1]=kind?
        return "Format: /add | Judul | isi (di menu %s)" % kind
    if sub in ("edit", "ubah", "rename", "hapus", "del"):
        if not unlocked(chat):
            return "Kunci dulu: /pass 777"
    if sub in ("edit", "ubah"):
        # /edit <no> | <isi baru>   /edit judul <no> | <judul baru>
        return ("Format: /edit <no> | <isi baru>\n"
                "Ganti judul: /rename <no> | <judul baru>")
    if sub == "rename":
        return "Format: /rename <no> | <judul baru>"
    if sub in ("hapus", "del", "delete"):
        return "Format: /del <no>  (tambah Y di belakang untuk pasti)"
    return daftar(kind)


def do_mutasi(kind, args, chat):
    """Eksekusi mutasi (sudah lolos kunci). Kembalikan teks hasil."""
    d = load()
    lst = d[kind]
    sub = args[0].lower()
    try:
        if sub == "add":
            rest = " ".join(args[1:]).lstrip("| ").strip()
            t, _, x = rest.partition("|")
            if not x.strip():
                return "Format: /add | Judul | isi"
            lst.insert(0, {"t": t.strip() or "Tanpa judul",
                           "x": x.strip()})
            save(d)
            return "Tersimpan #%s di %s." % (1, kind)
        no = int(args[1]) - 1
        q = lst[no]
        if sub in ("edit", "ubah"):
            rest = " ".join(args[2:])
            if not rest.strip().strip("|").strip():
                return "Format: /edit <no> | <isi baru>"
            q["x"] = rest.strip().strip("|").strip()
            save(d)
            return "Isi #%s diubah." % (no + 1)
        if sub == "rename":
            rest = " ".join(args[2:])
            name = rest.strip().strip("|").strip()
            if not name:
                return "Format: /rename <no> | <judul baru>"
            q["t"] = name
            save(d)
            return "Judul #%s jadi: %s" % (no + 1, name)
        if sub in ("hapus", "del", "delete"):
            pasti = len(args) > 2 and args[2].upper() == "Y"
            if not pasti:
                return ("Yakin hapus #%s (%s)? Balas: /del %s %s Y" %
                        (no + 1, q["t"], kind, no + 1))
            lst.pop(no)
            save(d)
            return "Dihapus."
    except (ValueError, IndexError):
        return "Nomor tak ada."
    return "Perintah tak dikenal."


def handle(msg):
    chat = str((msg.get("chat") or {}).get("id", ""))
    text = (msg.get("text") or "").strip()
    if not text or not is_allowed(chat):
        return
    if text == "/start":
        kirim(chat, "Bot Prompt Fashion Radar.\nPilih menu:",
              MENU)
        return
    if text.startswith("/pass"):
        if text.split(None, 1)[-1].strip() == PWD or text.strip() == "/pass 777":
            sesi[chat] = time.time()
            kirim(chat, "Terbuka 30 menit. Perintah ubah aktif.")
        else:
            kirim(chat, "Password salah.")
        return
    if text in KIND:
        kirim(chat, KIND[text].upper() + ":\n" + daftar(KIND[text]))
        return
    if text.startswith("/"):
        parts = text[1:].split()
        if not parts:
            return
        # /add tiktok | ... /lihat shopee 3 /del 2 Y (konteks menu terakhir?)
        # Bentuk: /<aksi> [kind] ...
        first = parts[0].lower()
        kind = None
        rest = parts[1:]
        if rest and rest[0].lower() in ("tiktok", "shopee"):
            kind = rest[0].lower()
            rest = rest[1:]
        if first in ("lihat", "salin", "add", "tambah"):
            if not kind:
                kirim(chat, "Pilih menu dulu: /lihat shopee 3 "
                      "atau buka menu Prompt TikTok/Shopee.")
                return
            if first == "lihat":
                kirim(chat, cmd(kind, ["lihat"] + rest, chat))
            elif first == "salin":
                try:
                    q = load()[kind][int(rest[0]) - 1]
                    kirim(chat, q["x"])
                except (ValueError, IndexError):
                    kirim(chat, "Nomor tak ada. Format: /salin %s <no>"
                          % kind)
            else:
                kirim(chat, do_mutasi(kind, ["add"] + rest, chat)
                      if unlocked(chat) else "Kunci dulu: /pass 777")
            return
        if first in ("edit", "ubah", "rename", "hapus", "del", "delete"):
            if not kind:
                kirim(chat, "Tambah jenis: mis. /edit tiktok 1 | ...")
                return
            kirim(chat, do_mutasi(kind, [first] + rest, chat)
                  if unlocked(chat) else "Kunci dulu: /pass 777")
            return
        kirim(chat, "Perintah: /add /lihat /salin /edit /rename /del "
              "+ jenis (tiktok/shopee). Contoh: /salin shopee 1")
        return


def main():
    if not BOT:
        print("FASHION_RADAR_BOT kosong.")
        return
    check(CHAT)
    off = 0
    print("bot prompt jalan (Ctrl+C berhenti)...")
    while True:
        try:
            r = call("getUpdates", offset=off + 1, timeout=25)
            for u in r.get("result", []):
                off = max(off, u["update_id"])
                if "message" in u:
                    try:
                        handle(u["message"])
                    except PermissionError:
                        pass
                    except Exception as e:
                        print("handler:", str(e)[:100])
        except Exception as e:
            print("poll:", str(e)[:100])
            time.sleep(5)


if __name__ == "__main__":
    main()
