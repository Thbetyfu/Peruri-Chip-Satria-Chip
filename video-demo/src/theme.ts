// theme.ts — satu-satunya sumber warna, easing, spring, dan font.
// Jangan menulis hex/easing langsung di komponen.
import { Easing } from "remotion";

export const theme = {
  colors: {
    bg: "#060A14",
    bgAlt: "#0D1424",
    card: "rgba(17, 25, 44, 0.78)",
    line: "rgba(148, 163, 184, 0.16)",
    primary: "#2DD4BF", // warna hero — maksimal satu elemen per frame
    accent: "#60A5FA",
    text: "#F1F5F9",
    textDim: "#94A3B8",
    textFaint: "#64748B",
    glow: "rgba(45, 212, 191, 0.40)",
    // warna semantik vonis (data, bukan dekorasi)
    accept: "#34D399",
    flag: "#FBBF24",
    escalate: "#FB923C",
    reject: "#F87171",
  },
  fonts: {
    display: "Inter Display",
    body: "Inter",
    mono: "DejaVu Sans Mono",
  },
  ease: {
    out: Easing.bezier(0.16, 1, 0.3, 1),
    inOut: Easing.bezier(0.83, 0, 0.17, 1),
    in: Easing.bezier(0.7, 0, 0.84, 0),
  },
  spring: {
    snappy: { damping: 14, stiffness: 160, mass: 0.6 },
    smooth: { damping: 20, stiffness: 90, mass: 1 },
    bouncy: { damping: 11, stiffness: 170, mass: 0.7 },
    counter: { damping: 30, stiffness: 60, mass: 1 },
  },
  video: { width: 1920, height: 1080, fps: 30 },
} as const;

export const verdictColor = (v: string): string =>
  v === "ACCEPT" ? theme.colors.accept
    : v === "FLAG" ? theme.colors.flag
      : v === "ESCALATE" ? theme.colors.escalate
        : theme.colors.reject;
