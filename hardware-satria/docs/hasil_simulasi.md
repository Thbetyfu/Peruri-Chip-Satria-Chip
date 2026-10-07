| Skenario | Hasil | Keterangan | Cycle |
|---|---|---|---|
| transaksi sah (klien baru: turunkan kunci) | ACCEPT | - | 820 |
| transaksi sah | ACCEPT | - | 481 |
| bit-flip rekaman bit 255 | REJECT | INTEGRITY | 746 |
| bit-flip rekaman bit 300 | REJECT | INTEGRITY | 407 |
| bit-flip rekaman bit 511 | REJECT | INTEGRITY | 407 |
| bit-flip rekaman bit 76 | REJECT | INTEGRITY | 407 |
| bit-flip rekaman bit 299 | REJECT | INTEGRITY | 407 |
| bit-flip rekaman bit 441 | REJECT | INTEGRITY | 407 |
| bit-flip rekaman bit 418 | REJECT | INTEGRITY | 407 |
| bit-flip pada tag | REJECT | INTEGRITY | 407 |
| transaksi asli setelah serangan | ACCEPT | - | 481 |
| transaksi sah | ACCEPT | - | 820 |
| token disubmit sebagai transaksi | REJECT | INTEGRITY|DOMAIN | 746 |
| transaksi nonce 10 | ACCEPT | - | 820 |
| replay transaksi yang sama | REJECT | REPLAY | 481 |
| nonce 9 terlambat, belum dipakai | ACCEPT | - | 481 |
| replay nonce 9 | REJECT | REPLAY | 481 |
| nonce baru (11) | ACCEPT | - | 481 |
| lonjakan akun #1 dlm 64 dtk | ACCEPT | - | 820 |
| lonjakan akun #2 dlm 64 dtk | ACCEPT | - | 481 |
| lonjakan akun #3 dlm 64 dtk | ACCEPT | - | 481 |
| lonjakan akun #4 dlm 64 dtk | ACCEPT | - | 481 |
| lonjakan akun #5 dlm 64 dtk | ACCEPT | - | 481 |
| lonjakan akun #6 dlm 64 dtk | FLAG | VELOCITY | 481 |
| lonjakan akun #7 dlm 64 dtk | FLAG | VELOCITY | 481 |
| setelah jendela waktu lewat | ACCEPT | - | 481 |
| nominal di atas batas | ESCALATE | AMOUNT | 481 |
| log #0 | ESCALATE | AMOUNT | 820 |
| log #1 | ACCEPT | - | 481 |
| log #2 | ESCALATE | AMOUNT | 481 |
| log #3 | ACCEPT | - | 481 |
| log #4 | REJECT | INTEGRITY | 407 |
| log #5 | ACCEPT | - | 481 |
| log #6 | ESCALATE | AMOUNT | 481 |
| log #7 | ACCEPT | - | 481 |
| log #8 | ACCEPT | - | 481 |
| log #9 | ACCEPT | - | 481 |
| verifikasi log asli | OK | rantai utuh (10 entri) | - |
| log: entri REJECT diubah jadi ACCEPT | TERDETEKSI | rantai putus pada seq 4 | - |
| log: entri #6 dihapus | TERDETEKSI | celah/urutan seq: harap 6, dapat 7 | - |
| log: urutan entri ditukar | TERDETEKSI | rantai putus pada seq 2 | - |
| isi cache kunci klien | ACCEPT | - | 820 |
| sapu 256 alamat bus: kunci master/token/klien/indeks & ipad/opad | TIDAK BOCOR | kunci mentah = 0 setelah LOCK | - |
| sebelum serangan | ACCEPT | - | 820 |
| host menulis ulang kunci setelah LOCK | TAMPER | zeroize, semua REJECT, token=0 | - |
| host melonggarkan aturan setelah LOCK | TAMPER | kebijakan tetap | - |
| sinyal sensor tamper eksternal | TAMPER | zeroize | - |
| chip belum diprovisioning | REJECT | fail-closed | - |
| klien A dengan kunci A | ACCEPT | - | 820 |
| klien B ditandatangani kunci A (bocor) | REJECT | INTEGRITY | 746 |
| klien B dengan kunci B | ACCEPT | - | 481 |
| id klien diganti host | REJECT | INTEGRITY | 407 |
| tag dengan kunci master langsung | REJECT | INTEGRITY | 746 |
| token log diverifikasi hanya dengan K_tok | OK | backend tidak memegang K_master/K_client | - |
| bergantian 0x1000 #1 | ACCEPT | - | 820 |
| bergantian 0x1040 #1 | ACCEPT | - | 481 |
| bergantian 0x1000 #2 | ACCEPT | - | 481 |
| bergantian 0x1040 #2 | ACCEPT | - | 481 |
| bergantian 0x1000 #3 | ACCEPT | - | 481 |
| bergantian 0x1040 #3 | ACCEPT | - | 481 |
| bergantian 0x1000 #4 | ACCEPT | - | 481 |
| bergantian 0x1040 #4 | ACCEPT | - | 481 |
| bergantian 0x1000 #5 | ACCEPT | - | 481 |
| bergantian 0x1040 #5 | ACCEPT | - | 481 |
| bergantian 0x1000 #6 | FLAG | VELOCITY | 481 |
| bergantian 0x1040 #6 | FLAG | VELOCITY | 481 |
| bergantian 0x1000 #7 | FLAG | VELOCITY | 481 |
| bergantian 0x1040 #7 | FLAG | VELOCITY | 481 |
| bergantian 0x1000 #8 | FLAG | VELOCITY | 481 |
| bergantian 0x1040 #8 | FLAG | VELOCITY | 481 |
| bergantian 0x1000 #9 | FLAG | VELOCITY | 481 |
| bergantian 0x1040 #9 | FLAG | VELOCITY | 481 |
| bergantian 0x1000 #10 | FLAG | VELOCITY | 481 |
| bergantian 0x1040 #10 | FLAG | VELOCITY | 481 |
| 2 rekening bergantian, 20 transaksi Rp9 juta / 20 dtk | FLAG | 10 dari 20 ditandai | - |
| target #1 di tengah 300 rekening | ACCEPT | - | 820 |
| target #2 di tengah 300 rekening | ACCEPT | - | 481 |
| target #3 di tengah 300 rekening | ACCEPT | - | 481 |
| target #4 di tengah 300 rekening | ACCEPT | - | 481 |
| target #5 di tengah 300 rekening | ACCEPT | - | 481 |
| target #6 di tengah 300 rekening | FLAG | VELOCITY | 481 |
| target #7 di tengah 300 rekening | FLAG | VELOCITY | 481 |
| target #8 di tengah 300 rekening | FLAG | VELOCITY | 481 |
| rek A ts=5000 | ACCEPT | - | 820 |
| rek B nonce 12 | ACCEPT | - | 481 |
| rek C BARU, klien lain, jam mundur 2 dtk | ACCEPT | - | 820 |
| nonce 11 datang terlambat (masih di jendela) | ACCEPT | - | 820 |
| nonce 11 diputar ulang | REJECT | REPLAY | 481 |
| nonce melompat ke 100 | ACCEPT | - | 481 |
| nonce 36 (di luar jendela 64) | REJECT | REPLAY | 481 |
| nonce 37 (tepi jendela, belum dipakai) | ACCEPT | - | 481 |
| klien 0x01 (slot 1) | ACCEPT | - | 820 |
| klien 0x11 (di luar 0..15) | REJECT | CLIENT | 820 |
| klien 0x01 tetap berjalan | ACCEPT | - | 820 |
