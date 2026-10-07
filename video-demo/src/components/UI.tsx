// Elemen tipografi dan kartu yang dipakai ulang di semua adegan.
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { Entrance, WordReveal, useBreathe } from "./Motion";

export const PAD = 120; // margin aman kiri/kanan

export const Kicker: React.FC<{ text: string; delay?: number; color?: string }> = ({ text, delay = 0, color = theme.colors.accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: theme.spring.snappy });
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 16,
      opacity: interpolate(p, [0, 1], [0, 1]),
      transform: `translateX(${interpolate(p, [0, 1], [-30, 0])}px)`,
    }}>
      <div style={{ width: interpolate(p, [0, 1], [0, 56]), height: 3, background: color, borderRadius: 2 }} />
      <span style={{
        fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 24, letterSpacing: "0.16em",
        textTransform: "uppercase", color,
      }}>{text}</span>
    </div>
  );
};

export const Headline: React.FC<{
  text: string; delay?: number; size?: number; highlight?: string[]; width?: number; color?: string;
}> = ({ text, delay = 0, size = 76, highlight = [], width = 1500, color = theme.colors.text }) => (
  <WordReveal
    text={text} delay={delay} highlight={highlight} gap={Math.round(size * 0.26)}
    style={{
      fontFamily: theme.fonts.display, fontWeight: 700, fontSize: size, lineHeight: 1.08,
      letterSpacing: "-0.03em", color, maxWidth: width, rowGap: Math.round(size * 0.08),
    }}
  />
);

export const Body: React.FC<{ children: React.ReactNode; delay?: number; size?: number; width?: number; color?: string }> = ({
  children, delay = 0, size = 32, width = 1300, color = theme.colors.textDim,
}) => (
  <Entrance delay={delay} y={24}>
    <div style={{ fontFamily: theme.fonts.body, fontWeight: 400, fontSize: size, lineHeight: 1.45, color, maxWidth: width }}>
      {children}
    </div>
  </Entrance>
);

export const SourceTag: React.FC<{ text: string; delay?: number }> = ({ text, delay = 0 }) => (
  <Entrance delay={delay} y={12}>
    <div style={{ fontFamily: theme.fonts.mono, fontSize: 18, color: theme.colors.textFaint, letterSpacing: "0.02em" }}>
      Sumber: {text}
    </div>
  </Entrance>
);

export const Card: React.FC<{
  children: React.ReactNode; style?: React.CSSProperties; border?: string; glow?: boolean;
}> = ({ children, style, border = theme.colors.line, glow = false }) => (
  <div style={{
    background: theme.colors.card, border: `1px solid ${border}`, borderRadius: 24,
    boxShadow: glow
      ? `0 0 60px ${theme.colors.glow}, 0 30px 60px -20px rgba(0,0,0,0.6)`
      : "0 30px 60px -24px rgba(0,0,0,0.65)",
    backdropFilter: "blur(10px)", ...style,
  }}>{children}</div>
);

export const Pill: React.FC<{ text: string; color: string; size?: number }> = ({ text, color, size = 22 }) => (
  <span style={{
    display: "inline-block", padding: `${size * 0.28}px ${size * 0.7}px`, borderRadius: 999,
    border: `1.5px solid ${color}`, color, background: `${color}1F`,
    fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: size, letterSpacing: "0.04em",
  }}>{text}</span>
);

/** Ikon chip dari CSS (bukan emoji): badan + kaki di empat sisi. */
export const ChipMark: React.FC<{ size?: number; glow?: boolean; label?: string }> = ({ size = 220, glow = true, label = "SATRIA" }) => {
  const b = useBreathe(26, 0.015);
  const pins = 7;
  const pinLen = size * 0.12;
  const body = size * 0.64;
  const off = (size - body) / 2;
  const pinStyle = (i: number, side: "t" | "b" | "l" | "r"): React.CSSProperties => {
    const pos = off + (body / (pins + 1)) * (i + 1) - size * 0.012;
    const common: React.CSSProperties = { position: "absolute", background: theme.colors.textDim, borderRadius: 2 };
    if (side === "t") return { ...common, left: pos, top: off - pinLen, width: size * 0.024, height: pinLen };
    if (side === "b") return { ...common, left: pos, top: off + body, width: size * 0.024, height: pinLen };
    if (side === "l") return { ...common, top: pos, left: off - pinLen, height: size * 0.024, width: pinLen };
    return { ...common, top: pos, left: off + body, height: size * 0.024, width: pinLen };
  };
  return (
    <div style={{ position: "relative", width: size, height: size, transform: `scale(${b.scale}) translateY(${b.float}px)` }}>
      {(["t", "b", "l", "r"] as const).flatMap((s) => Array.from({ length: pins }).map((_, i) => <div key={s + i} style={pinStyle(i, s)} />))}
      <div style={{
        position: "absolute", left: off, top: off, width: body, height: body, borderRadius: size * 0.08,
        background: "linear-gradient(145deg, #1E293B, #0B1220)", border: `2px solid ${glow ? theme.colors.primary : theme.colors.line}`,
        boxShadow: glow ? `0 0 60px ${theme.colors.glow}, inset 0 0 30px rgba(45,212,191,0.12)` : "none",
        display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column",
      }}>
        <div style={{ fontFamily: theme.fonts.display, fontWeight: 700, fontSize: size * 0.13, color: theme.colors.text, letterSpacing: "-0.02em" }}>{label}</div>
        <div style={{ fontFamily: theme.fonts.mono, fontSize: size * 0.06, color: theme.colors.textDim, marginTop: size * 0.03 }}>FPGA · 5CSEBA6</div>
      </div>
    </div>
  );
};
