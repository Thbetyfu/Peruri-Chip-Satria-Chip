"""
SATRIA-CHIP: Dasbor Demo Penegakan APU-PPT Berbasis Silikon

Setiap vonis di dasbor ini DIHITUNG oleh golden model (hardware-satria/model/golden.py),
model referensi yang bit-exact dengan RTL (diverifikasi cocotb pada 10.000 transaksi acak).
Latensi (cycle) mengikuti hasil simulasi RTL: 481/820 cycle untuk transaksi diproses,
407/746 cycle untuk penolakan integritas (cache kunci klien hit/miss).
Nonce = nomor urut per klien (institusi), seperti yang diterbitkan gateway sumber.

Tanpa dependensi eksternal - cukup Python 3.8+:
    python demo_dashboard/app.py            -> http://127.0.0.1:3001
    python demo_dashboard/app.py 8080       -> port lain

Untuk menjalankan skenario yang sama di board DE10-Nano: hardware-satria/host/demo_uart.py
"""

import copy
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
for _p in (_root, os.path.join(_root, "hardware-satria", "model"), os.path.join(_root, "..", "model")):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

import golden as G  # noqa: E402
from aml_gateway_simulator import DEMO_MASTER_KEY, AMLGatewaySimulator  # noqa: E402
from str_generator import STRGenerator  # noqa: E402

AMOUNT_LIMIT = 100_000_000      # ambang nominal demo (Rp); dapat dikonfigurasi sebelum LOCK
VEL_LIMIT, WIN_SHIFT = 5, 6    # >5 transaksi per rekening dalam 2^6 = 64 detik -> FLAG
WINDOW = 1 << WIN_SHIFT

ACTION = {
    "ACCEPT": "Dieksekusi core banking (token valid)",
    "FLAG": "Dieksekusi + ditandai kandidat LTKM",
    "ESCALATE": "Ditunda, menunggu tinjauan petugas (UU 8/2010 Ps. 26)",
    "REJECT": "Ditolak: rekaman tidak sah",
}


def rupiah(n: int) -> str:
    return "Rp" + f"{n:,}".replace(",", ".")


