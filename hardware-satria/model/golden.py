"""Golden model (referensi Python) untuk Integrity-Gated Transaction Screener.

Dipakai oleh testbench cocotb dan skrip host demo. Semua perilaku chip
(HMAC, aturan, verdict token, rantai log) direplikasi di sini sehingga
RTL dapat dibandingkan bit-per-bit.
"""
import hashlib
import hmac
import struct
from dataclasses import dataclass, field

DOM_TXN = 0x01
DOM_TOKEN = 0x02

ACCEPT, FLAG, ESCALATE, REJECT = 0, 1, 2, 3
VERDICT_NAME = {ACCEPT: "ACCEPT", FLAG: "FLAG", ESCALATE: "ESCALATE", REJECT: "REJECT"}

R_INTEGRITY, R_REPLAY, R_VELOCITY, R_AMOUNT, R_DOMAIN, R_VAULT, R_CLIENT = (1 << i for i in range(7))
REASON_NAME = {R_INTEGRITY: "INTEGRITY", R_REPLAY: "REPLAY", R_VELOCITY: "VELOCITY",
               R_AMOUNT: "AMOUNT", R_DOMAIN: "DOMAIN", R_VAULT: "VAULT", R_CLIENT: "CLIENT"}


def reasons_str(r: int) -> str:
    return "|".join(n for b, n in REASON_NAME.items() if r & b) or "-"


def make_record(account: int, nonce: int, amount: int, tstamp: int,
                doc: bytes = b"dokumen", ttype: int = 1, domain: int = DOM_TXN,
                client: int = 1) -> bytes:
    """Rekaman transaksi 64 byte (lihat format di screener_top.v).
    Byte 2-3 = id klien (penerbit) yang menentukan kunci HMAC-nya."""
    doc_hash = hashlib.sha256(doc).digest()
    rec = struct.pack(">BBHIQQQ", domain, ttype, client, tstamp, nonce, account, amount) + doc_hash
    assert len(rec) == 64
    return rec


def tag_of(key: bytes, msg: bytes) -> bytes:
    return hmac.new(key, msg, hashlib.sha256).digest()


# ---------------------------------------------------------------- hierarki kunci
MSG_TOK = b"PERURI-TOKEN-KEY-v1".ljust(64, b"\0")
MSG_CLK = b"PERURI-CLIENT-KEY-v1".ljust(62, b"\0")


def token_key(master: bytes) -> bytes:
    """K_tok = HMAC(K_master, "PERURI-TOKEN-KEY-v1") - dipegang backend/auditor."""
    return tag_of(master, MSG_TOK)


def client_key(master: bytes, client: int) -> bytes:
    """K_client = HMAC(K_master, "PERURI-CLIENT-KEY-v1" || id) - dipegang klien."""
    return tag_of(master, MSG_CLK + struct.pack(">H", client))


MSG_IDX = b"PERURI-INDEX-KEY-v1".ljust(64, b"\0")

# ------------------------------------------------- kompresi SHA-256 (state bebas)
_K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]
SHA_IV = bytes.fromhex("6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19")


def _rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF


