# Verifikasi SATRIA-CHIP — 7 Oktober 2026 (revisi Count-Min Sketch)

## Mengapa desain diubah

Uji serangan tambahan pada desain sebelumnya (Account State Memory 64 slot
direct-mapped, indeks = 6 bit bawah ID rekening) menemukan dua kelemahan:

1. **Velocity dapat diakali.** Dua rekening yang jatuh di slot yang sama dan
   bertransaksi bergantian saling menggusur, sehingga hitungan velocity selalu
   kembali ke 1. Uji: 40 transaksi Rp9 juta dalam 40 detik (batas 5/60 detik)
   menghasilkan **0 FLAG**.
2. **Transaksi sah ditolak sebagai REPLAY.** Watermark per slot menolak rekening
   baru bila jam sistem sumber berselisih beberapa detik.

## Perubahan desain

| Bagian | Sebelum | Sesudah |
|---|---|---|
| Velocity | Tabel 64 slot, akun lama tergusur (fail-open) | Count-Min Sketch 4 × 4.096 penghitung di M10K; perkiraan = min antar baris dari (hitungan epoch kini + epoch sebelumnya); tidak pernah menghitung kurang (fail-safe) |
| Indeks | 6 bit bawah ID rekening (dapat dipilih pelaku) | 4 × 12 bit dari `Compress(st_Kidx, akun)`; `K_idx = HMAC(K_master, "PERURI-INDEX-KEY-v1")` diturunkan saat LOCK, tidak pernah keluar chip |
| Jendela | 60 detik, jendela tetap per akun | 2^`CFG_WIN_SHIFT` detik (default 64), dua epoch |
| Anti-replay | Nonce per rekening + watermark per slot | Nonce = nomor urut per klien; tabel 16 klien (id 0–15) dengan jendela geser 64 (gaya IPsec); id di luar 0–15 → `REJECT CLIENT` |
| Reset | — | Sketch disapu bersih 4.096 cycle setelah reset (`STATUS` bit 4) |
| Rule engine | 3 cycle | 4 cycle (pipeline: latch, tahap A, tahap B, keputusan) |

## Hasil

| Pemeriksaan | Hasil | Bukti |
|---|---|---|
| Core RTL | 16/16 lulus (15 skenario + laporan) | `log_simulasi_core.txt`, `hasil_simulasi.md` |
| Serangan 2 rekening bergantian | transaksi ke-6 dst. tiap rekening FLAG (10 dari 20) | `t12_collision_cannot_evade_velocity` |
| Rekening target di antara 300 rekening lain | transaksi ke-6 dst. FLAG | `t13_many_accounts_never_undercount` |
| Selisih jam sumber / nonce terlambat | ACCEPT; replay & nonce di luar jendela REJECT | `t14_replay_window_and_clock_skew` |
| Id klien di luar 0–15 | REJECT CLIENT, klien terdaftar tetap jalan | `t15_client_out_of_range_fail_closed` |
| Regresi acak | 10.000/10.000 bit-exact (seed 20261007, 2.000 rekening, batas velocity 2/64 dtk agar jalur FLAG teruji: 117 FLAG) | `log_regresi_random_10000.txt`, `hasil_regresi_acak.md` |
| UART end-to-end | 1/1 lulus | `log_simulasi_uart.txt` |
| Waveform cache hit | ACCEPT, 481 cycle | `log_simulasi_wave.txt`, `fig/timing_transaksi.png` |
| Bukti formal isolasi kunci (Yosys) | lulus; 9 register rahasia (termasuk `idx_ipad`), 4 kontrol negatif terdeteksi | `log_formal.txt` |
| Quartus fitter | 6.037 ALM (14%), 11.364 register, 104 M10K (19%), 864.768 bit (15%), 0 DSP | `quartus/screener.fit.summary` |
| Timing @50 MHz | Fmax worst-case 77,38 MHz (Slow −40 °C); setup +7,077 ns, hold +0,121 ns minimum | `quartus/screener.sta.rpt` |
| Power Analyzer | 553,27 mW (dinamis 126,67; statis 414,31; I/O 12,29), vectorless, confidence Low | `quartus/screener.pow.rpt` |

Latensi: cache hit 481 cycle (9,62 µs) / cache miss 820 cycle (16,40 µs);
penolakan integritas 407 / 746 cycle. Kapasitas core ±103.950 / 60.976
transaksi/detik sebelum biaya I/O.

Catatan: kompilasi pertama dengan rule engine 3 cycle hanya mencapai Fmax
46,57 MHz (gagal 50 MHz). Rule engine kemudian dipipeline menjadi 4 cycle dan
kompilasi ulang lulus timing dengan margin. Jalur kritis sekarang berada di
logika zeroize key vault (12 ns), bukan di rule engine.

Simulator: Icarus Verilog 14.0 (devel, OSS CAD Suite 2026-10-01) + cocotb 2.1.
Pesan `Simulation failed: -11` di akhir log regresi muncul saat simulator
ditutup, setelah `TESTS=1 PASS=1 FAIL=0` tercetak; seluruh 10.000 transaksi
sudah diperiksa sebelum itu.
