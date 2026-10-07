# SATRIA-CHIP Hardware Engine (FPGA Cyclone V)

Direktori ini memuat seluruh rancangan perangkat keras silikon (*Register Transfer Level / RTL*), proyek kompilasi Intel Quartus Prime Lite 24.1, serta kerangka verifikasi simulasi untuk **SATRIA-CHIP: Hardware Security Accelerator Anti-Pencucian Uang (AML) untuk Penegakan Penundaan Transaksi Mencurigakan pada Gateway Perbankan dan Aset Kripto**.

---

## 📁 Struktur Direktori Hardware

```
hardware-satria/
├── rtl/               ──> Berkas Sumber Verilog-2005 (Murni tanpa IP Vendor)
│   ├── sha256_round.v    (Satu ronde kompresi SHA-256 kombinasional)
│   ├── sha256_core.v     (Kompresi blok penuh 512-bit, 65 cycle/blok)
│   ├── hmac_engine.v     (Mesin HMAC-SHA256 rekaman & token, 3 blok SHA)
│   ├── rule_engine.v     (Velocity per rekening, ambang nominal, anti-replay, 64-slot RAM)
│   ├── key_vault.v       (State machine kunci, write-once LOCK, reset zeroize)
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
│   ├── test_screener.py  (12 skenario + laporan: integritas, replay, velocity, tamper)
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

* **Logic Elements / ALM**: 4.346 / 41.910 ALMs (**10%**)
* **Registers / Flip-Flops**: 8.568 Flip-Flops (**±5%**)
* **Block RAM (M10K)**: 15 blok (**±3%** blok) / 93.696 bit (1,7%)
* **DSP Blocks**: **0 DSP (0%)**
* **Fmax Operasional**: **75,04 MHz** (Model Slow -40°C; Setup Slack: +6,67 ns @ 50 MHz)
* **Estimasi Konsumsi Daya**: **493,84 mW @ 50 MHz** (Quartus Power Analyzer)

---

## 🧪 Cara Menjalankan Simulasi RTL

Untuk menjalankan verifikasi fungsionalitas logika RTL terhadap Golden Model Python:

```powershell
cd tb
python run.py
```

*Status Verifikasi*: **13/13 tes core PASS** (12 skenario + laporan) dan **10.000 Transaksi Acak Bit-Exact PASS**.
