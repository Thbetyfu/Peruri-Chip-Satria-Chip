import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { Entrance, WordReveal } from "../components/Motion";
import { Body, ChipMark, Kicker, PAD } from "../components/UI";

const TAGS = ["HMAC-SHA256", "Rule engine", "Verdict token", "Audit hash-chain", "Anti-tamper"];

export const S04Solusi: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const chipIn = spring({ frame: frame - 4, fps, config: theme.spring.bouncy });
  const rot = spring({ frame: frame - 4, fps, config: theme.spring.smooth });
  return (
    <AbsoluteFill style={{ flexDirection: "row", alignItems: "center", padding: `0 ${PAD}px`, gap: 110 }}>
      <div style={{
        opacity: interpolate(chipIn, [0, 1], [0, 1]),
        transform: `scale(${interpolate(chipIn, [0, 1], [0.6, 1])}) rotate(${interpolate(rot, [0, 1], [-40, 0])}deg)`,
      }}>
        <ChipMark size={460} />
      </div>
      <div style={{ flex: 1 }}>
        <Kicker text="Solusi kami" delay={10} />
        <div style={{ height: 18 }} />
        <WordReveal text="SATRIA-CHIP" delay={14} style={{
          fontFamily: theme.fonts.display, fontWeight: 700, fontSize: 140, letterSpacing: "-0.04em",
          color: theme.colors.text, lineHeight: 1,
        }} />
        <Entrance delay={34} y={20}>
          <div style={{ fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 30, color: theme.colors.accent, marginTop: 14 }}>
            Sistem Akselerasi Penapisan Transaksi Real-Time &amp; Isolasi Aset
          </div>
        </Entrance>
        <div style={{ height: 34 }} />
        <Body delay={70} size={34} width={1000} color={theme.colors.text}>
          Co-processor keamanan berbasis FPGA yang memindahkan keputusan penapisan transaksi dan log auditnya ke dalam
          batas silikon. Aturannya tetap berlaku walaupun OS gateway diambil alih.
        </Body>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 14, marginTop: 40 }}>
          {TAGS.map((t, i) => (
            <Entrance key={t} delay={150 + i * 5} y={16} config="snappy">
              <span style={{
                display: "inline-block", padding: "10px 20px", borderRadius: 999, border: `1px solid ${theme.colors.line}`,
                background: theme.colors.bgAlt, fontFamily: theme.fonts.mono, fontSize: 22, color: theme.colors.textDim,
              }}>{t}</span>
            </Entrance>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};
