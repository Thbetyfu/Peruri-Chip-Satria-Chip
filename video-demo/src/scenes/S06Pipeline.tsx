import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { theme } from "../theme";
import { Counter, Entrance, useProgress } from "../components/Motion";
import { Headline, Kicker, PAD } from "../components/UI";

const STAGES = [
  { n: "1", t: "Integrity Gate", d: "HMAC-SHA256 dengan kunci yang disimpan di silikon" },
  { n: "2", t: "Rule Engine", d: "Velocity, ambang nominal, anti-replay — 3 cycle" },
  { n: "3", t: "Decision Unit", d: "ACCEPT · FLAG · ESCALATE · REJECT" },
  { n: "4", t: "Verdict Token", d: "HMAC(K_tok) — syarat eksekusi di core banking" },
  { n: "5", t: "Audit Log", d: "Hash-chain 256 entri, read-only bagi host" },
];
const W = 300;
const GAP = 34;
const TRAVEL_START = 190;
const TRAVEL_LEN = 150;

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const SEGMENTS = [
  { label: "HMAC rekaman · 3 blok SHA-256", frac: 203 / 411, color: theme.colors.accent },
  { label: "aturan", frac: 5 / 411, color: theme.colors.flag },
  { label: "verdict token + log · 3 blok", frac: 203 / 411, color: theme.colors.accept },
];

export const S06Pipeline: React.FC = () => {
  const frame = useCurrentFrame();
  const line = useProgress(60, 70);
  const travel = interpolate(frame, [TRAVEL_START, TRAVEL_START + TRAVEL_LEN], [0, 1], { ...clamp, easing: theme.ease.inOut });
  const totalW = STAGES.length * W + (STAGES.length - 1) * GAP;
  const dotX = travel * (totalW - W) + W / 2;
  const activeIdx = frame >= TRAVEL_START && frame <= TRAVEL_START + TRAVEL_LEN + 30
    ? Math.round(travel * (STAGES.length - 1)) : -1;
  const bar = useProgress(360, 70);
  return (
    <AbsoluteFill style={{ padding: `86px ${PAD}px`, justifyContent: "center" }}>
      <Kicker text="Di dalam chip" />
      <div style={{ height: 22 }} />
      <Headline text="Lima tahap, deterministik, selesai dalam 411 cycle" size={64} delay={6} highlight={[]} />
      <div style={{ position: "relative", width: totalW, marginTop: 70, alignSelf: "center" }}>
        <div style={{ position: "absolute", left: W / 2, top: 60, height: 3, width: (totalW - W) * line, background: theme.colors.line }} />
        {travel > 0 && travel < 1 && (
          <div style={{
            position: "absolute", left: dotX - 9, top: 52, width: 18, height: 18, borderRadius: 9,
            background: theme.colors.text, boxShadow: `0 0 24px ${theme.colors.text}`,
          }} />
        )}
        <div style={{ display: "flex", gap: GAP }}>
          {STAGES.map((s, i) => {
            const on = i === activeIdx;
            return (
              <Entrance key={s.n} delay={50 + i * 14} y={40}>
                <div style={{ width: W }}>
                  <div style={{
                    width: 120, height: 120, margin: "0 auto", borderRadius: 30, display: "flex", alignItems: "center",
                    justifyContent: "center", fontFamily: theme.fonts.display, fontWeight: 700, fontSize: 52,
                    background: on ? theme.colors.primary : theme.colors.bgAlt, color: on ? theme.colors.bg : theme.colors.text,
                    border: `1.5px solid ${on ? theme.colors.primary : theme.colors.line}`,
                    boxShadow: on ? `0 0 50px ${theme.colors.glow}` : "0 20px 40px -20px rgba(0,0,0,0.6)",
                    position: "relative", zIndex: 2,
                  }}>{s.n}</div>
                  <div style={{ textAlign: "center", marginTop: 22, fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 30, color: theme.colors.text }}>{s.t}</div>
                  <div style={{ textAlign: "center", marginTop: 8, fontFamily: theme.fonts.body, fontSize: 21, color: theme.colors.textDim, lineHeight: 1.35 }}>{s.d}</div>
                </div>
              </Entrance>
            );
          })}
        </div>
      </div>
      <Entrance delay={350} y={30} style={{ marginTop: 70 }}>
        <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", marginBottom: 14 }}>
          <div style={{ fontFamily: theme.fonts.mono, fontSize: 22, color: theme.colors.textDim }}>
            Satu transaksi di fabric Cyclone V @ 50 MHz (simulasi RTL)
          </div>
          <div style={{ fontFamily: theme.fonts.display, fontWeight: 700, fontSize: 46, color: theme.colors.text }}>
            <Counter to={411} delay={370} suffix=" cycle" /> <span style={{ color: theme.colors.textDim }}>=</span> <Counter to={8.22} decimals={2} delay={370} suffix=" µs" />
          </div>
        </div>
        <div style={{ display: "flex", height: 54, borderRadius: 12, overflow: "hidden", border: `1px solid ${theme.colors.line}`, background: theme.colors.bgAlt }}>
          {SEGMENTS.map((s, i) => {
            const before = SEGMENTS.slice(0, i).reduce((a, x) => a + x.frac, 0);
            const fill = Math.max(0, Math.min(1, (bar - before) / s.frac));
            return (
              <div key={i} style={{ width: `${s.frac * 100}%`, position: "relative", borderRight: i < 2 ? `1px solid ${theme.colors.bg}` : "none" }}>
                <div style={{ position: "absolute", inset: 0, width: `${fill * 100}%`, background: `${s.color}55` }} />
                {s.frac > 0.1 && (
                  <div style={{
                    position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center",
                    fontFamily: theme.fonts.mono, fontSize: 20, color: theme.colors.text, opacity: fill,
                  }}>{s.label}</div>
                )}
              </div>
            );
          })}
        </div>
        <div style={{ fontFamily: theme.fonts.body, fontSize: 24, color: theme.colors.textDim, marginTop: 18 }}>
          Klien baru (kunci diturunkan ulang): 750 cycle = 15,00 µs · kapasitas core ±121.654 transaksi/detik — tidak menambah antrean transaksi sah.
        </div>
      </Entrance>
    </AbsoluteFill>
  );
};
