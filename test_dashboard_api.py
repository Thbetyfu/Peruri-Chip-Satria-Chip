"""Tes otomatis dasbor demo SATRIA-CHIP (tanpa dependensi: python test_dashboard_api.py)."""
import json
import os
import sys
import threading
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_dashboard"))
import app  # noqa: E402


def fresh():
    e = app.DemoEngine()
    return e


def test_engine():
    e = fresh()
    r1 = e.scenario("normal")[0]
    r2 = e.scenario("normal")[0]
    assert (r1["verdict"], r1["cycles"]) == ("ACCEPT", 750), r1      # klien baru: derivasi kunci
    assert (r2["verdict"], r2["cycles"]) == ("ACCEPT", 411), r2      # cache hit

    burst = e.scenario("velocity")
    assert [r["verdict"] for r in burst] == ["ACCEPT"] * 5 + ["FLAG"], [r["verdict"] for r in burst]
    assert burst[-1]["reasons"] == "VELOCITY"

    esc = e.scenario("amount")[0]
    assert (esc["verdict"], esc["reasons"]) == ("ESCALATE", "AMOUNT"), esc

    forged = e.scenario("forge")[0]
    assert (forged["verdict"], forged["reasons"], forged["cycles"]) == ("REJECT", "INTEGRITY", 407), forged

    rep = e.scenario("replay")[-1]
    assert (rep["verdict"], rep["reasons"]) == ("REJECT", "REPLAY"), rep

    cx = e.scenario("crypto")[0]
    assert (cx["verdict"], cx["cycles"]) == ("ACCEPT", 750), cx      # klien lain: cache miss

    assert e.audit_action("verify")["status"] == "UTUH"
    assert e.audit_action("modify")["status"] == "TERDETEKSI"
    assert e.audit_action("delete")["status"] == "TERDETEKSI"
    assert e.audit_action("swap")["status"] == "TERDETEKSI"
    assert e.audit_action("verify")["status"] == "UTUH"             # log asli tidak ikut berubah

    xml = e.ltkm(esc["seq"])
    assert "DRAFT" in xml and esc["token"] in xml and "PENUNDAAN" in xml

    e.scenario("root_policy")
    after = e.scenario("normal")[0]
    assert (after["verdict"], after["reasons"]) == ("REJECT", "VAULT"), after
    assert e.state()["tamper"] is True


def test_gateway_key_matches_golden():
    import golden as G
    from aml_gateway_simulator import AMLGatewaySimulator, DEMO_MASTER_KEY
    gw = AMLGatewaySimulator()
    rec, tag = gw.parse_snap_bi_transfer({"partner_id": 1, "source_account": 1, "amount": 1, "nonce": 1,
                                          "timestamp": 1})
    assert tag == G.sign_txn(DEMO_MASTER_KEY, rec)


def test_http():
    app.ENGINE.reset()
    srv = app.make_server(0)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}"

    def post(path, body):
        req = urllib.request.Request(base + path, json.dumps(body).encode(), {"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req).read())

    html = urllib.request.urlopen(base + "/").read().decode()
    assert "SATRIA-CHIP" in html
    st = post("/api/simulate", {"type": "amount"})
    assert st["counts"]["ESCALATE"] == 1 and st["delayed_amount"] == "Rp250.000.000"
    seq = st["rows"][0]["seq"]
    xml = urllib.request.urlopen(f"{base}/api/ltkm/{seq}").read().decode()
    assert "hardware_attestation" in xml
    assert post("/api/reset", {})["total"] == 0
    srv.shutdown()


if __name__ == "__main__":
    test_engine()
    test_gateway_key_matches_golden()
    test_http()
    print("Semua tes dasbor LULUS (engine, kunci gateway = golden model, HTTP).")
