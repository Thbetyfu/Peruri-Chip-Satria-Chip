"""Regresi acak: N transaksi campuran, setiap verdict/token dibandingkan bit-exact
dengan golden model. Jumlah transaksi diatur lewat env RANDOM_N (default 10000)."""
import os
import random
import sys
import time

import cocotb

sys.path.insert(0, os.path.dirname(__file__))
import test_screener as T  # noqa: E402
G = T.G

N = int(os.getenv("RANDOM_N", "10000"))
SEED = int(os.getenv("RANDOM_SEED", "20261007"))


@cocotb.test()
async def random_regression(dut):
    bus = await T.setup(dut)
    # batas velocity diturunkan ke 2 agar jalur FLAG sketch sering teruji
    policy = G.Policy(window_shift=6, vel_limit=2, amount_limit=T.POLICY.amount_limit)
    await T.provision(bus, policy=policy)
    m = G.Screener(T.KEY, policy)
    rnd = random.Random(SEED)

    clients = [1, 2, 3, 7, 0x0A]
    accounts = [0x10000 + rnd.randrange(1 << 24) for _ in range(2000)]
    hot = accounts[:8]               # rekening "lonjakan" agar velocity sering terpicu
    nonce = {c: 0 for c in clients}
    history = []                     # (rec, tag) transaksi sah yang pernah dikirim
    now = 1_000
    stats = {}
    t0 = time.time()

    for i in range(N):
        now += rnd.choice([0, 0, 1, 1, 2, 5, 30])
        kind = rnd.choices(
            ["sah", "bitflip", "tag_salah", "kunci_klien_lain", "replay", "nominal_besar", "jam_mundur",
             "nonce_terlambat", "klien_bentrok"],
            weights=[50, 8, 5, 5, 12, 8, 6, 4, 2])[0]
        acct = rnd.choice(hot) if rnd.random() < 0.3 else rnd.choice(accounts)
        cli = rnd.choice(clients)
        if kind == "replay" and history:
            rec, tag = rnd.choice(history)
        else:
            if kind == "klien_bentrok":
                cli = cli + 0x10             # id di luar 0..15 (harus ditolak)
                nn = 1
            elif kind == "nonce_terlambat" and nonce[cli] > 3:
                nn = nonce[cli] - rnd.randrange(1, 80)   # di dalam / di luar jendela 64
            else:
                nonce[cli] += rnd.choice([1, 1, 1, 2, 7])
                nn = nonce[cli]
            ts = now if kind != "jam_mundur" else max(1, now - rnd.randrange(1, 400))
            amt = rnd.choice([100, 5_000, 250_000, 9_999_999]) if kind != "nominal_besar" else 10_000_001 + rnd.randrange(10**9)
            rec = G.make_record(acct, max(1, nn), amt, ts, doc=i.to_bytes(4, "big"), client=cli)
            tag = G.sign_txn(T.KEY, rec)
            if kind == "bitflip":
                b = bytearray(rec); bit = rnd.randrange(8, 512); b[bit // 8] ^= 1 << (7 - bit % 8); rec = bytes(b)
            elif kind == "tag_salah":
                t = bytearray(tag); t[rnd.randrange(32)] ^= 1 << rnd.randrange(8); tag = bytes(t)
            elif kind == "kunci_klien_lain":
                tag = G.tag_of(G.client_key(T.KEY, rnd.choice([c for c in clients if c != cli])), rec)
            else:
                history.append((rec, tag))
                if len(history) > 400:
                    history.pop(0)

        v, r, s, tok, cyc = await T.submit(bus, rec, tag)
        ev, er, es, etok = m.process(rec, tag)
        assert (v, r, s, tok) == (ev, er, es, etok), \
            f"transaksi #{i} ({kind}): RTL {(v, r, s)} != model {(ev, er, es)}"
        key = (kind, G.VERDICT_NAME[v])
        stats[key] = stats.get(key, 0) + 1
        if (i + 1) % 1000 == 0:
            dut._log.info("%5d/%d transaksi cocok bit-exact (%.0f s)", i + 1, N, time.time() - t0)

    head = await bus.read_bytes(T.A_HEAD, 8)
    assert head == m.head, "kepala rantai log RTL != model"
    count = await bus.read(T.A_LCOUNT)
    assert count == N

    lines = ["| Jenis transaksi | Verdict | Jumlah |", "|---|---|---|"]
    for (k, v), n in sorted(stats.items()):
        lines.append(f"| {k} | {v} | {n} |")
    lines.append(f"| **total** | **semua bit-exact dengan golden model** | **{N}** |")
    out = os.path.join(os.path.dirname(__file__), "..", "build", "random_results.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(f"Seed {SEED}, {N} transaksi, batas velocity 2/64 dtk, {len(accounts)} akun (8 akun lonjakan), sketch 4x4096, {len(clients)} klien.\n\n")
        f.write("\n".join(lines) + "\n")
    dut._log.info("RINGKASAN\n%s", "\n".join(lines))
