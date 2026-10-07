// Shim "remotion" untuk merender tanpa akses npm (lingkungan sandbox).
// interpolate / spring / Easing / interpolateColors = kode sumber ASLI Remotion 4.0.534
// (vendor-remotion-core, lisensi Remotion). Komponen lain diimplementasikan dengan perilaku yang sama
// untuk subset API yang dipakai proyek ini. Di laptop dengan npm, proyek memakai paket remotion resmi.
import React, { createContext, useContext } from "react";

export { interpolate } from "./vendor-remotion-core/interpolate";
export { Easing } from "./vendor-remotion-core/easing";
export { spring, measureSpring } from "./vendor-remotion-core/spring/index";
export { interpolateColors } from "./vendor-remotion-core/interpolate-colors";

type Cfg = { fps: number; width: number; height: number; durationInFrames: number; id: string };

export const __FrameCtx = createContext<number>(0);
export const __CfgCtx = createContext<Cfg>({ fps: 30, width: 1920, height: 1080, durationInFrames: 1, id: "x" });
const OffsetCtx = createContext<number>(0);

export const useCurrentFrame = (): number => useContext(__FrameCtx) - useContext(OffsetCtx);
export const useVideoConfig = (): Cfg => useContext(__CfgCtx);

export const AbsoluteFill = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ style, ...rest }, ref) => (
  <div ref={ref} {...rest} style={{
    position: "absolute", top: 0, left: 0, right: 0, bottom: 0, width: "100%", height: "100%",
    display: "flex", flexDirection: "column", ...style,
  }} />
));

export const Sequence: React.FC<{
  from?: number; durationInFrames?: number; children?: React.ReactNode; name?: string;
  layout?: "absolute-fill" | "none"; style?: React.CSSProperties;
}> = ({ from = 0, durationInFrames = Infinity, children, layout = "absolute-fill", style }) => {
  const parentOffset = useContext(OffsetCtx);
  const abs = useContext(__FrameCtx);
  const local = abs - parentOffset;
  if (local < from || local >= from + durationInFrames) return null;
  const inner = <OffsetCtx.Provider value={parentOffset + from}>{children}</OffsetCtx.Provider>;
  return layout === "none" ? inner : <AbsoluteFill style={style}>{inner}</AbsoluteFill>;
};

export const staticFile = (p: string): string => "public/" + p.replace(/^\/+/, "");

export const Img: React.FC<React.ImgHTMLAttributes<HTMLImageElement>> = (props) => <img {...props} />;

// Audio tidak dirender di browser; render-local/render.mjs me-mix isyarat audio dengan ffmpeg.
export const Audio: React.FC<Record<string, unknown>> = () => null;

declare global { interface Window { __pendingRenders: number } }
let handles = 0;
export const delayRender = (_label?: string): number => {
  window.__pendingRenders = (window.__pendingRenders || 0) + 1;
  return ++handles;
};
export const continueRender = (_h: number): void => {
  window.__pendingRenders = Math.max(0, (window.__pendingRenders || 0) - 1);
};

export const Composition: React.FC<Record<string, unknown>> = () => null;
export const registerRoot = (_c: unknown): void => undefined;
