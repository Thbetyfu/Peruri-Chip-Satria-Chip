# Verifikasi versi SystemVerilog (`rtl_sv/`)

`rtl_sv/*.sv` adalah padanan SystemVerilog (IEEE 1800-2017) dari `rtl/*.v`:
`logic`, `always_ff`, `function automatic`, dan FSM `screener_top` memakai
`typedef enum`. Perilaku tidak diubah. Versi Verilog-2005 (`rtl/`) tetap menjadi
sumber yang dikompilasi Quartus.

| Pemeriksaan | Hasil | Log |
|---|---|---|
| Core (`HDL=sv python tb/run.py core`) | 16/16 lulus; latensi 481/820 cycle, sama dengan `.v` | `log_simulasi_core_sv.txt` |
| UART end-to-end (`HDL=sv python tb/run.py uart`) | 1/1 lulus | `log_simulasi_uart_sv.txt` |
| Regresi acak (`HDL=sv RANDOM_N=10000 python tb/run.py random`) | 10.000/10.000 bit-exact dengan golden model | `log_regresi_random_10000_sv.txt` |
| Sintesis Yosys (`read_verilog -sv`) | berhasil, tanpa error | — |

Simulator: Icarus Verilog 14.0 (devel) `-g2012` + cocotb 2.1.
