# SATRIA-CHIP Hardware Engine (FPGA Cyclone V)

Direktori ini memuat seluruh rancangan perangkat keras silikon (*Register Transfer Level / RTL*), proyek kompilasi Intel Quartus Prime Lite 24.1, serta kerangka verifikasi simulasi untuk **SATRIA-CHIP: Hardware Security Accelerator Anti-Pencucian Uang (AML) untuk Penegakan Penundaan Transaksi Mencurigakan pada Gateway Perbankan dan Aset Kripto**.

---

## 📁 Struktur Direktori Hardware

```
hardware-satria/
├── rtl/               ──> Berkas Sumber Verilog-2005 (Murni tanpa IP Vendor)
│   ├── sha256_round.v    (Satu ronde kompresi SHA-256 kombinasional)
│   ├── sha256_core.v     (Kompresi blok penuh 512-bit, 65 cycle/blok)
│   ├── hmac_engine.v     (HMAC-SHA256 rekaman & token 3 blok; HASH1 indeks sketch 1 blok)
│   ├── rule_engine.v     (Count-Min Sketch 4x4096 velocity, ambang nominal, anti-replay per klien)
│   ├── key_vault.v       (Kunci write-once LOCK; turunkan K_tok & K_idx; zeroize)
│   ├── audit_log.v       (Ring buffer 256 entri keyed hash-chain anti-tamper)
│   ├── screener_top.v    (Top-level RTL, FSM, Avalon-MM register bus, Decision Unit)
│   ├── uart_bridge.v     (Jembatan UART 115200 8N1 ke bus register Avalon-MM)
│   └── de10_nano_top.v   (Top-level board DE10-Nano: pin clk50, KEY, LED, GPIO)
│
├── quartus/           ──> Proyek Intel/Altera Quartus Prime Lite 24.1
│   ├── screener.qpf      (Berkas proyek Quartus)
│   ├── screener.qsf      (Penugasan pin FPGA Cyclone V 5CSEBA6U23I7)
│   ├── screener.sdc      (Kendala pewaktuan timing clock 50 MHz)
│   └── output_files/     (Bitstream screener.sof; laporan ringkas di docs/quartus/)
│
├── tb/                ──> Kerangka Pengujian Verifikasi Otomatis (cocotb + Python)
│   ├── test_screener.py  (15 skenario + laporan: integritas, replay, velocity, serangan bergantian, tamper)
│   ├── test_random.py    (Regresi acak 10.000 transaksi bit-exact)
│   └── run.py            (Eksekutor testbench cocotb)
│
└── host/              ──> Driver Antarmuka Komunikasi Host Gateway
    ├── aml_gateway_simulator.py (Pengemas transaksi SNAP BI/kripto -> rekaman 64 B + tag HMAC)
    ├── str_generator.py  (Penyusun draf LTKM XML bergaya goAML)
    ├── dashboard/app.py  (Dasbor demo, vonis dari golden model)
    └── demo_uart.py      (Skrip demonstrasi fisik via port UART DE10-Nano)
```

---

## ⚡ Hasil Sintesis & Utilisasi Resource (DE10-Nano Cyclone V)

Hasil kompilasi penuh menggunakan Intel Quartus Prime Lite 24.1 (Device: `5CSEBA6U23I7`):

* **Logic Elements / ALM**: 6.037 / 41.910 ALMs (**14%**)
* **Registers / Flip-Flops**: 11.364 Flip-Flops (**±7%**)
* **Block RAM (M10K)**: 104 blok (**19%**) / 864.768 bit (15%) — sebagian besar untuk Count-Min Sketch
* **DSP Blocks**: **0 DSP (0%)**
* **Fmax Operasional**: **77,38 MHz** (Model Slow -40°C; Setup Slack: +7,08 ns @ 50 MHz)
* **Estimasi Konsumsi Daya**: **553,27 mW @ 50 MHz** (Quartus Power Analyzer, vectorless)
* **Latensi**: 481 cycle (cache hit) / 820 cycle (cache miss); ringkasan perubahan di `docs/verifikasi_2026-10-07.md`

---

## 🧪 Cara Menjalankan Simulasi RTL

Untuk menjalankan verifikasi fungsionalitas logika RTL terhadap Golden Model Python:

```powershell
cd tb
python run.py
```

*Status Verifikasi*: **16/16 tes core PASS** (15 skenario + laporan) dan **10.000 Transaksi Acak Bit-Exact PASS**.
