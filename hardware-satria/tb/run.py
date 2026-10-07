"""Jalankan testbench: python tb/run.py [all|core|uart|random|wave]  (butuh icarus-verilog + cocotb>=2).
HDL=sv untuk menguji versi SystemVerilog (rtl_sv/).
random: RANDOM_N=10000 (default) transaksi acak vs golden model."""
import os
import sys
from pathlib import Path

from cocotb_tools.runner import get_runner

ROOT = Path(__file__).resolve().parent.parent
HDL = os.getenv("HDL", "v")          # HDL=sv -> uji rtl_sv/*.sv (SystemVerilog)
RTL = sorted((ROOT / "rtl_sv").glob("*.sv")) if HDL == "sv" else sorted((ROOT / "rtl").glob("*.v"))


def run(top, module, extra=None):
    sim = os.getenv("SIM", "icarus")
    r = get_runner(sim)
    extra = dict(extra or {})
    srcs = extra.pop("sources", RTL)
    r.build(sources=srcs, hdl_toplevel=top, build_dir=ROOT / "build" / (top + ("_sv" if HDL == "sv" else "")),
            always=True, timescale=("1ns", "1ps"), **extra)
    r.test(hdl_toplevel=top, test_module=module, test_dir=ROOT / "tb",
           build_dir=ROOT / "build" / (top + ("_sv" if HDL == "sv" else "")), waves=bool(os.getenv("WAVES")))


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "core"):
        run("screener_top", "test_screener")
    if which in ("random",):
        run("screener_top", "test_random")
    if which == "wave":
        run("screener_top", "test_wave")
    if which in ("all", "uart"):
        run("tb_de10", "test_uart", {"sources": RTL + [ROOT / "tb" / "tb_de10.v"]})
