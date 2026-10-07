# Skematik dari Quartus Prime Lite 24.1

Semua berkas diekspor langsung dari Netlist Viewer Quartus (File → Export,
PDF vektor; perbesar di pembaca PDF untuk melihat detail) pada hasil
kompilasi 7 Oktober 2026 (6.037 ALM, 104 M10K, Fmax 77,38 MHz).

| Berkas | Isi |
|---|---|
| `01_RTL_top_level.pdf` | RTL Viewer: `de10_nano_top` — pin board, `rst_sync`, `uart_bridge`, `screener_top` |
| `02_RTL_screener_top_lengkap.pdf` | RTL Viewer: isi `screener_top` diekspansi (register, multiplexer, FSM, `hmac_engine`, `key_vault`, `rule_engine`, `audit_log`) |
| `03_PostFit_top_level.pdf` | Technology Map Viewer (Post-Fitting): netlist hasil place & route tingkat atas |
| `04_PostFit_rule_engine_gerbang.pdf` | Technology Map Viewer (Post-Fitting): `rule_engine` sampai tingkat sel Cyclone V (LUT/ALM, register, blok M10K) — inilah "gerbang" yang sebenarnya diimplementasikan di FPGA |
| `04_cuplikan_zoom_rule_engine.png` | Cuplikan perbesaran 04: kotak ungu = sel kombinasional (LUT), kotak hijau-biru = register (flip-flop) |

Catatan: FPGA tidak memakai gerbang AND/OR diskret; logika dipetakan ke LUT
6-input di dalam ALM. Skematik post-fit menunjukkan sel-sel tersebut beserta
sambungannya, sesuai yang diprogram ke chip Cyclone V 5CSEBA6U23I7.
