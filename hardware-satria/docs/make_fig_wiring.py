"""Diagram wiring demo SATRIA-CHIP di Terasic DE10-Nano (gaya skema teknik).

Sumber pin: quartus/screener.qsf dan rtl/de10_nano_top.v.
Output: docs/fig/wiring_de10nano.png  (2400 x 1410 px)
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

INK, MUTED, LINE, NAVY = "#111827", "#6B7280", "#D1D5DB", "#1B365D"
C_TX, C_RX, C_GND, C_USB, C_PWR = "#D97706", "#059669", "#111827", "#2563EB", "#DC2626"
BOARD, BOARD_EDGE = "#0F3D2E", "#0B2A20"
MONO, SANS = "DejaVu Sans Mono", "DejaVu Sans"

W, H = 24.0, 14.1
fig = plt.figure(figsize=(W / 2, H / 2), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")


def t(x, y, s, size=8, color=INK, weight="normal", ha="center", va="center", family=SANS, z=8):
    ax.text(x, y, s, fontsize=size, color=color, weight=weight, ha=ha, va=va, family=family, zorder=z,
            linespacing=1.35)


def rbox(x, y, w, h, fc, ec, lw=1.4, r=0.18, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw,
                                zorder=z))


def wire(pts, color, lw=2.3, z=5, dots=True):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", solid_joinstyle="round", zorder=z)
    if dots:
        for (x, y) in (pts[0], pts[-1]):
            ax.add_patch(Circle((x, y), 0.075, color=color, zorder=z + 1))


def port(x, y, w, h, label, size=6.5):
    rbox(x, y, w, h, "#F3F4F6", "#6B7280", lw=1.0, r=0.06, z=6)
    t(x + w / 2, y + h / 2, label, size, INK, z=9)


# ---------------------------------------------------------------- judul
t(0.6, H - 0.55, "Gambar Wiring Demo On-Board — SATRIA-CHIP pada Terasic DE10-Nano", 12.5, NAVY, "bold", ha="left")
t(0.6, H - 1.03, "Host PC → adaptor USB-UART 3,3 V → header JP1 (GPIO_0) FPGA Cyclone V 5CSEBA6U23I7  ·  "
  "pemrograman bitstream lewat USB-Blaster II on-board", 8.2, MUTED, ha="left")
ax.plot([0.6, W - 0.6], [H - 1.38, H - 1.38], color=LINE, lw=1)

# ---------------------------------------------------------------- host PC
hx, hy, hw, hh = 0.6, 7.6, 4.3, 4.2
rbox(hx, hy, hw, hh, "#F9FAFB", "#9CA3AF")
t(hx + hw / 2, hy + hh - 0.45, "HOST PC / LAPTOP", 9, INK, "bold")
t(hx + hw / 2, hy + hh - 1.1, "Quartus Programmer\nhost/demo_uart.py · dasbor demo", 6.8, MUTED)
port(hx + hw - 1.4, hy + 1.75, 1.4, 0.5, "USB-A #1")
port(hx + hw - 1.4, hy + 0.6, 1.4, 0.5, "USB-A #2")
t(hx + 0.25, hy + 2.0, "JTAG", 6.6, C_USB, "bold", ha="left")
t(hx + 0.25, hy + 0.85, "serial COMx", 6.6, C_USB, "bold", ha="left")

# ---------------------------------------------------------------- adaptor USB-UART
ax0, ay0, aw, ah = 6.4, 5.4, 3.8, 3.3
rbox(ax0, ay0, aw, ah, "#FFF7ED", "#C2410C")
t(ax0 + aw / 2, ay0 + ah - 0.42, "ADAPTOR USB-UART", 8.6, "#9A3412", "bold")
t(ax0 + aw / 2, ay0 + ah - 0.85, "CP2102 / CH340 / FT232", 6.6, MUTED)
t(ax0 + aw / 2, ay0 + ah - 1.25, "jumper VCCIO = 3,3 V", 6.6, "#C2410C", "bold")
port(ax0 - 0.05, ay0 + 0.95, 0.8, 0.45, "USB")
apin = {"GND": ay0 + 1.75, "RXD": ay0 + 1.2, "TXD": ay0 + 0.65}
for name, yy in apin.items():
    port(ax0 + aw - 0.85, yy - 0.2, 0.85, 0.4, name)
t(ax0 + 0.95, ay0 + 0.35, "pin VCC: tidak disambung", 5.9, C_PWR, ha="left")

# ---------------------------------------------------------------- papan DE10-Nano
bx, by, bw, bh = 11.6, 2.4, 11.8, 9.6
rbox(bx, by, bw, bh, BOARD, BOARD_EDGE, lw=2, r=0.3)
t(bx + 0.4, by + bh - 0.45, "TERASIC DE10-NANO", 10.5, "white", "bold", ha="left")
t(bx + 0.4, by + bh - 0.92, "Cyclone V SoC 5CSEBA6U23I7  ·  clock FPGA_CLK1_50 (PIN_V11)", 6.8, "#A7F3D0", ha="left")
port(bx + 7.1, by + bh - 0.8, 1.9, 0.6, "USB-Blaster II\n(mini-USB)", 6.2)
port(bx + 9.4, by + bh - 0.8, 1.7, 0.6, "DC 5 V / 2 A", 6.2)

# FPGA
fx, fy, fw, fh = bx + 6.3, by + 4.6, 5.0, 3.2
rbox(fx, fy, fw, fh, "#111827", "#4B5563", lw=1.4, r=0.12, z=3)
t(fx + fw / 2, fy + fh - 0.48, "Cyclone V FPGA fabric", 8.4, "white", "bold")
t(fx + fw / 2, fy + fh / 2 - 0.2, "de10_nano_top\n├─ uart_bridge  (115200 8N1)\n└─ screener_top (SATRIA-CHIP)",
  6.6, "#93C5FD", family=MONO)

# header JP1 2x20, mendatar: pin ganjil baris bawah, pin genap baris atas
jx, jy, p = bx + 0.9, by + 3.35, 0.36
ax.add_patch(Rectangle((jx - 0.24, jy - 0.24), 19 * p + 0.48, p + 0.48, fc="#1F2937", ec="#9CA3AF", lw=1, zorder=3))
pin = {}
USED = {1: C_TX, 2: C_RX, 12: "#E5E7EB"}
WARN = {11, 29}
for n in range(1, 41):
    col, top = (n - 1) // 2, (n % 2 == 0)
    x, y = jx + col * p, jy + (p if top else 0)
    pin[n] = (x, y)
    fc = USED.get(n) or ("#7F1D1D" if n in WARN else "#4B5563")
    ec = "white" if n in USED else ("#FCA5A5" if n in WARN else "#6B7280")
    ax.add_patch(Rectangle((x - 0.11, y - 0.11), 0.22, 0.22, fc=fc, ec=ec, lw=0.8, zorder=6))
t(pin[1][0], pin[1][1] - 0.32, "1", 5.8, "#D1D5DB")
t(pin[2][0], pin[2][1] + 0.3, "2", 5.8, "#D1D5DB")
t(pin[39][0] + 0.45, pin[39][1], "39", 6.2, "#D1D5DB")
t(pin[40][0] + 0.45, pin[40][1], "40", 6.2, "#D1D5DB")
t(jx - 0.24, jy - 0.55, "JP1 (GPIO_0) — header 2×20, pitch 2,54 mm", 6.8, "white", "bold", ha="left")
for n in (11, 29):
    t(pin[n][0], pin[n][1] - 0.32, str(n), 5.8, "#FCA5A5")
t(pin[12][0] + 0.32, pin[12][1] + 0.2, "12", 5.8, "#E5E7EB")

# jalur header -> FPGA
wire([(fx + 1.0, jy + p + 0.24), (fx + 1.0, fy)], "#6EE7B7", lw=1.4, dots=False)
t(fx + 1.15, jy + 1.0, "GPIO_0[1:0] → UART_RX / UART_TX", 6.0, "#6EE7B7", ha="left", family=MONO)

# legenda pin di bawah header
legend = [(C_TX, "pin 1   GPIO_0[0]  PIN_V12  UART_RX ← TXD"),
          (C_RX, "pin 2   GPIO_0[1]  PIN_E8   UART_TX → RXD"),
          ("#E5E7EB", "pin 12  GND                GND ↔ GND"),
          ("#7F1D1D", "pin 11 VCC5, pin 29 VCC3P3: jangan disambung")]
for i, (c, s) in enumerate(legend):
    yy = by + 2.15 - i * 0.42
    ax.add_patch(Rectangle((jx - 0.24, yy - 0.1), 0.2, 0.2, fc=c, ec="#9CA3AF", lw=0.6, zorder=6))
    t(jx + 0.12, yy, s, 6.4, "#FCA5A5" if i == 3 else "#E5E7EB", ha="left", family=MONO)

# LED & tombol
lx, ly = fx + 0.2, by + 0.75
t(lx, ly + 1.2, "LED[7:0]", 7, "white", "bold", ha="left")
led_c = {0: "#FACC15", 1: "#FACC15", 2: "#60A5FA", 3: "#A78BFA", 7: "#F87171"}
for i in range(8):
    k, x = 7 - i, lx + i * 0.42
    ax.add_patch(Rectangle((x, ly + 0.45), 0.26, 0.42, fc=led_c.get(k, "#374151"), ec="#9CA3AF", lw=0.6, zorder=6))
    t(x + 0.13, ly + 0.2, str(k), 5.8, "#D1D5DB")
for i, (name, desc) in enumerate([("KEY0", "reset"), ("KEY1", "tamper")]):
    kx = fx + 3.75 + i * 0.75
    ax.add_patch(Rectangle((kx, ly + 0.4), 0.55, 0.55, fc="#E5E7EB", ec="#6B7280", lw=0.8, zorder=6))
    ax.add_patch(Circle((kx + 0.275, ly + 0.675), 0.17, fc="#374151", zorder=7))
    t(kx + 0.275, ly + 0.05, f"{name}\n{desc}", 5.6, "#D1D5DB")

# ---------------------------------------------------------------- kabel
top_y = by + bh + 0.25
ub, pw = (bx + 8.05, by + bh - 0.2), (bx + 10.25, by + bh - 0.2)
wire([(hx + hw, hy + 2.0), (5.6, hy + 2.0), (5.6, top_y), (ub[0], top_y), ub], C_USB)
t(8.3, top_y + 0.2, "kabel USB A ↔ mini-B  ·  JTAG / pemrograman screener.sof", 6.8, C_USB, "bold")
wire([(hx + hw, hy + 0.85), (5.25, hy + 0.85), (5.25, ay0 + 1.17), (ax0 - 0.05, ay0 + 1.17)], C_USB)
wire([(pw[0], top_y + 0.05), pw], C_PWR, lw=2.6)
t(pw[0] + 0.15, top_y + 0.12, "adaptor 5 V / 2 A", 6.6, C_PWR, "bold", ha="left")

ex = ax0 + aw
wire([(ex, apin["GND"]), (pin[12][0], apin["GND"]), (pin[12][0], pin[12][1] + 0.11)], C_GND)
wire([(ex, apin["RXD"]), (11.15, apin["RXD"]), (11.15, pin[2][1]), (pin[2][0] - 0.11, pin[2][1])], C_RX)
wire([(ex, apin["TXD"]), (10.75, apin["TXD"]), (10.75, pin[1][1]), (pin[1][0] - 0.11, pin[1][1])], C_TX)

# ---------------------------------------------------------------- tabel
def table(x, y, cols, widths, rows, title):
    t(x, y + 0.36, title, 7.6, NAVY, "bold", ha="left")
    tw = sum(widths)
    ax.add_patch(Rectangle((x, y - 0.36), tw, 0.36, fc=NAVY, ec=NAVY, zorder=2))
    cx = x
    for c, w in zip(cols, widths):
        t(cx + 0.08, y - 0.18, c, 6.3, "white", "bold", ha="left"); cx += w
    for r, row in enumerate(rows):
        yy = y - 0.36 - (r + 1) * 0.33
        if r % 2 == 0:
            ax.add_patch(Rectangle((x, yy), tw, 0.33, fc="#F3F4F6", ec="none", zorder=1))
        cx = x
        for v, w in zip(row, widths):
            t(cx + 0.08, yy + 0.165, v, 6.2, INK, ha="left", family=MONO if cx > x else SANS); cx += w
    ax.plot([x, x + tw], [y - 0.36 - len(rows) * 0.33] * 2, color=LINE, lw=0.8)


table(0.6, 6.55, ["Sinyal", "Adaptor", "JP1", "Pin FPGA", "Standar I/O"], [1.05, 0.95, 0.55, 1.05, 1.35],
      [["UART_RX", "TXD", "1", "PIN_V12", "3.3-V LVTTL"],
       ["UART_TX", "RXD", "2", "PIN_E8", "3.3-V LVTTL"],
       ["GND", "GND", "12", "—", "—"]],
      "Tabel koneksi (quartus/screener.qsf)")
table(0.6, 4.25, ["Elemen", "Pin FPGA", "Fungsi"], [1.05, 1.6, 2.65],
      [["KEY0", "PIN_AH17", "reset (aktif rendah)"],
       ["KEY1", "PIN_AH16", "sensor tamper → zeroize"],
       ["LED[1:0]", "PIN_AA24, W15", "vonis terakhir"],
       ["LED[2]", "PIN_V16", "transaksi selesai"],
       ["LED[3]", "PIN_V15", "status LOCK"],
       ["LED[7]", "PIN_AA23", "status TAMPER"]],
      "Antarmuka pengguna on-board (rtl/de10_nano_top.v)")

# ---------------------------------------------------------------- catatan & blok judul
t(0.6, 1.05, "⚠  Logika 3,3 V: jangan sambungkan VCC adaptor ke JP1.  UART 115200 bps, 8N1, tanpa flow control.",
  6.8, C_PWR, "bold", ha="left")
t(0.6, 0.65, "Target bootcamp: jalur UART diganti HPS-to-FPGA Lightweight AXI Bridge (adaptor tidak diperlukan).",
  6.6, MUTED, ha="left")
tbx, tby, tbw = W - 7.0, 0.3, 6.4
ax.add_patch(Rectangle((tbx, tby), tbw, 1.6, fc="white", ec="#9CA3AF", lw=0.8, zorder=2))
for yy in (tby + 0.55, tby + 1.05):
    ax.plot([tbx, tbx + tbw], [yy, yy], color=LINE, lw=0.6)
t(tbx + 0.12, tby + 1.32, "SATRIA-CHIP · Wiring demo DE10-Nano", 7.0, INK, "bold", ha="left")
t(tbx + 0.12, tby + 0.8, "Tim Paket Kulit 12k · Telkom University", 6.3, MUTED, ha="left")
t(tbx + tbw - 0.12, tby + 0.8, "Rev 2 · 7 Okt 2026", 6.3, MUTED, ha="right")
t(tbx + 0.12, tby + 0.28, "Sumber pin: quartus/screener.qsf · rtl/de10_nano_top.v", 6.0, MUTED, ha="left")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig", "wiring_de10nano.png")
fig.savefig(out, dpi=200, facecolor="white")
print("saved", out)
