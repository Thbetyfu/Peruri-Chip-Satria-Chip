"""Testbench cocotb untuk screener_top, dibandingkan dengan golden model Python."""
import os
import random
import sys

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "model"))
import golden as G  # noqa: E402

KEY = bytes.fromhex("c0ffee00" * 2 + "5ec0de11" * 2 + "0badf00d" * 2 + "deadbeef" * 2)
POLICY = G.Policy(window_shift=6, vel_limit=5, amount_limit=10_000_000)

A_TXN, A_TAG, A_CTRL, A_STATUS, A_RESULT, A_SEQ, A_CYC = 0x00, 0x10, 0x18, 0x19, 0x1A, 0x1B, 0x1C
A_TOKEN, A_HEAD, A_LCOUNT, A_LIDX, A_LSEQ, A_LMETA, A_LTOK = 0x20, 0x28, 0x30, 0x31, 0x32, 0x33, 0x38
A_KEY, A_CFG_WIN, A_CFG_VEL, A_CFG_AHI, A_CFG_ALO, A_LOCK = 0x40, 0x48, 0x49, 0x4A, 0x4B, 0x4F
LOCK_MAGIC = 0x4C4F434B

RESULTS = []   # dikumpulkan untuk laporan


class Bus:
    def __init__(self, dut):
        self.dut = dut

    async def write(self, addr, data):
        d = self.dut
        await FallingEdge(d.clk)
        d.address.value = addr
        d.writedata.value = data & 0xFFFFFFFF
        d.write.value = 1
        await FallingEdge(d.clk)
        d.write.value = 0

    async def read(self, addr):
        d = self.dut
        await FallingEdge(d.clk)
        d.address.value = addr
        d.read.value = 1
        await FallingEdge(d.clk)
        d.read.value = 0
        return int(d.readdata.value)

    async def write_bytes(self, base, data: bytes):
        for i, w in enumerate(G.words_be(data)):
            await self.write(base + i, w)

    async def read_bytes(self, base, nwords):
        out = b""
        for i in range(nwords):
            out += (await self.read(base + i)).to_bytes(4, "big")
        return out


async def setup(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())   # 50 MHz
    dut.rst_n.value = 0
    dut.tamper_n.value = 1
    dut.address.value = 0
    dut.write.value = 0
    dut.writedata.value = 0
    dut.read.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    return Bus(dut)


async def provision(bus, key=KEY, policy=POLICY):
    await bus.write_bytes(A_KEY, key)
    await bus.write(A_CFG_WIN, policy.window_shift)
    await bus.write(A_CFG_VEL, policy.vel_limit)
    await bus.write(A_CFG_AHI, policy.amount_limit >> 32)
    await bus.write(A_CFG_ALO, policy.amount_limit & 0xFFFFFFFF)
    await bus.write(A_LOCK, LOCK_MAGIC)
    for _ in range(5000):
        st = await bus.read(A_STATUS)
        if st & 0x4 and st & 0x10:          # LOCKED dan sketch selesai disapu
            return st
    raise AssertionError("vault tidak pernah LOCKED")


async def submit(bus, rec: bytes, tag: bytes):
    await bus.write_bytes(A_TXN, rec)
    await bus.write_bytes(A_TAG, tag)
    await bus.write(A_CTRL, 1)
    for _ in range(5000):
        st = await bus.read(A_STATUS)
        if st & 0x2 and not st & 0x1:
            break
    else:
        raise AssertionError("transaksi tidak selesai")
    res = await bus.read(A_RESULT)
    seq = await bus.read(A_SEQ)
    cyc = await bus.read(A_CYC)
    tok = await bus.read_bytes(A_TOKEN, 8)
    return res & 0x3, (res >> 8) & 0xFFFF, seq, tok, cyc


