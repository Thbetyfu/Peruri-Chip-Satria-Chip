import React from "react";
import { AbsoluteFill } from "remotion";
import { theme } from "../theme";
import { Counter, Entrance } from "../components/Motion";
import { Card, Headline, Kicker, PAD } from "../components/UI";

type M = { big: React.ReactNode; label: string; hero?: boolean };
const D = 70;
const METRICS: M[] = [
  { big: <><Counter to={10000} delay={D + 14} />/10.000</>, label: "transaksi acak bit-exact vs golden model", hero: true },
  { big: <><Counter to={13} delay={D} />/13</>, label: "tes core cocotb lulus (12 skenario + laporan)" },
  { big: <Counter to={8.22} decimals={2} suffix=" µs" delay={D + 28} />, label: "per transaksi (411 cycle @ 50 MHz)" },
  { big: <Counter to={75.04} decimals={2} suffix=" MHz" delay={D + 42} />, label: "Fmax · target 50 MHz, slack setup +6,67 ns" },
  { big: <Counter to={10} suffix="%" delay={D + 56} />, label: "ALM terpakai (4.346 / 41.910) · 0 DSP · 15 M10K" },
  { big: <>±<Counter to={20} delay={D + 70} />×</>, label: "SHA-256: 65 vs 1.284 cycle/blok baseline TT07" },
  { big: <Counter to={0} delay={D + 84} suffix=" bocor" />, label: "kunci rahasia pada sapuan 256 alamat bus" },
  { big: <Counter to={493.84} decimals={2} suffix=" mW" delay={D + 98} />, label: "estimasi daya @ 50 MHz (Power Analyzer)" },
];

export const S09Bukti: React.FC = () => (
  <AbsoluteFill style={{ padding: `86px ${PAD}px`, justifyContent: "center" }}>
    <Kicker text="Bukti, bukan klaim" />
    <div style={{ height: 22 }} />
    <Headline text="Terverifikasi di simulasi RTL dan sintesis Quartus" size={64} delay={6} />
    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 26, marginTop: 56 }}>
      {METRICS.map((m, i) => (
        <Entrance key={i} delay={D + i * 14} y={40}>
          <Card glow={m.hero} border={m.hero ? theme.colors.primary : theme.colors.line} style={{ padding: "32px 30px", height: 270 }}>
            <div style={{
              fontFamily: theme.fonts.display, fontWeight: 700, fontSize: 54, letterSpacing: "-0.03em", lineHeight: 1.05, whiteSpace: "nowrap",
              color: m.hero ? theme.colors.primary : theme.colors.text,
            }}>{m.big}</div>
            <div style={{ fontFamily: theme.fonts.body, fontSize: 24, color: theme.colors.textDim, marginTop: 18, lineHeight: 1.35 }}>
              {m.label}
            </div>
          </Card>
        </Entrance>
      ))}
    </div>
    <Entrance delay={260} y={20} style={{ marginTop: 44 }}>
      <div style={{ fontFamily: theme.fonts.mono, fontSize: 22, color: theme.colors.textFaint }}>
        Icarus Verilog 12 · cocotb 2.1 · Quartus Prime Lite 24.1 · Cyclone V 5CSEBA6U23I7 · log di repo Peruri-Chip-Satria-Chip
      </div>
    </Entrance>
  </AbsoluteFill>
);
