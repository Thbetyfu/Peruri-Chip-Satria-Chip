import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme, verdictColor } from "../theme";
import { DEMO_ROWS } from "../data";
import { Entrance, fmtId } from "../components/Motion";
import { Card, Headline, Kicker, PAD, Pill } from "../components/UI";

export const ROW_FIRST = 100;
export const ROW_STEP = 115;
const COLS = [500, 190, 180, 260, 390, 0];

const Row: React.FC<{ i: number }> = ({ i }) => {
  const r = DEMO_ROWS[i];
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const at = ROW_FIRST + i * ROW_STEP;
  const p = spring({ frame: frame - at, fps, config: theme.spring.smooth });
  const pill = spring({ frame: frame - at - 12, fps, config: theme.spring.bouncy });
  const latest = frame >= at && (i === DEMO_ROWS.length - 1 || frame < at + ROW_STEP);
  const c = verdictColor(r.verdict);
  const us = r.cycles === "-" ? "—" : `${r.cycles} cyc · ${fmtId(r.cycles / 50, 2)} µs`;
  return (
    <div style={{
      display: "flex", alignItems: "center", height: 76, padding: "0 28px",
      borderTop: `1px solid ${theme.colors.line}`,
      background: latest ? `${c}10` : "transparent",
      opacity: interpolate(p, [0, 1], [0, 1]),
      transform: `translateX(${interpolate(p, [0, 1], [-50, 0])}px)`,
    }}>
      <div style={{ width: COLS[0], fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 25, color: theme.colors.text }}>{r.label}</div>
      <div style={{ width: COLS[1], transform: `scale(${interpolate(pill, [0, 1], [0.5, 1])})`, opacity: interpolate(pill, [0, 1], [0, 1]), transformOrigin: "left center" }}>
        <Pill text={r.verdict} color={c} size={21} />
      </div>
      <div style={{ width: COLS[2], fontFamily: theme.fonts.mono, fontSize: 21, color: r.reasons === "—" ? theme.colors.textFaint : c }}>{r.reasons}</div>
      <div style={{ width: COLS[3], fontFamily: theme.fonts.mono, fontSize: 20, color: theme.colors.textDim, whiteSpace: "nowrap" }}>{us}</div>
      <div style={{ width: COLS[4], fontFamily: theme.fonts.body, fontSize: 23, color: theme.colors.text }}>{r.action}</div>
      <div style={{ flex: 1, fontFamily: theme.fonts.mono, fontSize: 19, color: theme.colors.textFaint, textAlign: "right" }}>{r.token.slice(0, 8)}…</div>
    </div>
  );
};

export const S07Demo: React.FC = () => (
  <AbsoluteFill style={{ padding: `80px ${PAD}px` }}>
    <Kicker text="Demo" />
    <div style={{ height: 20 }} />
    <Headline text="Tujuh skenario, vonis dihitung model yang bit-exact dengan RTL" size={54} width={1680} delay={6} />
    <Entrance delay={34} y={14}>
      <div style={{ fontFamily: theme.fonts.mono, fontSize: 20, color: theme.colors.textFaint, marginTop: 16 }}>
        golden model Python ≡ RTL (regresi 10.000/10.000) · ambang demo Rp100 juta · uji on-board DE10-Nano saat bootcamp
      </div>
    </Entrance>
    <Entrance delay={60} y={40} style={{ marginTop: 34 }}>
      <Card style={{ overflow: "hidden" }}>
        <div style={{ display: "flex", alignItems: "center", height: 60, padding: "0 28px", background: theme.colors.bgAlt }}>
          {["Skenario", "Vonis chip", "Alasan", "Latensi", "Tindak lanjut", "Token (HMAC)"].map((h, i) => (
            <div key={h} style={{
              width: COLS[i] || undefined, flex: COLS[i] ? undefined : 1, textAlign: i === 5 ? "right" : "left",
              fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 19, letterSpacing: "0.08em", textTransform: "uppercase",
              color: theme.colors.textDim,
            }}>{h}</div>
          ))}
        </div>
        {DEMO_ROWS.map((_, i) => <Row key={i} i={i} />)}
      </Card>
    </Entrance>
  </AbsoluteFill>
);
