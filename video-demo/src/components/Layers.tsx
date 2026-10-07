// Lapisan latar dan finishing: BgMesh (paling bawah) … Grade → Grain → Vignette (paling atas).
import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { theme } from "../theme";

export const BgMesh: React.FC = () => {
  const frame = useCurrentFrame();
  const d1 = Math.sin(frame / 55) * 60;
  const d2 = Math.cos(frame / 70) * 50;
  const d3 = Math.sin(frame / 90) * 40;
  return (
    <AbsoluteFill style={{ background: theme.colors.bg }}>
      <div style={{
        position: "absolute", width: 1400, height: 1400, borderRadius: "50%",
        top: -620, left: -380 + d1, filter: "blur(60px)",
        background: `radial-gradient(circle, ${theme.colors.primary}22, transparent 62%)`,
      }} />
      <div style={{
        position: "absolute", width: 1200, height: 1200, borderRadius: "50%",
        bottom: -640, right: -360 - d2, filter: "blur(80px)",
        background: `radial-gradient(circle, ${theme.colors.accent}26, transparent 64%)`,
      }} />
      <div style={{
        position: "absolute", width: 900, height: 900, borderRadius: "50%",
        top: 160 + d3, left: 700, filter: "blur(90px)",
        background: `radial-gradient(circle, #1E293B55, transparent 65%)`,
      }} />
      {/* grid tipis ala papan sirkuit */}
      <AbsoluteFill style={{
        opacity: 0.07,
        backgroundImage:
          "linear-gradient(rgba(148,163,184,0.6) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.6) 1px, transparent 1px)",
        backgroundSize: "64px 64px",
        backgroundPosition: `${(frame * 0.3) % 64}px ${(frame * 0.15) % 64}px`,
        maskImage: "radial-gradient(ellipse at center, black 30%, transparent 75%)",
        WebkitMaskImage: "radial-gradient(ellipse at center, black 30%, transparent 75%)",
      }} />
    </AbsoluteFill>
  );
};

export const Grade: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <AbsoluteFill style={{ backgroundColor: theme.colors.accent, mixBlendMode: "soft-light", opacity: 0.12 }} />
    <AbsoluteFill style={{
      background: "linear-gradient(180deg, rgba(0,0,0,0.18), transparent 26%, transparent 74%, rgba(0,0,0,0.28))",
    }} />
  </AbsoluteFill>
);

const NOISE = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E")`;

export const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{
      pointerEvents: "none", backgroundImage: NOISE, backgroundSize: "220px",
      backgroundPosition: `${(frame * 7) % 220}px ${(frame * 13) % 220}px`,
      opacity: 0.06, mixBlendMode: "overlay",
    }} />
  );
};

export const Vignette: React.FC = () => (
  <AbsoluteFill style={{
    pointerEvents: "none",
    background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.42) 100%)",
  }} />
);
