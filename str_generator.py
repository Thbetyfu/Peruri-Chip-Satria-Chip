"""
SATRIA-CHIP: Penyusun Draf LTKM (Laporan Transaksi Keuangan Mencurigakan / STR)

Menyusun DRAF laporan berformat XML bergaya goAML berdasarkan vonis, verdict token,
dan entri audit log dari chip. Draf ini WAJIB ditinjau petugas kepatuhan sebelum
dikirim melalui aplikasi goAML PPATK. Struktur XML di sini bersifat ilustratif
(prototipe), bukan skema resmi goAML.
"""

import time
import xml.etree.ElementTree as ET
from typing import Any, Dict
from xml.dom import minidom

VERDICT_ACTION = {
    "ACCEPT": "DIEKSEKUSI",
    "FLAG": "DIEKSEKUSI_DITANDAI_KANDIDAT_LTKM",
    "ESCALATE": "DIUSULKAN_PENUNDAAN_TRANSAKSI_UU8_2010_PS26",
    "REJECT": "DITOLAK_REKAMAN_TIDAK_SAH",
}

REASON_TEXT = {
    "VELOCITY": "Frekuensi transaksi rekening melampaui batas kebijakan dalam jendela waktu.",
    "AMOUNT": "Nominal transaksi melampaui ambang kebijakan.",
    "REPLAY": "Rekaman transaksi lama dikirim ulang (nonce/timestamp tidak baru).",
    "INTEGRITY": "Tag HMAC tidak cocok: rekaman diubah setelah ditandatangani sistem sumber.",
    "DOMAIN": "Domain rekaman tidak valid.",
}


class STRGenerator:
    def __init__(self, reporting_entity: str = "PJK DEMO (Prototipe SATRIA-CHIP)"):
        self.reporting_entity = reporting_entity

    def generate_goaml_xml(self, d: Dict[str, Any]) -> str:
        root = ET.Element("report")
        root.set("report_type", "STR")
        root.set("status", "DRAFT")

        ET.SubElement(root, "note").text = (
            "DRAF - wajib ditinjau petugas kepatuhan sebelum dikirim melalui aplikasi goAML PPATK. "
            "Struktur XML ilustratif (prototipe), bukan skema resmi goAML.")

        ent = ET.SubElement(root, "reporting_entity")
        ET.SubElement(ent, "name").text = self.reporting_entity
        ET.SubElement(ent, "draft_created_utc").text = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        tx = ET.SubElement(root, "transaction")
        ET.SubElement(tx, "transaction_number").text = str(d.get("txn_id", "-"))
        ET.SubElement(tx, "channel").text = str(d.get("channel", "-"))
        ET.SubElement(tx, "source_account").text = str(d.get("account", "-"))
        ET.SubElement(tx, "amount_idr").text = str(d.get("amount", 0))
        ET.SubElement(tx, "destination").text = str(d.get("dest", "-"))

        hw = ET.SubElement(root, "hardware_attestation")
        ET.SubElement(hw, "chip").text = "SATRIA-CHIP (Cyclone V 5CSEBA6, DE10-Nano)"
        ET.SubElement(hw, "verdict").text = str(d.get("verdict", "-"))
        ET.SubElement(hw, "reasons").text = str(d.get("reasons", "-"))
        ET.SubElement(hw, "system_action").text = VERDICT_ACTION.get(d.get("verdict"), "-")
        ET.SubElement(hw, "audit_seq").text = str(d.get("seq", "-"))
        ET.SubElement(hw, "verdict_token_hmac_sha256").text = str(d.get("token", "-"))
        ET.SubElement(hw, "latency_cycles_at_50mhz").text = str(d.get("cycles", "-"))
        ET.SubElement(hw, "verification").text = (
            "Token dapat diverifikasi dengan K_tok; rantai audit diverifikasi berurutan dari seq 0.")

        ind = ET.SubElement(root, "suspicion_indicators")
        for r in str(d.get("reasons", "")).split("|"):
            if r in REASON_TEXT:
                i = ET.SubElement(ind, "indicator")
                i.set("code", r)
                i.text = REASON_TEXT[r]

        return minidom.parseString(ET.tostring(root, encoding="utf-8")).toprettyxml(indent="  ")


if __name__ == "__main__":
    print(STRGenerator().generate_goaml_xml({
        "txn_id": "SEQ-0005", "channel": "SNAP BI", "account": 9876543210, "amount": 250_000_000,
        "dest": "CHASUS33XXX", "verdict": "ESCALATE", "reasons": "AMOUNT", "seq": 5,
        "token": "ab" * 32, "cycles": 411}))
