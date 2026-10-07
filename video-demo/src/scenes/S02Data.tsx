import React from "react";
import { AbsoluteFill } from "remotion";
import { theme } from "../theme";
import { SOURCES } from "../data";
import { Counter, Entrance } from "../components/Motion";
import { Card, Headline, Kicker, PAD, SourceTag } from "../components/UI";

type Stat = { value: React.ReactNode; label: string; sub: string; src: string };

const STATS: Stat[] = [
  {
    value: <Counter to={183281} delay={70} />, label: "laporan transaksi keuangan mencurigakan (LTKM)",
    sub: "diterima PPATK sepanjang 2025 · 47,49% terkait judi online", src: SOURCES.ppatk2025,
  },
  {
    value: <Counter to={484.8} decimals={1} prefix="+" suffix="%" delay={100} />, label: "lonjakan laporan penundaan transaksi",
    sub: "menjadi 14.204 laporan pada 2025 — mekanisme tahan-sebelum-eksekusi makin diandalkan", src: SOURCES.ppatk2025,
  },
  {
    value: <Counter to={30} prefix="±Rp" suffix=" T" delay={130} />, label: "dana judi online dilarikan ke luar negeri",
    sub: "melalui instrumen aset kripto, sepanjang 2024", src: SOURCES.ppatkKripto,
  },
  {
    value: <Counter to={5.2} decimals={1} suffix=" miliar" delay={160} />, label: "anomali trafik siber terdeteksi",
    sub: "Januari–November 2025 · sektor keuangan dinilai paling rentan", src: SOURCES.bssn,
  },
];

export const S02Data: React.FC = () => (
  <AbsoluteFill style={{ padding: `86px ${PAD}px` }}>
    <Kicker text="Urgensi" />
    <div style={{ height: 22 }} />
    <Headline text="Skala kejahatan keuangan yang harus disaring setiap hari" size={62} width={1680} delay={6} />
    <div style={{ display: "grid", gridTemplateColumns: "minmax(0,1fr) minmax(0,1fr)", gap: 28, marginTop: 44 }}>
      {STATS.map((s, i) => (
        <Entrance key={i} delay={60 + i * 30} y={50}>
          <Card style={{ padding: "28px 36px", height: 262 }}>
            <div style={{
              fontFamily: theme.fonts.display, fontWeight: 700, fontSize: 76, letterSpacing: "-0.03em",
              color: theme.colors.text, lineHeight: 1,
            }}>{s.value}</div>
            <div style={{ fontFamily: theme.fonts.body, fontWeight: 500, fontSize: 28, color: theme.colors.text, marginTop: 16 }}>
              {s.label}
            </div>
            <div style={{ fontFamily: theme.fonts.body, fontSize: 21, color: theme.colors.textDim, marginTop: 8, lineHeight: 1.35 }}>
              {s.sub}
            </div>
            <div style={{ marginTop: 10 }}><SourceTag text={s.src} delay={90 + i * 30} /></div>
          </Card>
        </Entrance>
      ))}
    </div>
    <Entrance delay={420} y={30} style={{ marginTop: 36 }}>
      <div style={{
        display: "flex", alignItems: "center", gap: 26, padding: "22px 34px", borderRadius: 18,
        border: `1.5px solid ${theme.colors.primary}`, background: `${theme.colors.primary}14`,
        boxShadow: `0 0 50px ${theme.colors.glow}`,
      }}>
        <div style={{ fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 24, color: theme.colors.primary, whiteSpace: "nowrap" }}>
          UU 8/2010 Ps. 26
        </div>
        <div style={{ fontFamily: theme.fonts.body, fontSize: 28, color: theme.colors.text, lineHeight: 1.35 }}>
          Penyedia jasa keuangan boleh <b>menunda transaksi mencurigakan</b> hingga 5 hari kerja. Pertanyaannya: siapa yang menjamin keputusan itu tidak bisa diakali?
        </div>
      </div>
    </Entrance>
  </AbsoluteFill>
);