class DemoEngine:
    def __init__(self):
        self.reset()

    def reset(self):
        self.gw = AMLGatewaySimulator(DEMO_MASTER_KEY)
        self.chip = G.Screener(key=DEMO_MASTER_KEY,
                               policy=G.Policy(window_shift=WIN_SHIFT, vel_limit=VEL_LIMIT, amount_limit=AMOUNT_LIMIT))
        self.ts = 1_791_300_000
        self.nonces = {}
        self.cached_client = None
        self.tamper = False
        self.rows = []
        self.last_ok = None
        self.audit = {"status": "-", "detail": "Belum diverifikasi."}

    # ------------------------------------------------------------ util
    def _nonce(self, client):
        """Nomor urut per klien (partner SNAP BI / bursa kripto)."""
        self.nonces[client] = self.nonces.get(client, 0) + 1
        return self.nonces[client]

    def _tick(self, s):
        self.ts += s
        return self.ts

    def _snap(self, acct, amount, dest="BMRIIDJA:1234567890", dt=7):
        return self.gw.parse_snap_bi_transfer({"partner_id": 1, "source_account": acct, "amount": amount,
                                               "nonce": self._nonce(1), "timestamp": self._tick(dt),
                                               "beneficiary_bank": dest.split(":")[0],
                                               "beneficiary_account": dest.split(":")[-1]})

    def _submit(self, rec, tag, meta):
        client = G.client_of(rec)
        if self.tamper:
            row = dict(meta, verdict="REJECT", reasons="VAULT", seq=None, token="0" * 64, cycles="-",
                       action="Chip fail-closed (TAMPER/zeroize)")
        else:
            v, r, seq, tok = self.chip.process(rec, tag)
            miss = client != self.cached_client
            self.cached_client = client
            if r & (G.R_INTEGRITY | G.R_DOMAIN):
                cycles = 746 if miss else 407          # ditolak sebelum indeks sketch
            else:
                cycles = 820 if miss else 481
            name = G.VERDICT_NAME[v]
            action = ACTION[name]
            if name == "REJECT" and r & G.R_REPLAY:
                action = "Ditolak: replay rekaman lama"
            elif name == "REJECT" and r & G.R_CLIENT:
                action = "Ditolak: id klien tidak terdaftar (di luar 0..15)"
            elif name == "REJECT" and r & G.R_INTEGRITY:
                action = "Ditolak: rekaman diubah setelah ditandatangani"
            row = dict(meta, verdict=name, reasons=G.reasons_str(r), seq=seq, token=tok.hex(), cycles=cycles,
                       action=action)
            if name == "ACCEPT":
                self.last_ok = (rec, tag, meta)
        row["time"] = time.strftime("%H:%M:%S")
        row["us"] = "-" if row["cycles"] == "-" else f"{row['cycles'] / 50:.2f}".replace(".", ",")
        self.rows.insert(0, row)
        return row

    # ------------------------------------------------------------ skenario
    def scenario(self, kind):
        out = []
        if kind == "normal":
            acct = 1009882100 + len(self.rows)
            rec, tag = self._snap(acct, 25_000_000)
            out.append(self._submit(rec, tag, {"channel": "SNAP BI", "account": acct, "amount": 25_000_000,
                                               "dest": "Bank Mandiri", "label": "Transfer sah"}))
        elif kind == "crypto":
            acct = 77219 + len(self.rows)
            amt = 15_000_000
            rec, tag = self.gw.parse_crypto_deposit({"exchange_id": 2, "kyc_user_id": acct, "amount_idr": amt,
                                                     "nonce": self._nonce(2), "timestamp": self._tick(7),
                                                     "destination_wallet": "hot-wallet-bursa"})
            out.append(self._submit(rec, tag, {"channel": "Bursa kripto", "account": acct, "amount": amt,
                                               "dest": "Hot wallet bursa", "label": "Deposit kripto sah"}))
        elif kind == "velocity":
            acct = 9876543210
            for i in range(6):
                rec, tag = self._snap(acct, 9_500_000, "OCBCSGSG:555", dt=5)
                out.append(self._submit(rec, tag, {"channel": "SNAP BI", "account": acct, "amount": 9_500_000,
                                                   "dest": "Rekening luar negeri", "label": f"Lonjakan #{i + 1}"}))
        elif kind == "amount":
            acct = 5551234567
            rec, tag = self._snap(acct, 250_000_000, "CHASUS33:8821")
            out.append(self._submit(rec, tag, {"channel": "SNAP BI", "account": acct, "amount": 250_000_000,
                                               "dest": "Rekening luar negeri", "label": "Nominal besar"}))
        elif kind == "forge":
            acct = 4440001111
            rec, tag = self._snap(acct, 480_000_000, "CHASUS33:8821")
            forged = bytearray(rec)
            forged[24:32] = (48_000_000).to_bytes(8, "big")   # host mengecilkan nominal agar lolos ambang
            out.append(self._submit(bytes(forged), tag, {"channel": "SNAP BI", "account": acct, "amount": 48_000_000,
                                                         "dest": "Rekening luar negeri",
                                                         "label": "Host ubah nominal Rp480 jt -> Rp48 jt"}))
        elif kind == "replay":
            if self.last_ok is None:
                out.extend(self.scenario("normal"))
            rec, tag, meta = self.last_ok
            out.append(self._submit(rec, tag, dict(meta, label="Kirim ulang rekaman lama")))
        elif kind == "root_policy":
            self.tamper = True
            self.audit = {"status": "TAMPER",
                          "detail": "Host menulis register kebijakan setelah LOCK: chip TAMPER, kunci di-zeroize, "
                                    "semua transaksi berikutnya ditolak (fail-closed)."}
        return out

    # ------------------------------------------------------------ audit
    def audit_action(self, kind):
        log = self.chip.log
        ktok = G.token_key(DEMO_MASTER_KEY)
        if kind == "verify":
            ok, msg = G.verify_chain(ktok, log)
            self.audit = {"status": "UTUH" if ok else "RUSAK", "detail": f"Verifikasi log asli: {msg}."}
            return self.audit
        if len(log) < 3:
            self.audit = {"status": "-", "detail": "Jalankan minimal 3 transaksi dahulu."}
            return self.audit
        fake = copy.deepcopy(log)
        if kind == "modify":
            idx = next((i for i, e in enumerate(fake) if e["verdict"] != G.ACCEPT), 1)
            old = G.VERDICT_NAME[fake[idx]["verdict"]]
            fake[idx]["verdict"], fake[idx]["reasons"] = G.ACCEPT, 0
            what = f"Host mengubah entri seq {fake[idx]['seq']} dari {old} menjadi ACCEPT"
        elif kind == "delete":
            idx = len(fake) // 2
            what = f"Host menghapus entri seq {fake[idx]['seq']}"
            del fake[idx]
        else:
            fake[1], fake[2] = fake[2], fake[1]
            what = "Host menukar urutan entri seq 1 dan 2"
        ok, msg = G.verify_chain(ktok, fake)
        self.audit = {"status": "TIDAK TERDETEKSI" if ok else "TERDETEKSI", "detail": f"{what}: {msg}."}
        return self.audit

    # ------------------------------------------------------------ state
    def state(self):
        cnt = {k: sum(1 for r in self.rows if r["verdict"] == k) for k in ("ACCEPT", "FLAG", "ESCALATE", "REJECT")}
        delayed = sum(r["amount"] for r in self.rows if r["verdict"] == "ESCALATE")
        return {
            "status": "TAMPER (zeroized, fail-closed)" if self.tamper else "LOCKED (kebijakan terkunci)",
            "tamper": self.tamper,
            "total": len(self.rows), "counts": cnt,
            "delayed_amount": rupiah(delayed),
            "log_len": len(self.chip.log),
            "chain_head": self.chip.head.hex()[:24],
            "audit": self.audit,
            "policy": f"Ambang {rupiah(AMOUNT_LIMIT)} | velocity >{VEL_LIMIT} tx / {WINDOW} dtk per rekening",
            "rows": [dict(r, amount_str=rupiah(r["amount"]), token_short=r["token"][:16]) for r in self.rows[:60]],
        }

    def ltkm(self, seq):
        row = next((r for r in self.rows if r["seq"] == seq), None)
        if row is None:
            return None
        return STRGenerator().generate_goaml_xml({
            "txn_id": f"SEQ-{seq:04d}", "channel": row["channel"], "account": row["account"],
            "amount": row["amount"], "dest": row["dest"], "verdict": row["verdict"], "reasons": row["reasons"],
            "seq": seq, "token": row["token"], "cycles": row["cycles"]})