async def check(bus, model, rec, tag, label, expect_verdict=None):
    v, r, s, tok, cyc = await submit(bus, rec, tag)
    ev, er, es, etok = model.process(rec, tag)
    assert (v, r, s) == (ev, er, es), f"{label}: RTL {(v, r, s)} != model {(ev, er, es)}"
    assert tok == etok, f"{label}: token RTL != model"
    if expect_verdict is not None:
        assert v == expect_verdict, f"{label}: verdict {G.VERDICT_NAME[v]} != {G.VERDICT_NAME[expect_verdict]}"
    bus.dut._log.info("%-40s -> %-8s reasons=%-18s seq=%d cycles=%d",
                      label, G.VERDICT_NAME[v], G.reasons_str(r), s, cyc)
    RESULTS.append((label, G.VERDICT_NAME[v], G.reasons_str(r), cyc))
    return v, r, s, tok, cyc


# ---------------------------------------------------------------------------
@cocotb.test()
async def t01_valid_transaction_hmac_matches_golden(dut):
    """Transaksi sah -> ACCEPT; token bit-exact dengan golden model; ukur cycle."""
    bus = await setup(dut)
    await provision(bus)
    m = G.Screener(KEY, POLICY)
    rec = G.make_record(account=0x1001, nonce=1, amount=10_000, tstamp=1_000, doc=b"surat-perjanjian.pdf")
    _, _, _, _, cyc0 = await check(bus, m, rec, G.sign_txn(KEY, rec),
                                   "transaksi sah (klien baru: turunkan kunci)", G.ACCEPT)
    rec = G.make_record(account=0x1001, nonce=2, amount=10_000, tstamp=1_001, doc=b"lampiran.pdf")
    _, _, _, _, cyc = await check(bus, m, rec, G.sign_txn(KEY, rec), "transaksi sah", G.ACCEPT)
    assert cyc < 500, f"latensi {cyc} cycle melebihi target"
    assert cyc0 < 850, f"latensi turunkan kunci {cyc0} cycle melebihi target"


