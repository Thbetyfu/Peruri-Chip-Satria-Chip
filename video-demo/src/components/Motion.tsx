// Komponen gerak dasar. Semua animasi memakai spring atau easing bezier, tidak ada yang linear.
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Masuk: opacity + naik + skala (3 properti sekaligus). */
export const Entrance: React.FC<{
  delay?: number; children: React.ReactNode; y?: number; style?: React.CSSProperties;
  config?: keyof typeof theme.spring;
}> = ({ delay = 0, children, y = 40, style, config = "smooth" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: theme.spring[config] });
  return (
    <div style={{
      opacity: interpolate(p, [0, 1], [0, 1], clamp),
      transform: `translateY(${interpolate(p, [0, 1], [y, 0])}px) scale(${interpolate(p, [0, 1], [0.94, 1])})`,
      ...style,
    }}>{children}</div>
  );
};

/** Teks muncul per kata (stagger 3 frame). Jarak antarkata pakai px, bukan em. */
export const WordReveal: React.FC<{
  text: string; delay?: number; per?: number; style?: React.CSSProperties;
  highlight?: string[]; highlightColor?: string; gap?: number;
}> = ({ text, delay = 0, per = 3, style, highlight = [], highlightColor = theme.colors.primary, gap = 18 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ display: "flex", flexWrap: "wrap", columnGap: gap, ...style }}>
      {text.split(" ").map((word, i) => {
        const p = spring({ frame: frame - delay - i * per, fps, config: theme.spring.snappy });
        const hl = highlight.includes(word.replace(/[.,:;?!]/g, ""));
        return (
          <span key={i} style={{
            display: "inline-block",
            opacity: interpolate(p, [0, 1], [0, 1], clamp),
            transform: `translateY(${interpolate(p, [0, 1], [34, 0])}px) scale(${interpolate(p, [0, 1], [0.96, 1])})`,
            color: hl ? highlightColor : undefined,
          }}>{word}</span>
        );
      })}
    </div>
  );
};

/** Format angka gaya Indonesia: titik ribuan, koma desimal. */
export const fmtId = (n: number, decimals = 0): string => {
  const fixed = Math.abs(n).toFixed(decimals);
  const [int, dec] = fixed.split(".");
  const withDots = int.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return (n < 0 ? "-" : "") + withDots + (dec ? "," + dec : "");
};

/** Penghitung angka dengan spring; tabular-nums supaya tidak bergetar. */
export const Counter: React.FC<{
  to: number; from?: number; delay?: number; decimals?: number; prefix?: string; suffix?: string;
  style?: React.CSSProperties;
}> = ({ to, from = 0, delay = 0, decimals = 0, prefix = "", suffix = "", style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: theme.spring.counter });
  const v = interpolate(p, [0, 1], [from, to]);
  return <span style={{ fontVariantNumeric: "tabular-nums", ...style }}>{prefix}{fmtId(v, decimals)}{suffix}</span>;
};

/** Pembungkus adegan: masuk ~20 frame, keluar 10 frame (lebih cepat dari masuk). */
export const SceneShell: React.FC<{ dur: number; children: React.ReactNode }> = ({ dur, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: theme.spring.smooth });
  const exitP = interpolate(frame, [dur - 12, dur - 2], [0, 1], { ...clamp, easing: theme.ease.in });
  return (
    <div style={{
      position: "absolute", inset: 0,
      opacity: interpolate(enter, [0, 1], [0, 1], clamp) * (1 - exitP),
      transform: `translateY(${interpolate(enter, [0, 1], [24, 0]) - exitP * 40}px) scale(${interpolate(enter, [0, 1], [0.985, 1]) + exitP * 0.02})`,
      filter: `blur(${exitP * 6}px)`,
    }}>{children}</div>
  );
};

/** Mikro-gerak untuk elemen yang tampil lama (>2 detik). */
export const useBreathe = (speed = 22, amp = 0.012) => {
  const frame = useCurrentFrame();
  return { scale: 1 + Math.sin(frame / speed) * amp, float: Math.sin(frame / (speed * 1.4)) * 4 };
};

/** Progres 0..1 dengan easing (untuk garis, bar, sapuan). */
export const useProgress = (start: number, len: number, easing = theme.ease.out) => {
  const frame = useCurrentFrame();
  return interpolate(frame, [start, start + len], [0, 1], { ...clamp, easing });
};
