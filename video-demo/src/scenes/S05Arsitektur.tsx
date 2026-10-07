import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { theme } from "../theme";
import { Entrance } from "../components/Motion";
import { Headline, Kicker, PAD } from "../components/UI";

const TIERS = [
  { n: "1", t: "Gateway (host tidak dipercaya)", d: "Instruksi SNAP BI & bursa kripto dikemas jadi rekaman 64 byte + tag HMAC." },
  { n: "2", t: "Silikon FPGA", d: "Verifikasi, aturan, vonis, token, dan log audit — semuanya ≤15 µs." },
  { n: "3", t: "Edge SoC (ARM HPS)", d: "Driver AXI dan penyusun draf LTKM berformat goAML (target bootcamp)." },
  { n: "4", t: "Tindak lanjut kepatuhan", d: "Core banking hanya mengeksekusi transaksi bertoken valid; ESCALATE = ditunda." },
];
const STEP = 90;
const FIRST = 70;

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const S05Arsitektur: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const active = Math.max(0, Math.min(TIERS.length - 1, Math.floor((frame - FIRST) / STEP)));
  const kb = interpolate(frame, [0, dur], [1.0, 1.08], { ...clamp, easing: theme.ease.inOut });
  const pan = interpolate(frame, [0, dur], [10, -20], { ...clamp, easing: theme.ease.inOut });
  return (
    <AbsoluteFill style={{ padding: `86px ${PAD}px` }}>
      <Kicker text="Arsitektur end-to-end" />
      <div style={{ height: 22 }} />
      <Headline text="Empat lapis, satu batas tepercaya di silikon" size={64} delay={6} />
      <div style={{ display: "flex", gap: 50, marginTop: 50, alignItems: "flex-start" }}>
        <div style={{ width: 560, display: "flex", flexDirection: "column", gap: 18 }}>
          {TIERS.map((t, i) => {
            const on = i === active && frame >= FIRST;
            return (
              <Entrance key={t.n} delay={FIRST + i * STEP} y={30}>
                <div style={{
                  display: "flex", gap: 20, padding: "20px 22px", borderRadius: 18,
                  background: on ? `${theme.colors.primary}14` : theme.colors.card,
                  border: `1.5px solid ${on ? theme.colors.primary : theme.colors.line}`,
                  boxShadow: on ? `0 0 40px ${theme.colors.glow}` : "none",
                }}>
                  <div style={{
                    minWidth: 52, height: 52, borderRadius: 14, display: "flex", alignItems: "center", justifyContent: "center",
                    fontFamily: theme.fonts.display, fontWeight: 700, fontSize: 28,
                    color: on ? theme.colors.bg : theme.colors.text, background: on ? theme.colors.primary : theme.colors.bgAlt,
                  }}>{t.n}</div>
                  <div>
                    <div style={{ fontFamily: theme.fonts.display, fontWeight: 600, fontSize: 30, color: theme.colors.text }}>{t.t}</div>
                    <div style={{ fontFamily: theme.fonts.body, fontSize: 22, color: theme.colors.textDim, marginTop: 6, lineHeight: 1.35 }}>{t.d}</div>
                  </div>
                </div>
              </Entrance>
            );
          })}
        </div>
        <Entrance delay={30} y={50} style={{ flex: 1 }}>
          <div style={{
            borderRadius: 24, overflow: "hidden", border: `1px solid ${theme.colors.line}`, background: "#fff",
            boxShadow: "0 40px 80px -20px rgba(0,0,0,0.7)", height: 690,
          }}>
            <Img src={staticFile("img/arsitektur.png")} style={{
              width: "100%", height: "100%", objectFit: "contain",
              transform: `scale(${kb}) translateX(${pan}px)`,
            }} />
          </div>
        </Entrance>
      </div>
    </AbsoluteFill>
  );
};
