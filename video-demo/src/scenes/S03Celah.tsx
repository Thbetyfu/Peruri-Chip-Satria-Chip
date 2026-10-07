import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { Entrance, useBreathe, useProgress } from "../components/Motion";
import { Body, Card, Headline, Kicker, PAD } from "../components/UI";

const ROWS = [
  { name: "Filter anti-pencucian uang", hit: "dimatikan", at: 150 },
  { name: "Ambang & aturan penundaan", hit: "dilonggarkan", at: 205 },
  { name: "Log audit transaksi", hit: "dihapus", at: 260 },
];

const Row: React.FC<{ name: string; hit: string; at: number; delay: number }> = ({ name, hit, at, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const h = spring({ frame: frame - at, fps, config: theme.spring.snappy });
  const strike = useProgress(at, 12);
  const shake = frame >= at && frame < at + 10 ? Math.sin((frame - at) * 2.6) * 6 * (1 - (frame - at) / 10) : 0;
  const col = h > 0.5 ? theme.colors.reject : theme.colors.accept;
  return (
    <Entrance delay={delay} y={24}>
      <div style={{
        display: "flex", alignItems: "center", gap: 20, padding: "20px 26px", borderRadius: 16,
        background: `${col}12`, border: `1.5px solid ${col}66`, transform: `translateX(${shake}px)`,
      }}>
        <div style={{
          width: 30, height: 30, borderRadius: 8, border: `2.5px solid ${col}`, display: "flex",
          alignItems: "center", justifyContent: "center", color: col, fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 20,
        }}>{h > 0.5 ? "×" : "✓"}</div>
        <div style={{ position: "relative", fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 30, color: theme.colors.text }}>
          {name}
          <div style={{
            position: "absolute", left: 0, top: "52%", height: 3, width: `${strike * 100}%`, background: theme.colors.reject,
          }} />
        </div>
        <div style={{ flex: 1 }} />
        <div style={{
          fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 24, color: theme.colors.reject,
          opacity: interpolate(h, [0, 1], [0, 1]), transform: `scale(${interpolate(h, [0, 1], [0.6, 1])})`,
        }}>{hit}</div>
      </div>
    </Entrance>
  );
};

export const S03Celah: React.FC = () => {
  const b = useBreathe(20, 0.02);
  const arrow = useProgress(120, 22);
  return (
    <AbsoluteFill style={{ padding: `86px ${PAD}px`, justifyContent: "center" }}>
      <Kicker text="Celahnya" />
      <div style={{ height: 22 }} />
      <Headline text="Keputusan tunda atau lolos masih berjalan sebagai software di server gateway" size={62} width={1600} delay={6} />
      <div style={{ display: "flex", gap: 60, marginTop: 60, alignItems: "center" }}>
        <Entrance delay={50} y={40} style={{ flex: 1 }}>
          <Card style={{ padding: 34 }}>
            <div style={{ fontFamily: theme.fonts.mono, fontSize: 22, color: theme.colors.textDim, marginBottom: 20 }}>
              SERVER GATEWAY · OS umum
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {ROWS.map((r, i) => <Row key={i} {...r} delay={62 + i * 6} />)}
            </div>
          </Card>
        </Entrance>
        <div style={{ width: 150, height: 4, position: "relative" }}>
          <div style={{ position: "absolute", right: 0, top: 0, height: 4, width: `${arrow * 100}%`, background: theme.colors.reject, borderRadius: 2 }} />
          <div style={{
            position: "absolute", left: -6, top: -11, width: 0, height: 0, opacity: arrow,
            borderTop: "13px solid transparent", borderBottom: "13px solid transparent", borderRight: `20px solid ${theme.colors.reject}`,
          }} />
        </div>
        <Entrance delay={100} y={40} style={{ width: 430 }}>
          <div style={{
            padding: 34, borderRadius: 24, border: `1.5px solid ${theme.colors.reject}88`, background: `${theme.colors.reject}12`,
            transform: `scale(${b.scale})`,
          }}>
            <div style={{ fontFamily: theme.fonts.display, fontWeight: 700, fontSize: 40, color: theme.colors.reject }}>Akses root</div>
            <div style={{ fontFamily: theme.fonts.body, fontSize: 26, color: theme.colors.text, marginTop: 10, lineHeight: 1.4 }}>
              malware atau orang dalam yang menguasai server
            </div>
          </div>
        </Entrance>
      </div>
      <div style={{ marginTop: 44 }}>
        <Body delay={320} size={34} color={theme.colors.text}>
          Hasilnya: transaksi mencurigakan lolos, <span style={{ color: theme.colors.reject, fontWeight: 600 }}>dan tidak ada jejak yang tersisa.</span>
        </Body>
      </div>
    </AbsoluteFill>
  );
};
