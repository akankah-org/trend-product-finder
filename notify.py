# -*- coding: utf-8 -*-
"""Kirim notif Telegram. Dipakai skrip deploy manual.
Sumber token: credential/telegram_bots.txt (lokal, gitignored) atau env.
Pakai: python notify.py <bot> <pesan...>   (bot: fashion | opencodeku)
"""
import os
import sys
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))


def load_tokens():
    toks = {}
    try:
        for ln in open(os.path.join(BASE, "credential", "telegram_bots.txt"),
                       encoding="utf-8"):
            if "=" in ln:
                k, v = ln.strip().split("=", 1)
                toks[k.strip()] = v.strip()
    except Exception:
        pass
    toks.setdefault("FASHION_RADAR_BOT", os.environ.get("FASHION_BOT", ""))
    toks.setdefault("OPENCODEKU_BOT", os.environ.get("OPENCODEKU_BOT", ""))
    toks.setdefault("TELEGRAM_CHAT_ID",
                    os.environ.get("TELEGRAM_CHAT_ID", "8772898381"))
    return toks


def send(bot_token, chat_id, text):
    data = urllib.parse.urlencode(
        {"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/sendMessage", data=data)
    return urllib.request.urlopen(req, timeout=30).read()[:60]


if __name__ == "__main__":
    which = (sys.argv[1] if len(sys.argv) > 1 else "fashion").lower()
    msg = " ".join(sys.argv[2:]) or "(tes notif)"
    toks = load_tokens()
    token = toks["FASHION_RADAR_BOT" if which == "fashion"
                 else "OPENCODEKU_BOT"]
    print(send(token, toks["TELEGRAM_CHAT_ID"], msg))
