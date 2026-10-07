import React from "react";
import { AbsoluteFill, interpolate, Sequence, useCurrentFrame } from "remotion";
import { theme } from "../theme";
import { SOURCES } from "../data";
import { Counter, Entrance, useBreathe } from "../components/Motion";
import { Headline, Kicker, PAD, SourceTag } from "../components/UI";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const Figure: React.FC = () => {
  const frame = useCurrentFrame();
  const b = useBreathe(24, 0.01);
  const exit = interpolate(frame, [150, 162], [0, 1], { ...clamp, easing: theme.ease.in });
  return (
    <AbsoluteFill style={{
      justifyContent: "center", alignItems: "center", flexDirection: "column", gap: 28,
      opacity: 1 - exit, transform: `translateY(${-exit * 60}px) scale(${1 - exit * 0.04})`,
    }}>
      <Entrance delay={6} y={60} config="bouncy">
        <div style={{
          fontFamily: theme.fonts.display, fontWeight: 700, fontSize: 210, letterSpacing: "-0.045em",
          color: theme.colors.primary, lineHeight: 1,
          textShadow: `0 0 60px ${theme.colors.primary}66, 0 0 120px ${theme.colors.primary}33`,
          transform: `scale(${b.scale})`,
        }}>
          <Counter to={286.82} decimals={2} prefix="Rp" delay={8} />
          <span style={{ fontSize: 112, marginLeft: 26, letterSpacing: "-0.02em" }}>triliun</span>
        </div>
      </Entrance>
      <Entrance delay={40} y={30}>
        <div style={{ fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 40, color: theme.colors.text }}>
          perputaran dana judi online di Indonesia sepanjang 2025
        </div>
      </Entrance>
      <SourceTag text={SOURCES.ppatkJudol} delay={62} />
    </AbsoluteFill>
  );
};

const Question: React.FC = () => (
  <AbsoluteFill style={{ justifyContent: "center", paddingLeft: PAD + 60, paddingRight: PAD }}>
    <Kicker text="Pertanyaannya" />
    <div style={{ height: 34 }} />
    <Headline
      text="Bagaimana jika filter yang seharusnya menahan aliran ini bisa dimatikan dari dalam?"
      size={92} width={1500} delay={4} highlight={["dimatikan"]}
    />
  </AbsoluteFill>
);

export const S01Hook: React.FC = () => (
  <AbsoluteFill>
    <div style={{ position: "absolute", left: PAD, top: 80 }}>
      <Kicker text="PERURI Chip Hackathon 2026 · Tim Paket Kulit 12k" delay={2} color={theme.colors.textDim} />
    </div>
    <Sequence durationInFrames={166}><Figure /></Sequence>
    <Sequence from={166}><Question /></Sequence>
  </AbsoluteFill>
);