@cocotb.test()
async def t02_bitflip_rejected_by_integrity_gate(dut):
    """Satu bit diubah (rekaman atau tag) -> REJECT INTEGRITY, tidak mencapai rule engine."""
    bus = await setup(dut)
    await provision(bus)
    m = G.Screener(KEY, POLICY)
    rec = G.make_record(account=0x2002, nonce=7, amount=50_000, tstamp=2_000)
    tag = G.sign_txn(KEY, rec)
    rnd = random.Random(1)
    for bit in [0, 255, 300, 511] + [rnd.randrange(8, 512) for _ in range(4)]:
        if bit < 8:
            continue   # bit domain diuji terpisah
        b = bytearray(rec)
        b[bit // 8] ^= 1 << (7 - bit % 8)
        await check(bus, m, bytes(b), tag, f"bit-flip rekaman bit {bit}", G.REJECT)
    t = bytearray(tag)
    t[31] ^= 1
    await check(bus, m, rec, bytes(t), "bit-flip pada tag", G.REJECT)
    # transaksi asli masih diterima: penolakan tidak mengubah state akun
    await check(bus, m, rec, tag, "transaksi asli setelah serangan", G.ACCEPT)


@cocotb.test()
async def t03_domain_separation(dut):
    """Verdict token yang sah tidak bisa dipakai ulang sebagai transaksi."""
    bus = await setup(dut)
    await provision(bus)
    m = G.Screener(KEY, POLICY)
    rec = G.make_record(account=0x3003, nonce=1, amount=1, tstamp=10)
    tag = G.sign_txn(KEY, rec)
    v, r, s, tok, _ = await check(bus, m, rec, tag, "transaksi sah", G.ACCEPT)
    forged = G.token_msg(v, r, s, tag, bytes(32))     # pesan yang MAC-nya = tok
    assert G.tag_of(G.token_key(KEY), forged) == tok
    await check(bus, m, forged, tok, "token disubmit sebagai transaksi", G.REJECT)


@cocotb.test()
async def t04_replay_rejected(dut):
    """Nonce = nomor urut per klien; replay & nonce yang sudah dipakai ditolak."""
    bus = await setup(dut)
    await provision(bus)
    m = G.Screener(KEY, POLICY)
    rec = G.make_record(account=0x4004, nonce=10, amount=1_000, tstamp=100)
    tag = G.sign_txn(KEY, rec)
    await check(bus, m, rec, tag, "transaksi nonce 10", G.ACCEPT)
    await check(bus, m, rec, tag, "replay transaksi yang sama", G.REJECT)
    late = G.make_record(account=0x4004, nonce=9, amount=1_000, tstamp=101)
    await check(bus, m, late, G.sign_txn(KEY, late), "nonce 9 terlambat, belum dipakai", G.ACCEPT)
    await check(bus, m, late, G.sign_txn(KEY, late), "replay nonce 9", G.REJECT)
    new = G.make_record(account=0x4004, nonce=11, amount=1_000, tstamp=102)
    await check(bus, m, new, G.sign_txn(KEY, new), "nonce baru (11)", G.ACCEPT)


@cocotb.test()
async def t05_velocity_and_amount(dut):
    bus = await setup(dut)
    await provision(bus)
    m = G.Screener(KEY, POLICY)
    for i in range(7):
        rec = G.make_record(account=0x5005, nonce=i + 1, amount=5_000, tstamp=500 + i)
        exp = G.ACCEPT if i < POLICY.vel_limit else G.FLAG
        await check(bus, m, rec, G.sign_txn(KEY, rec), f"lonjakan akun #{i+1} dlm 64 dtk", exp)
    rec = G.make_record(account=0x5005, nonce=100, amount=5_000, tstamp=500 + 140)
    await check(bus, m, rec, G.sign_txn(KEY, rec), "setelah jendela waktu lewat", G.ACCEPT)
    rec = G.make_record(account=0x6006, nonce=101, amount=25_000_000, tstamp=900)
    await check(bus, m, rec, G.sign_txn(KEY, rec), "nominal di atas batas", G.ESCALATE)


@cocotb.test()
async def t06_audit_log_hash_chain(dut):
    """Log on-chip membentuk rantai; ubah/hapus/tukar entri terdeteksi verifikator."""
    bus = await setup(dut)
    await provision(bus)
    m = G.Screener(KEY, POLICY)
    rnd = random.Random(7)
    tags = []
    for i in range(10):
        rec = G.make_record(account=0x7000 + (i % 3), nonce=i + 1,
                            amount=rnd.choice([100, 20_000_000]), tstamp=1000 + i)
        tag = G.sign_txn(KEY, rec)
        if i == 4:
            tag = bytes(32)   # satu transaksi palsu, ikut tercatat sebagai REJECT
        tags.append(tag)
        await check(bus, m, rec, tag, f"log #{i}")
    count = await bus.read(A_LCOUNT)
    assert count == 10
    entries = []
    for i in range(count):
        await bus.write(A_LIDX, i)
        await bus.read(A_LSEQ)   # beri 1 cycle untuk baca RAM
        seq = await bus.read(A_LSEQ)
        meta = await bus.read(A_LMETA)
        tok = await bus.read_bytes(A_LTOK, 8)
        entries.append({"seq": seq, "verdict": (meta >> 16) & 0xFF, "reasons": meta & 0xFFFF,
                        "txn_tag24": tags[i][:24], "token": tok})
    head = await bus.read_bytes(A_HEAD, 8)
    assert head == entries[-1]["token"] == m.head

    ok, msg = G.verify_chain(G.token_key(KEY), entries)
    dut._log.info("log asli           : %s", msg)
    assert ok
    RESULTS.append(("verifikasi log asli", "OK", msg, 0))

    e2 = [dict(e) for e in entries]
    e2[4]["verdict"] = G.ACCEPT; e2[4]["reasons"] = 0      # ubah REJECT jadi ACCEPT
    ok, msg = G.verify_chain(G.token_key(KEY), e2)
    dut._log.info("entri #4 diubah    : %s", msg)
    assert not ok
    RESULTS.append(("log: entri REJECT diubah jadi ACCEPT", "TERDETEKSI", msg, 0))

    e3 = entries[:6] + entries[7:]
    ok, msg = G.verify_chain(G.token_key(KEY), e3)
    dut._log.info("entri #6 dihapus   : %s", msg)
    assert not ok
    RESULTS.append(("log: entri #6 dihapus", "TERDETEKSI", msg, 0))

    e4 = [dict(e) for e in entries]
    e4[2], e4[3] = e4[3], e4[2]
    e4[2]["seq"], e4[3]["seq"] = 2, 3                       # samarkan seq juga
    ok, msg = G.verify_chain(G.token_key(KEY), e4)
    dut._log.info("entri ditukar      : %s", msg)
    assert not ok
    RESULTS.append(("log: urutan entri ditukar", "TERDETEKSI", msg, 0))


@cocotb.test()
async def t07_key_never_readable(dut):
    """Sapu seluruh 256 alamat: tidak ada word kunci/ipad/opad yang terbaca."""
    bus = await setup(dut)
    await provision(bus)
    vault = dut.u_vault
    m = G.Screener(KEY, POLICY)
    rec = G.make_record(account=0x9009, nonce=1, amount=1, tstamp=5, client=7)
    await check(bus, m, rec, G.sign_txn(KEY, rec), "isi cache kunci klien")
    secrets = set(G.words_be(KEY)) | set(G.words_be(G.token_key(KEY))) | set(G.words_be(G.client_key(KEY, 7)))
    for sig in (vault.ipad_state, vault.opad_state, vault.tok_ipad, vault.tok_opad, vault.idx_ipad,
                dut.c_ipad, dut.c_opad):
        v = int(sig.value)
        assert v != 0, "state turunan harus terisi untuk uji ini"
        secrets |= set(G.words_be(v.to_bytes(32, "big")))
    assert int(vault.key.value) == 0, "kunci mentah harus terhapus setelah LOCK"
    leaked = []
    for a in range(256):
        if 0x40 <= a <= 0x4F:
            continue   # tulis area ini = tamper; baca saja aman tapi dilewati
        val = await bus.read(a)
        if val in secrets and val != 0:
            leaked.append((a, val))
    for a in range(0x40, 0x48):
        assert await bus.read(a) == 0
    assert not leaked, f"kebocoran: {leaked}"
    RESULTS.append(("sapu 256 alamat bus: kunci master/token/klien/indeks & ipad/opad", "TIDAK BOCOR", "kunci mentah = 0 setelah LOCK", 0))


@cocotb.test()
async def t08_rewrite_key_triggers_zeroize(dut):
    """Host terkompromi mencoba mengganti kunci -> TAMPER, zeroize, fail-closed."""
    bus = await setup(dut)
    await provision(bus)
    m = G.Screener(KEY, POLICY)
    rec = G.make_record(account=0x8008, nonce=1, amount=1, tstamp=1)
    await check(bus, m, rec, G.sign_txn(KEY, rec), "sebelum serangan", G.ACCEPT)
    await bus.write(A_KEY, 0x41414141)                      # serangan
    st = await bus.read(A_STATUS)
    assert st & 0x8 and not st & 0x4, "harus TAMPER dan tidak LOCKED"
    for sig in (dut.u_vault.ipad_state, dut.u_vault.opad_state, dut.u_vault.tok_ipad,
                dut.u_vault.tok_opad, dut.u_vault.idx_ipad, dut.c_ipad, dut.c_opad):
        assert int(sig.value) == 0, "semua state kunci harus di-zeroize"
    attacker_key = bytes([0x41] * 4) + bytes(28)
    rec2 = G.make_record(account=0x8008, nonce=2, amount=1, tstamp=2)
    v, r, s, tok, _ = await submit(bus, rec2, G.tag_of(attacker_key, rec2))
    assert v == G.REJECT and r & G.R_VAULT and tok == bytes(32)
    v, r, s, tok, _ = await submit(bus, rec2, G.sign_txn(KEY, rec2))
    assert v == G.REJECT and r & G.R_VAULT and tok == bytes(32)
    RESULTS.append(("host menulis ulang kunci setelah LOCK", "TAMPER", "zeroize, semua REJECT, token=0", 0))


@cocotb.test()
async def t09_policy_locked_and_tamper_pin(dut):
    bus = await setup(dut)
    await provision(bus)
    assert await bus.read(A_CFG_VEL) == POLICY.vel_limit
    await bus.write(A_CFG_VEL, 0xFFFF)                      # coba longgarkan aturan
    st = await bus.read(A_STATUS)
    assert st & 0x8, "ubah kebijakan setelah LOCK harus memicu TAMPER"
    assert await bus.read(A_CFG_VEL) == POLICY.vel_limit, "kebijakan tidak boleh berubah"
    RESULTS.append(("host melonggarkan aturan setelah LOCK", "TAMPER", "kebijakan tetap", 0))
    # pin tamper fisik (reset dulu)
    bus = await setup(dut)
    await provision(bus)
    dut.tamper_n.value = 0
    await ClockCycles(dut.clk, 4)
    dut.tamper_n.value = 1
    st = await bus.read(A_STATUS)
    assert st & 0x8 and int(dut.u_vault.ipad_state.value) == 0
    RESULTS.append(("sinyal sensor tamper eksternal", "TAMPER", "zeroize", 0))


@cocotb.test()
async def t10_unprovisioned_fail_closed(dut):
    bus = await setup(dut)
    rec = G.make_record(account=1, nonce=1, amount=1, tstamp=1)
    v, r, _, tok, _ = await submit(bus, rec, G.sign_txn(KEY, rec))
    assert v == G.REJECT and r & G.R_VAULT and tok == bytes(32)
    RESULTS.append(("chip belum diprovisioning", "REJECT", "fail-closed", 0))


@cocotb.test()
async def t11_per_client_key_isolation(dut):
    """Kunci klien diturunkan di chip: kunci klien A tidak bisa dipakai atas nama klien B."""
    bus = await setup(dut)
    await provision(bus)
    m = G.Screener(KEY, POLICY)
    ka, kb = G.client_key(KEY, 0x0A), G.client_key(KEY, 0x0B)
    assert ka != kb
    ra = G.make_record(account=0xA001, nonce=1, amount=100, tstamp=50, client=0x0A)
    await check(bus, m, ra, G.tag_of(ka, ra), "klien A dengan kunci A", G.ACCEPT)
    rb = G.make_record(account=0xB001, nonce=1, amount=100, tstamp=51, client=0x0B)
    await check(bus, m, rb, G.tag_of(ka, rb), "klien B ditandatangani kunci A (bocor)", G.REJECT)
    await check(bus, m, rb, G.tag_of(kb, rb), "klien B dengan kunci B", G.ACCEPT)
    ra2 = bytearray(G.make_record(account=0xA001, nonce=2, amount=100, tstamp=52, client=0x0A))
    tag = G.tag_of(ka, bytes(ra2))
    ra2[2:4] = (0x0B).to_bytes(2, "big")                    # ganti id klien di rekaman
    await check(bus, m, bytes(ra2), tag, "id klien diganti host", G.REJECT)
    rm = G.make_record(account=0xA001, nonce=3, amount=100, tstamp=53, client=0x0A)
    await check(bus, m, rm, G.tag_of(KEY, rm), "tag dengan kunci master langsung", G.REJECT)
    RESULTS.append(("token log diverifikasi hanya dengan K_tok", "OK", "backend tidak memegang K_master/K_client", 0))


@cocotb.test()
async def t12_collision_cannot_evade_velocity(dut):
    """Serangan lama (2 rekening bergantian di slot yang sama) kini tetap FLAG."""
    bus = await setup(dut)
    await provision(bus)
    m = G.Screener(KEY, POLICY)
    A, B = 0x1000, 0x1040            # dulu berbagi slot 0 di tabel 64 slot
    n, flags, seen = 0, 0, {A: 0, B: 0}
    for i in range(10):
        for acct in (A, B):
            n += 1
            rec = G.make_record(account=acct, nonce=n, amount=9_000_000, tstamp=1000 + 2 * i)
            seen[acct] += 1
            exp = G.FLAG if seen[acct] > POLICY.vel_limit else None
            v, *_ = await check(bus, m, rec, G.sign_txn(KEY, rec), f"bergantian {acct:#x} #{seen[acct]}", exp)
            flags += v == G.FLAG
    assert flags >= 10, f"hanya {flags} FLAG"
    RESULTS.append(("2 rekening bergantian, 20 transaksi Rp9 juta / 20 dtk", "FLAG", f"{flags} dari 20 ditandai", 0))


@cocotb.test()
async def t13_many_accounts_never_undercount(dut):
    """300 rekening lain lalu-lalang; rekening target tetap FLAG mulai transaksi ke-6."""
    bus = await setup(dut)
    await provision(bus)
    m = G.Screener(KEY, POLICY)
    rnd = random.Random(13)
    others = [0x200000 + rnd.randrange(1 << 24) for _ in range(300)]
    target, n, hits = 0xDEAD01, 0, 0
    for i in range(320):
        n += 1
        acct = target if i % 40 == 0 else others[i % 300]
        rec = G.make_record(account=acct, nonce=n, amount=1_000, tstamp=3000 + i // 8)
        if acct == target:
            hits += 1
            exp = G.FLAG if hits > POLICY.vel_limit else None
            await check(bus, m, rec, G.sign_txn(KEY, rec), f"target #{hits} di tengah 300 rekening", exp)
        else:
            v, r, s, tok, _ = await submit(bus, rec, G.sign_txn(KEY, rec))
            assert (v, r, s, tok) == m.process(rec, G.sign_txn(KEY, rec))


@cocotb.test()
async def t14_replay_window_and_clock_skew(dut):
    """Jendela anti-replay 64 per klien; selisih jam sumber tidak lagi menolak transaksi sah."""
    bus = await setup(dut)
    await provision(bus)
    m = G.Screener(KEY, POLICY)
    cases = [(1, 0x2000, 10, 5000, "rek A ts=5000", G.ACCEPT),
             (1, 0x2040, 12, 5001, "rek B nonce 12", G.ACCEPT),
             (2, 0x2080, 1, 4999, "rek C BARU, klien lain, jam mundur 2 dtk", G.ACCEPT),
             (1, 0x2000, 11, 5002, "nonce 11 datang terlambat (masih di jendela)", G.ACCEPT),
             (1, 0x2000, 11, 5003, "nonce 11 diputar ulang", G.REJECT),
             (1, 0x2000, 100, 5004, "nonce melompat ke 100", G.ACCEPT),
             (1, 0x2000, 36, 5005, "nonce 36 (di luar jendela 64)", G.REJECT),
             (1, 0x2000, 37, 5006, "nonce 37 (tepi jendela, belum dipakai)", G.ACCEPT)]
    for cli, acct, nonce, ts, lbl, exp in cases:
        rec = G.make_record(account=acct, nonce=nonce, amount=100, tstamp=ts, client=cli)
        await check(bus, m, rec, G.sign_txn(KEY, rec), lbl, exp)


@cocotb.test()
async def t15_client_out_of_range_fail_closed(dut):
    """Id klien di luar 0..15 ditolak; tidak dapat merebut slot klien terdaftar."""
    bus = await setup(dut)
    await provision(bus)
    m = G.Screener(KEY, POLICY)
    r1 = G.make_record(account=0x3000, nonce=1, amount=100, tstamp=10, client=0x01)
    await check(bus, m, r1, G.sign_txn(KEY, r1), "klien 0x01 (slot 1)", G.ACCEPT)
    r2 = G.make_record(account=0x3001, nonce=1, amount=100, tstamp=11, client=0x11)
    v, r, *_ = await check(bus, m, r2, G.sign_txn(KEY, r2), "klien 0x11 (di luar 0..15)", G.REJECT)
    assert r & G.R_CLIENT
    r3 = G.make_record(account=0x3000, nonce=2, amount=100, tstamp=12, client=0x01)
    await check(bus, m, r3, G.sign_txn(KEY, r3), "klien 0x01 tetap berjalan", G.ACCEPT)


@cocotb.test()
async def t99_report(dut):
    """Tulis ringkasan hasil ke build/results.md."""
    out = os.path.join(os.path.dirname(__file__), "..", "build", "results.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write("| Skenario | Hasil | Keterangan | Cycle |\n|---|---|---|---|\n")
        for lbl, v, r, c in RESULTS:
            f.write(f"| {lbl} | {v} | {r} | {c or '-'} |\n")
    dut._log.info("laporan ditulis ke %s", out)
