# Netlist gerbang (post-fit) dari Quartus

`screener_postfit.vo` dihasilkan EDA Netlist Writer Quartus Prime Lite 24.1
(Questa Intel FPGA, Verilog, timescale 1 ps) setelah place & route untuk
5CSEBA6U23I7. Isinya sel primitif Cyclone V yang benar-benar diprogram ke FPGA:

| Sel | Jumlah | Arti |
|---|---|---|
| `cyclonev_lcell_comb` | 10.013 | LUT kombinasional di dalam ALM (pengganti gerbang AND/OR/XOR) |
| `dffeas` | 11.364 | flip-flop (register) |
| `cyclonev_ram_block` | 104 | blok memori M10K (Count-Min Sketch, audit log) |
| `cyclonev_io_ibuf` / `io_obuf` | 4 / 9 | buffer pin I/O |
| `cyclonev_clkena` | 2 | jaringan clock |

Netlist ini dapat disimulasikan di Questa dengan pustaka `cyclonev_ver`
(`altera_mf`, `altera_lnsim`) dari instalasi Quartus.
