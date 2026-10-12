# Trend Product Finder — Next Steps

## Done ✅ (s/d 2026-10-10)
- Web `web/` (serve `:8001`) + Space live `0b7f826` (521 item)
- 12 tab: Semua/Google/Shopee by Google/TikTok by Google/Shopee/
  Shopee via Iklan/TikTok/Trend TikTok via Iklan/Pembeli Berulang Teratas/
  Prompt/7-30 Hari
- Buyer 2-tier (terjual → ulasan) + tombol hijau=Tokopedia/hitam=TikTok
- Iklan: 30 Captapi + 28 BigSpy + 1 user (badge likes/CTR/tayang, flag NAIK)
- Dork massal: 17 kat TikTok (134 video) + 17 kat Shopee (79 produk)
- Prompt tab: CRUD localStorage + Rename + Copy Prompt + password Ubah/Hapus/Rename + tooltip
- State-persist + PWA (sw fr-v4, banner jadwal+kuota, auto-reload)
- Kolektor: SocialCrawl Shop (94/100, `socialcrawl_collect.py` mingguan),
  Captapi (cache=true), tiktok_ads standby, herus13 mati-kredit
- GH secrets: APIFY_TOKEN + CAPTAPI_KEY + SOCIALCRAWL_KEY @ trend-fashion-auto
- HIJAB/MUKENA MASUK radar (cabut HIJAB OUT, 10 Okt)

## Done ✅ (11-12 Okt)
- Prompt: textarea besar + tab TikTok/Shopee pisah
  (frprompts/frprompts_shopee), 777 Rename/Ubah/Hapus dua-duanya
- Insiden 5 tab hilang (regex) → pulih, 13 tab. Live `d527b80`
- Repo `akankah-org/trend-product-finder` + refresh mingguan +
  monitor harian per-tab (SUCCESS). Secrets baru @ repo itu.
  Notif deploy=Opencodeku, cron=fashion bot (START dulu)
- `notify.py` + `monitor.py` (STALE >7h)

## Current State
- Live: `d527b80` (13 tab, prompt ganda)
- Kuota: Syphoon 3/40 • Apify $0,0008 HABIS • Captapi +-80/100
  • SocialCrawl 94/100 (pakai 6)
- OPEN: subdomain akankah.eu.org (A/B/C) + enrich sold (detail 503)

## Immediate Next Steps

### 1. Subdomain akankah.eu.org (tunggu keputusan user)
- A: Pages baru + `radar.akankah.eu.org` (long-term)
- B: CNAME → HF Space (cepat)
- C: Worker proxy (tengah)

### 2. Kredit Apify (blokir Shop refresh + enrich iklan)
- Top-up terkecil ATAU kurasi manual Top Ads (gratis)
- Setelah ada: herus13 enrich 38 iklan (sold/harga) + refresh Shop

### 3. Refresh iklan berkala (murah, Captapi cache=true = 0 kredit)
- Per leaderboard baru / setelah cache 24 jam basi
- Query multi-kategori; pool ±20/query (q hanya ranking ulang)

## Rules (tetap)
- `node --check` tiap file JS sebelum deploy; deploy = `_dep` pull/copy/push
- Guard kuota: Syphoon ≤40, Shop ≤1x/minggu, Captapi cache=true dulu
- Tanpa filter kategori di buyer/iklan (keputusan user 2026-10-05/08)
- Angka tampil = lacak ke snapshot+tanggal; sold/harga tak-terverifikasi = flag
- Secret: file lokal + vault + GH; dilarang di repo/chat/temp-menetap

## Run Commands
```bash
python web\serve.py            # lokal :8001 (quote path ber-spasi!)
python tiktok_apify.py --test  # 1 keyword (kecuali kredit habis)
```