ENGINE = DemoEngine()

PAGE = r"""<!DOCTYPE html>
<html lang="id"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SATRIA-CHIP: Dasbor Demo</title>
<style>
:root{--bg:#070D1F;--card:rgba(16,26,54,.8);--line:rgba(99,133,196,.2);--txt:#F1F5F9;--mut:#94A3B8;
--cyan:#38BDF8;--green:#10B981;--amber:#F59E0B;--orange:#FB923C;--red:#EF4444}
*{box-sizing:border-box;margin:0;padding:0;font-family:Inter,Segoe UI,system-ui,sans-serif}
body{background:var(--bg);color:var(--txt);padding:22px;min-height:100vh}
.hd{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:18px}
h1{font-size:21px;font-weight:800}.sub{font-size:12.5px;color:var(--mut);margin-top:4px}
.badges{display:flex;gap:8px;flex-wrap:wrap}
.badge{padding:6px 12px;border-radius:20px;font-size:11.5px;font-weight:600;border:1px solid}
.b-ok{color:var(--green);border-color:var(--green);background:rgba(16,185,129,.12)}
.b-bad{color:var(--red);border-color:var(--red);background:rgba(239,68,68,.15)}
.b-mode{color:var(--cyan);border-color:var(--cyan);background:rgba(56,189,248,.1)}
.stats{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:18px}
.st{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}
.st h3{font-size:10.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.4px;font-weight:600}
.st .v{font-size:22px;font-weight:700;margin-top:6px}.st .s{font-size:10.5px;color:var(--mut);margin-top:3px}
.grid{display:grid;grid-template-columns:1fr 360px;gap:18px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.panel h2{font-size:14.5px;font-weight:700;margin-bottom:12px;display:flex;justify-content:space-between;gap:8px}
.panel h2 small{font-weight:400;color:var(--mut);font-size:11.5px}
.btns{display:flex;flex-direction:column;gap:8px}
button{border:1px solid #334155;background:#1E293B;color:var(--txt);padding:10px 12px;border-radius:8px;font-size:12.5px;font-weight:600;cursor:pointer;text-align:left}
button:hover{filter:brightness(1.25)}
.k-ok{border-color:#059669}.k-warn{border-color:var(--amber);color:#FCD34D;background:rgba(245,158,11,.12)}
.k-esc{border-color:var(--orange);color:#FDBA74;background:rgba(251,146,60,.12)}
.k-bad{border-color:var(--red);color:#FCA5A5;background:rgba(239,68,68,.14)}
.k-ghost{background:transparent;color:var(--mut);text-align:center}
.sec{font-size:10.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.4px;margin:14px 0 6px;font-weight:700}
.sec:first-of-type{margin-top:0}
table{width:100%;border-collapse:collapse;font-size:11.5px}
th{text-align:left;padding:8px 6px;border-bottom:1px solid var(--line);color:var(--mut);font-weight:600;font-size:10.5px;text-transform:uppercase}
td{padding:8px 6px;border-bottom:1px solid rgba(140,165,210,.08);vertical-align:middle}
.tag{padding:3px 8px;border-radius:10px;font-weight:700;font-size:10.5px;display:inline-block;border:1px solid}
.ACCEPT{color:#34D399;border-color:#059669;background:rgba(16,185,129,.12)}
.FLAG{color:#FCD34D;border-color:#D97706;background:rgba(245,158,11,.12)}
.ESCALATE{color:#FDBA74;border-color:#EA580C;background:rgba(251,146,60,.14)}
.REJECT{color:#FCA5A5;border-color:#DC2626;background:rgba(239,68,68,.14)}
.mono{font-family:Consolas,ui-monospace,monospace;font-size:10.5px;color:var(--mut)}
a.dl{color:var(--cyan);font-weight:600;text-decoration:none;border:1px solid var(--cyan);padding:2px 7px;border-radius:6px;font-size:10.5px}
.audit{margin-top:10px;padding:10px;border-radius:8px;background:rgba(0,0,0,.25);border:1px solid var(--line);font-size:11.5px;line-height:1.5}
.audit b.ok{color:var(--green)}.audit b.bad{color:var(--red)}
.ctx{font-size:11px;color:var(--mut);line-height:1.6}.ctx b{color:var(--txt)}
.empty{color:var(--mut);text-align:center;padding:28px}
@media(max-width:1100px){.stats{grid-template-columns:repeat(3,1fr)}.grid{grid-template-columns:1fr}}
</style></head><body>
<div class="hd"><div><h1>SATRIA-CHIP: Penegakan APU-PPT Berbasis Silikon</h1>
<div class="sub">Setiap vonis dihitung golden model yang bit-exact dengan RTL Cyclone V &middot; <span id="pol"></span></div></div>
<div class="badges"><span class="badge b-mode">Mode: golden model (bit-exact RTL)</span><span class="badge b-ok" id="hw">LOCKED</span></div></div>

<div class="stats">
<div class="st"><h3>Transaksi diproses</h3><div class="v" id="sTotal">0</div><div class="s">481 / 820 cycle @ 50 MHz</div></div>
<div class="st"><h3>ACCEPT</h3><div class="v" style="color:#34D399" id="sA">0</div><div class="s">dieksekusi</div></div>
<div class="st"><h3>FLAG</h3><div class="v" style="color:#FCD34D" id="sF">0</div><div class="s">kandidat LTKM</div></div>
<div class="st"><h3>ESCALATE</h3><div class="v" style="color:#FDBA74" id="sE">0</div><div class="s">ditunda untuk ditinjau</div></div>
<div class="st"><h3>REJECT</h3><div class="v" style="color:#FCA5A5" id="sR">0</div><div class="s">rekaman palsu / replay</div></div>
<div class="st"><h3>Nominal ditunda</h3><div class="v" id="sD" style="font-size:18px">Rp0</div><div class="s">menunggu keputusan petugas</div></div>
</div>

<div class="grid">
<div class="panel"><h2><span>Umpan transaksi &amp; vonis chip</span><small>terbaru di atas</small></h2>
<table><thead><tr><th>Waktu</th><th>Seq</th><th>Skenario</th><th>Kanal</th><th>Rekening</th><th>Nominal</th><th>Vonis</th><th>Latensi</th><th>Tindak lanjut</th><th>Token</th><th>Draf LTKM</th></tr></thead>
<tbody id="tb"></tbody></table></div>

<div class="panel">
<div class="sec">Transaksi dari gateway</div>
<div class="btns">
<button class="k-ok" onclick="sim('normal')">&#10003; Transfer sah (SNAP BI)</button>
<button class="k-ok" onclick="sim('crypto')">&#10003; Deposit bursa kripto sah (klien lain)</button>
<button class="k-warn" onclick="sim('velocity')">&#9888; Lonjakan: 6 transfer 1 rekening dalam 30 dtk</button>
<button class="k-esc" onclick="sim('amount')">&#9208; Nominal Rp250 juta di atas ambang</button>
</div>
<div class="sec">Serangan dari host yang dikompromi</div>
<div class="btns">
<button class="k-bad" onclick="sim('forge')">&#10007; Host mengecilkan nominal setelah ditandatangani</button>
<button class="k-bad" onclick="sim('replay')">&#10007; Host mengirim ulang rekaman lama (replay)</button>
<button class="k-bad" onclick="sim('root_policy')">&#9889; Root melonggarkan ambang setelah LOCK</button>
</div>
<div class="sec">Audit log hash-chain on-chip</div>
<div class="btns">
<button onclick="aud('verify')">Verifikasi rantai audit (K_tok)</button>
<button class="k-bad" onclick="aud('modify')">Host ubah entri non-ACCEPT jadi ACCEPT</button>
<button class="k-bad" onclick="aud('delete')">Host hapus satu entri log</button>
<button class="k-bad" onclick="aud('swap')">Host tukar urutan entri</button>
</div>
<div class="audit" id="au">-</div>
<div class="sec">Konteks</div>
<div class="ctx">PPATK 2025: <b>183.281 LTKM</b>, 47,49% terkait judi online; laporan penundaan transaksi <b>naik 484,8%</b>. BSSN: <b>5,2 miliar</b> anomali trafik (Jan&ndash;Nov 2025), sektor keuangan paling rentan. Chip memastikan aturan penundaan tidak bisa dimatikan dari host.</div>
<div class="btns" style="margin-top:12px"><button class="k-ghost" onclick="post('/api/reset',{})">Reset demo</button></div>
</div></div>

<script>
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function render(d){
 document.getElementById('pol').textContent=d.policy;
 const hw=document.getElementById('hw');hw.textContent=d.status;hw.className='badge '+(d.tamper?'b-bad':'b-ok');
 sTotal.textContent=d.total;sA.textContent=d.counts.ACCEPT;sF.textContent=d.counts.FLAG;sE.textContent=d.counts.ESCALATE;sR.textContent=d.counts.REJECT;sD.textContent=d.delayed_amount;
 const a=d.audit;const cls=(a.status==='UTUH'||a.status==='TERDETEKSI')?'ok':(a.status==='-'?'':'bad');
 au.innerHTML=`<b class="${cls}">${esc(a.status)}</b> &middot; ${esc(a.detail)}<br><span class="mono">entri log: ${d.log_len} &middot; head: ${d.chain_head}&hellip;</span>`;
 tb.innerHTML=d.rows.length?d.rows.map(r=>`<tr><td>${r.time}</td><td>${r.seq===null?'-':r.seq}</td><td>${esc(r.label)}</td><td>${esc(r.channel)}</td><td class="mono">${r.account}</td><td>${r.amount_str}</td>
 <td><span class="tag ${r.verdict}">${r.verdict}</span><div class="mono">${esc(r.reasons)}</div></td><td>${r.cycles==='-'?'-':r.cycles+' cyc<div class="mono">'+r.us+' &micro;s</div>'}</td>
 <td>${esc(r.action)}</td><td class="mono">${r.token_short}&hellip;</td>
 <td>${(r.verdict!=='ACCEPT'&&r.seq!==null)?`<a class="dl" href="/api/ltkm/${r.seq}">XML</a>`:'-'}</td></tr>`).join(''):'<tr><td colspan="11" class="empty">Belum ada transaksi. Pilih skenario di panel kanan.</td></tr>';
}
async function post(u,b){const r=await fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});render(await r.json());}
const sim=t=>post('/api/simulate',{type:t});const aud=t=>post('/api/audit',{action:t});
fetch('/api/state').then(r=>r.json()).then(render);
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json", extra=None):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj))

    def do_GET(self):
        if self.path == "/":
            return self._send(200, PAGE, "text/html")
        if self.path == "/api/state":
            return self._json(ENGINE.state())
        if self.path.startswith("/api/ltkm/"):
            try:
                seq = int(self.path.rsplit("/", 1)[1])
            except ValueError:
                return self._json({"error": "seq tidak valid"}, 400)
            xml = ENGINE.ltkm(seq)
            if xml is None:
                return self._json({"error": "seq tidak ditemukan"}, 404)
            return self._send(200, xml, "application/xml",
                              {"Content-Disposition": f"attachment; filename=Draf_LTKM_SEQ-{seq:04d}.xml"})
        self._json({"error": "tidak ditemukan"}, 404)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            body = {}
        if self.path == "/api/simulate":
            ENGINE.scenario(body.get("type"))
        elif self.path == "/api/audit":
            ENGINE.audit_action(body.get("action", "verify"))
        elif self.path == "/api/reset":
            ENGINE.reset()
        else:
            return self._json({"error": "tidak ditemukan"}, 404)
        self._json(ENGINE.state())

    def log_message(self, *a):
        pass


def make_server(port=3001):
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3001
    print(f"SATRIA-CHIP dasbor demo: http://127.0.0.1:{port}  (Ctrl+C untuk berhenti)")
    make_server(port).serve_forever()
