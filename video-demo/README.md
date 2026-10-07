# Video Demo SATRIA-CHIP (Remotion)

Video penjelasan 3 menit (1920×1080, 30 fps, 5.400 frame) untuk PERURI Chip Hackathon 2026.
Dibuat dengan [Remotion](https://remotion.dev) mengikuti aturan skill
[`claude-remotion-skill`](https://github.com/haidrrrry/claude-remotion-skill):
tanpa easing linear, entrance 2–3 properti dengan stagger, exit lebih cepat dari entrance,
lima lapis (mesh → konten → grade → grain → vignette), satu warna hero per frame, dan SFX
dimulai 3 frame sebelum visual mendarat.

## Isi video

| Waktu | Adegan | Isi |
|---|---|---|
| 0:00 | Hook | Rp286,82 T perputaran dana judi online 2025 |
| 0:10 | Urgensi | 183.281 LTKM, penundaan transaksi +484,8%, ±Rp30 T via kripto, 5,2 miliar anomali (PPATK, BSSN) |
| 0:35 | Celah | Akses root bisa mematikan filter, melonggarkan ambang, menghapus log |
| 0:50 | Solusi | SATRIA-CHIP |
| 1:01 | Arsitektur | 4 tier, gambar arsitektur proposal |
| 1:20 | Pipeline | 5 tahap on-chip, 411 cycle = 8,22 µs |
| 1:40 | Demo | 7 skenario: ACCEPT, FLAG, ESCALATE, REJECT (integrity, replay), TAMPER |
| 2:12 | Audit log | Hash-chain; ubah seq 7 → rantai putus |
| 2:26 | Bukti | 10.000/10.000 bit-exact, 13/13, Fmax 75,04 MHz, 10% ALM, dll. |
| 2:45 | Penutup | Rencana bootcamp 3 hari dan kartu akhir |

Semua angka punya sumber (lihat `src/data.ts`). Baris demo dan rantai audit adalah **keluaran nyata**
golden model (`hardware-satria/model/golden.py`) yang bit-exact dengan RTL, bukan angka karangan.
Video menyebut jelas bahwa uji on-board DE10-Nano dijadwalkan saat bootcamp.

## Render dengan Remotion (laptop dengan internet)

```bash
cd video-demo
npm install
npm run audio        # sintesis musik + SFX ke public/audio (deterministik)
npm run studio       # pratinjau interaktif
npm run render       # out/satria-chip-demo.mp4 (h264, crf 16)
```

## Render tanpa npm (`render-local/`)

MP4 yang dikirim bersama proyek ini dirender di lingkungan tanpa akses npm:
- `render-local/remotion-shim.tsx` menggantikan paket `remotion`. Fungsi animasi `interpolate`,
  `spring`, `Easing`, `interpolateColors` adalah **kode sumber asli Remotion 4.0.534**
  (`render-local/vendor-remotion-core`, lisensi Remotion). `Sequence`, `AbsoluteFill`, `Img`,
  `staticFile`, `delayRender` diimplementasikan ulang untuk subset yang dipakai proyek ini.
- `render-local/render.mjs` membundel dengan esbuild, merender tiap frame di Chromium (Playwright),
  meng-encode dengan ffmpeg (libx264, CRF 16), lalu me-mix musik dan SFX sesuai `src/audio.ts`.

```bash
node render-local/render.mjs --stills 300,2400   # cek frame tertentu
node render-local/render.mjs --video --workers 2 # video penuh
```

## Lisensi aset
- Font Inter / Inter Display: SIL Open Font License (`public/fonts/LICENSE-Inter.txt`).
- DejaVu Sans Mono: lisensi bebas Bitstream Vera/DejaVu (`public/fonts/LICENSE-DejaVu.txt`).
- Musik dan SFX: disintesis oleh `scripts/gen-audio.mjs`, tanpa aset pihak ketiga.
- Remotion: [Remotion License](https://remotion.dev/license) — gratis untuk individu dan tim kecil.
