Seed 20261007, 10000 transaksi, batas velocity 2/64 dtk, 2000 akun (8 akun lonjakan), sketch 4x4096, 5 klien.

| Jenis transaksi | Verdict | Jumlah |
|---|---|---|
| bitflip | REJECT | 802 |
| jam_mundur | ACCEPT | 638 |
| jam_mundur | FLAG | 6 |
| klien_bentrok | REJECT | 208 |
| kunci_klien_lain | REJECT | 472 |
| nominal_besar | ESCALATE | 805 |
| nonce_terlambat | ACCEPT | 223 |
| nonce_terlambat | FLAG | 2 |
| nonce_terlambat | REJECT | 193 |
| replay | REJECT | 1199 |
| sah | ACCEPT | 4838 |
| sah | FLAG | 109 |
| tag_salah | REJECT | 505 |
| **total** | **semua bit-exact dengan golden model** | **10000** |
