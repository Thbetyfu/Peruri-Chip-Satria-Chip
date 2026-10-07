import React from "react";
import { AbsoluteFill, interpolate, Sequence, useCurrentFrame } from "remotion";
import { theme } from "../theme";
import { Entrance, WordReveal } from "../components/Motion";
import { Card, ChipMark, Headline, Kicker, PAD } from "../components/UI";

const DAYS = [
  { d: "Hari 1", t: "Bring-up board", s: "Bitstream di DE10-Nano, 12 skenario on-board lewat UART, trace SignalTap 411 cycle." },
  { d: "Hari 2", t: "Integrasi SoC", s: "HPS-to-FPGA Lightweight AXI bridge; uji serangan root dari Linux di ARM HPS." },
  { d: "Hari 3", t: "Ukur & pitching", s: "Daya dan throughput riil di board, draf LTKM, video & laporan teknis." },
];

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const SPLIT = 230;

const Plan: React.FC = () => {
  const frame = useCurrentFrame();
  const exit = interpolate(frame, [SPLIT - 12, SPLIT - 2], [0, 1], { ...clamp, easing: theme.ease.in });
  return (
    <AbsoluteFill style={{ padding: `86px ${PAD}px`, justifyContent: "center", opacity: 1 - exit, transform: `translateY(${-exit * 40}px)` }}>
      <Kicker text="Rencana bootcamp" />
      <div style={{ height: 22 }} />
      <Headline text="Dari simulasi ke board fisik dalam tiga hari" size={64} delay={6} />
      <div style={{ display: "flex", gap: 30, marginTop: 70 }}>
        {DAYS.map((x, i) => (
          <Entrance key={x.d} delay={40 + i * 16} y={40} style={{ flex: 1 }}>
            <Card style={{ padding: 38, height: 330 }}>
              <div style={{ fontFamily: theme.fonts.mono, fontSize: 22, color: theme.colors.accent }}>{x.d}</div>
              <div style={{ fontFamily: theme.fonts.display, fontWeight: 700, fontSize: 44, color: theme.colors.text, marginTop: 14 }}>{x.t}</div>
              <div style={{ fontFamily: theme.fonts.body, fontSize: 26, color: theme.colors.textDim, marginTop: 16, lineHeight: 1.45 }}>{x.s}</div>
            </Card>
          </Entrance>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const EndCard: React.FC = () => (
  <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column" }}>
    <Entrance delay={0} y={30} config="bouncy"><ChipMark size={250} /></Entrance>
    <div style={{ height: 36 }} />
    <WordReveal text="SATRIA-CHIP" delay={10} style={{
      fontFamily: theme.fonts.display, fontWeight: 700, fontSize: 120, letterSpacing: "-0.04em", color: theme.colors.text, lineHeight: 1,
    }} />
    <Entrance delay={26} y={20}>
      <div style={{ fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 36, color: theme.colors.textDim, marginTop: 20, textAlign: "center" }}>
        Aturan anti-pencucian uang yang ditegakkan di silikon.
      </div>
    </Entrance>
    <Entrance delay={44} y={16}>
      <div style={{ fontFamily: theme.fonts.body, fontSize: 28, color: theme.colors.text, marginTop: 44, textAlign: "center" }}>
        Tim Paket Kulit 12k · Telkom University · PERURI Chip Hackathon 2026
      </div>
    </Entrance>
    <Entrance delay={54} y={12}>
      <div style={{ fontFamily: theme.fonts.mono, fontSize: 24, color: theme.colors.accent, marginTop: 16, textAlign: "center" }}>
        github.com/Thbetyfu/Peruri-Chip-Satria-Chip
      </div>
    </Entrance>
  </AbsoluteFill>
);

export const S10Penutup: React.FC = () => (
  <AbsoluteFill>
    <Sequence durationInFrames={SPLIT}><Plan /></Sequence>
    <Sequence from={SPLIT}><EndCard /></Sequence>
  </AbsoluteFill>
);