def sha256_compress(state: bytes, block: bytes) -> bytes:
    """Satu kompresi SHA-256 dengan state awal bebas (sama dengan sha256_core.v)."""
    w = list(struct.unpack(">16I", block))
    for i in range(16, 64):
        s0 = _rotr(w[i-15], 7) ^ _rotr(w[i-15], 18) ^ (w[i-15] >> 3)
        s1 = _rotr(w[i-2], 17) ^ _rotr(w[i-2], 19) ^ (w[i-2] >> 10)
        w.append((w[i-16] + s0 + w[i-7] + s1) & 0xFFFFFFFF)
    h = list(struct.unpack(">8I", state))
    a, b, c, d, e, f, g, hh = h
    for i in range(64):
        t1 = (hh + (_rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)) + ((e & f) ^ (~e & g)) + _K[i] + w[i]) & 0xFFFFFFFF
        t2 = ((_rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & 0xFFFFFFFF
        hh, g, f, e, d, c, b, a = g, f, e, (d + t1) & 0xFFFFFFFF, c, b, a, (t1 + t2) & 0xFFFFFFFF
    return struct.pack(">8I", *[(x + y) & 0xFFFFFFFF for x, y in zip(h, [a, b, c, d, e, f, g, hh])])


def index_state(master: bytes) -> bytes:
    """State ipad K_idx; K_idx = HMAC(K_master, "PERURI-INDEX-KEY-v1") diturunkan saat LOCK."""
    k_idx = tag_of(master, MSG_IDX)
    return sha256_compress(SHA_IV, bytes(b ^ 0x36 for b in k_idx.ljust(64, b"\0")))


def account_indices(idx_state: bytes, account: int, rows: int = 4, bits: int = 12):
    """Indeks sketch per baris = potongan H_K(akun); tidak dapat diprediksi tanpa kunci chip."""
    d = int.from_bytes(sha256_compress(idx_state, struct.pack(">Q", account) + bytes(56)), "big")
    return [(d >> (256 - bits * (r + 1))) & ((1 << bits) - 1) for r in range(rows)]


def client_of(rec: bytes) -> int:
    return struct.unpack(">H", rec[2:4])[0]


def sign_txn(master: bytes, rec: bytes) -> bytes:
    """Tag yang dibuat klien sah untuk rekamannya (memakai K_client miliknya)."""
    return tag_of(client_key(master, client_of(rec)), rec)


def token_msg(verdict: int, reasons: int, seq: int, txn_tag: bytes, prev: bytes) -> bytes:
    m = struct.pack(">BBHI", DOM_TOKEN, verdict, reasons, seq) + txn_tag[:24] + prev
    assert len(m) == 64
    return m


@dataclass
class Policy:
    window_shift: int = 6          # jendela velocity = 2^6 = 64 detik
    vel_limit: int = 5
    amount_limit: int = 10_000_000


SKETCH_ROWS = 4
CLIENT_SLOTS = 16
REPLAY_WIN = 64


@dataclass
class Screener:
    """Model bit-exact screener_top.

    Anti-replay : nonce adalah nomor urut per klien (institusi). Tabel 16 klien
                  (id 0..15, slot = id) dengan jendela geser 64 nonce.
                  Id klien di luar 0..15 -> REJECT CLIENT (fail-closed).
    Velocity    : Count-Min Sketch 4 baris x 2^idx_bits penghitung, indeks dari
                  H_Kidx(akun). Tiap penghitung menyimpan {epoch, cur, prev};
                  perkiraan = cur + prev (dua epoch 2^window_shift detik), lalu
                  diambil minimum antar baris. Tabrakan hanya menaikkan perkiraan,
                  tidak pernah menurunkan (fail-safe).
    """
    key: bytes
    policy: Policy = field(default_factory=Policy)
    idx_bits: int = 12
    sketch: list = None
    clients: dict = field(default_factory=dict)
    seq: int = 0
    head: bytes = bytes(32)
    log: list = field(default_factory=list)

    def __post_init__(self):
        if self.sketch is None:
            self.sketch = [dict() for _ in range(SKETCH_ROWS)]
        self._idx_state = index_state(self.key)

    def _replay(self, client: int, nonce: int):
        """Kembalikan (client_reject, replay, state_baru)."""
        if client >= CLIENT_SLOTS:
            return True, False, None
        ent = self.clients.get(client)
        if ent is None:
            return False, False, {"id": client, "hi": nonce, "bm": 1}
        hi, bm = ent["hi"], ent["bm"]
        if nonce > hi:
            d = nonce - hi
            nbm = 1 if d >= REPLAY_WIN else ((bm << d) | 1) & ((1 << REPLAY_WIN) - 1)
            return False, False, {"id": client, "hi": nonce, "bm": nbm}
        off = hi - nonce
        if off >= REPLAY_WIN or (bm >> off) & 1:
            return False, True, None
        return False, False, {"id": client, "hi": hi, "bm": bm | (1 << off)}

    def _velocity(self, account: int, tstamp: int):
        e = (tstamp >> self.policy.window_shift) & 0xFFFF
        em1 = (e - 1) & 0xFFFF
        idx = account_indices(self._idx_state, account, SKETCH_ROWS, self.idx_bits)
        est, writes = None, []
        for r, i in enumerate(idx):
            tag, c, p = self.sketch[r].get(i, (0, 0, 0))
            cur = c if tag == e else 0
            prev = p if tag == e else (c if tag == em1 else 0)
            ncur = cur if cur == 0xFFFF else cur + 1
            v = ncur + prev
            est = v if est is None else min(est, v)
            writes.append((r, i, (e, ncur, prev)))
        return est, writes

    def process(self, rec: bytes, tag: bytes):
        """Kembalikan (verdict, reasons, seq, token) persis seperti RTL."""
        domain = rec[0]
        client = client_of(rec)
        tstamp, nonce, account, amount = struct.unpack(">IQQQ", rec[4:32])
        calc = sign_txn(self.key, rec)
        if domain != DOM_TXN or calc != tag:
            verdict = REJECT
            reasons = (R_DOMAIN if domain != DOM_TXN else 0) | (R_INTEGRITY if calc != tag else 0)
        else:
            c_rej, replay, cstate = self._replay(client, nonce)
            if c_rej or replay:
                verdict = REJECT
                reasons = R_CLIENT if c_rej else R_REPLAY
            else:
                est, writes = self._velocity(account, tstamp)
                vel = est > self.policy.vel_limit
                amt = amount > self.policy.amount_limit
                self.clients[client] = cstate
                for r, i, v in writes:
                    self.sketch[r][i] = v
                reasons = (R_VELOCITY if vel else 0) | (R_AMOUNT if amt else 0)
                verdict = ESCALATE if amt else FLAG if vel else ACCEPT
        seq = self.seq
        token = tag_of(token_key(self.key), token_msg(verdict, reasons, seq, tag, self.head))
        self.log.append({"seq": seq, "verdict": verdict, "reasons": reasons,
                         "txn_tag24": tag[:24], "token": token})
        self.seq += 1
        self.head = token
        return verdict, reasons, seq, token


def verify_chain(tok_key: bytes, entries, start_prev: bytes = bytes(32), start_seq: int = 0):
    """Verifikator backend: periksa urutan seq dan setiap mata rantai token.
    tok_key = K_tok (backend tidak perlu K_master maupun kunci klien).

    entries: list dict {seq, verdict, reasons, txn_tag24, token}
    Kembalikan (ok, pesan).
    """
    prev, exp_seq = start_prev, start_seq
    for e in entries:
        if e["seq"] != exp_seq:
            return False, f"celah/urutan seq: harap {exp_seq}, dapat {e['seq']}"
        m = struct.pack(">BBHI", DOM_TOKEN, e["verdict"], e["reasons"], e["seq"]) + e["txn_tag24"] + prev
        if not hmac.compare_digest(tag_of(tok_key, m), e["token"]):
            return False, f"rantai putus pada seq {e['seq']}"
        prev, exp_seq = e["token"], exp_seq + 1
    return True, f"rantai utuh ({len(entries)} entri)"


def words_be(b: bytes):
    return list(struct.unpack(f">{len(b)//4}I", b))
