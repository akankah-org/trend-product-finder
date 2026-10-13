# -*- coding: utf-8 -*-
"""Kunci akses Telegram fashion radar: HANYA ID pemilik.
Pola sama seperti proxyhfku (TELEGRAM_ALLOWED_CHAT_IDS).
Pakai di SEMUA kode yang kirim/terima Telegram.
"""
import os

OWNER_ID = "8772898381"


def allowed_ids():
    raw = os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "") or OWNER_ID
    return {c.strip() for c in raw.split(",") if c.strip()}


def is_allowed(chat_id):
    ids = allowed_ids()
    return (not ids) or (str(chat_id) in ids)


def check(chat_id):
    if not is_allowed(chat_id):
        raise PermissionError(
            f"chat_id {chat_id} tidak diizinkan (hanya pemilik)")
