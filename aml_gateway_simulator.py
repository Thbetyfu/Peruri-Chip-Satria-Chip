"""
SATRIA-CHIP: Financial Gateway Ingestion Simulator
Mengonversi instruksi transaksi (SNAP BI / bursa aset kripto) menjadi rekaman 64 byte
+ tag HMAC-SHA256 32 byte, persis seperti format yang diperiksa chip (lihat screener_top.v).

Kunci klien diturunkan dengan fungsi yang SAMA dengan golden model dan RTL
(golden.client_key), sehingga rekaman dari simulator ini lolos Integrity Gate di board.
"""

import hashlib
import os
import struct
import sys
import time
from typing import Any, Dict, Tuple

_here = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_here, "hardware-satria", "model"), os.path.join(_here, "..", "model")):
    if os.path.isfile(os.path.join(_p, "golden.py")) and _p not in sys.path:
        sys.path.insert(0, _p)
import golden as G  # noqa: E402

DOMAIN_TXN = G.DOM_TXN

# Tipe transaksi (byte 1 rekaman) - informatif, tidak memengaruhi aturan di chip
TYPE_BANK_TRANSFER = 0x10   # transfer / valas via SNAP BI, BI-FAST
TYPE_CRYPTO_CEX = 0x20      # deposit / penarikan bursa kripto terpusat
TYPE_CRYPTO_DEX = 0x21      # bridge / swap ke alamat unhosted

DEMO_MASTER_KEY = bytes.fromhex("c0ffee00" * 2 + "5ec0de11" * 2 + "0badf00d" * 2 + "deadbeef" * 2)


class AMLGatewaySimulator:
    def __init__(self, master_key: bytes = DEMO_MASTER_KEY):
        # Di sistem nyata kunci master hanya ada di chip; tiap institusi hanya memegang
        # K_client miliknya. Simulator memegang master hanya untuk keperluan demo.
        self.master_key = master_key

    def client_key(self, client_id: int) -> bytes:
        return G.client_key(self.master_key, client_id)

    def _pack(self, ttype: int, client_id: int, ts: int, nonce: int, account: int, amount: int,
              dest: bytes) -> Tuple[bytes, bytes]:
        dest_hash = hashlib.sha256(dest).digest()
        rec = struct.pack(">BBHIQQQ", DOMAIN_TXN, ttype, client_id, ts, nonce, account, amount) + dest_hash
        assert len(rec) == 64
        return rec, G.tag_of(self.client_key(client_id), rec)

    def parse_snap_bi_transfer(self, p: Dict[str, Any]) -> Tuple[bytes, bytes]:
        """Instruksi transfer bergaya SNAP BI -> (rekaman 64 B, tag 32 B)."""
        dest = f"{p.get('beneficiary_bank')}:{p.get('beneficiary_account')}".encode()
        return self._pack(TYPE_BANK_TRANSFER, int(p.get("partner_id", 1)), int(p.get("timestamp", time.time())),
                          int(p.get("nonce", 1)), int(p.get("source_account", 10001)),
                          int(p.get("amount", 50_000_000)), dest)

    def parse_crypto_deposit(self, p: Dict[str, Any]) -> Tuple[bytes, bytes]:
        """Instruksi deposit/penarikan bursa kripto -> (rekaman 64 B, tag 32 B).
        Nominal dinyatakan dalam ekuivalen Rupiah agar ambang nominal chip berlaku seragam."""
        ttype = TYPE_CRYPTO_CEX if p.get("is_cex", True) else TYPE_CRYPTO_DEX
        dest = str(p.get("destination_wallet", "0x0")).encode()
        return self._pack(ttype, int(p.get("exchange_id", 2)), int(p.get("timestamp", time.time())),
                          int(p.get("nonce", 1)), int(p.get("kyc_user_id", 20002)),
                          int(p.get("amount_idr", 10_000_000)), dest)


if __name__ == "__main__":
    sim = AMLGatewaySimulator()
    rec, tag = sim.parse_snap_bi_transfer({"partner_id": 1, "source_account": 9876543210,
                                           "beneficiary_bank": "CHASUS33XXX", "beneficiary_account": "8821992019",
                                           "amount": 25_000_000, "nonce": 101, "timestamp": int(time.time())})
    chip = G.Screener(key=DEMO_MASTER_KEY, policy=G.Policy(amount_limit=100_000_000))
    v, r, seq, _ = chip.process(rec, tag)
    print("Rekaman :", rec.hex()[:32], "...")
    print("Tag HMAC:", tag.hex()[:32], "...")
    print("Vonis golden model:", G.VERDICT_NAME[v], G.reasons_str(r))
