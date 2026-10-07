// Komposisi utama: BgMesh → adegan (aset + grafik) → Grade → Grain → Vignette, ditambah lapisan audio.
import React from "react";
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile } from "remotion";
import { theme } from "./theme";
import { SCENES } from "./data";
import { MUSIC, SFX_CUES } from "./audio";
import { ensureFonts } from "./fonts";
import { BgMesh, Grade, Grain, Vignette } from "./components/Layers";
import { SceneShell } from "./components/Motion";
import { S01Hook } from "./scenes/S01Hook";
import { S02Data } from "./scenes/S02Data";
import { S03Celah } from "./scenes/S03Celah";
import { S04Solusi } from "./scenes/S04Solusi";
import { S05Arsitektur } from "./scenes/S05Arsitektur";
import { S06Pipeline } from "./scenes/S06Pipeline";
import { S07Demo } from "./scenes/S07Demo";
import { S08Audit } from "./scenes/S08Audit";
import { S09Bukti } from "./scenes/S09Bukti";
import { S10Penutup } from "./scenes/S10Penutup";

ensureFonts();

const render = (id: string, dur: number): React.ReactNode => {
  switch (id) {
    case "hook": return <S01Hook />;
    case "data": return <S02Data />;
    case "celah": return <S03Celah />;
    case "solusi": return <S04Solusi />;
    case "arsitektur": return <S05Arsitektur dur={dur} />;
    case "pipeline": return <S06Pipeline />;
    case "demo": return <S07Demo />;
    case "audit": return <S08Audit />;
    case "bukti": return <S09Bukti />;
    default: return <S10Penutup />;
  }
};

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const AudioLayer: React.FC = () => (
  <>
    <Audio
      src={staticFile(MUSIC.file)}
      volume={(f) => interpolate(f, [0, MUSIC.fadeIn, MUSIC.total - MUSIC.fadeOut, MUSIC.total], [0, MUSIC.volume, MUSIC.volume, 0], { ...clamp, easing: theme.ease.inOut })}
    />
    {SFX_CUES.map((c, i) => (
      <Sequence key={i} from={c.at} durationInFrames={90} layout="none">
        <Audio src={staticFile(c.file)} volume={c.volume} />
      </Sequence>
    ))}
  </>
);

export const Main: React.FC = () => {
  let t = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: theme.colors.bg, fontFamily: theme.fonts.body }}>
      <style>{"*, *::before, *::after { box-sizing: border-box; }"}</style>
      <BgMesh />
      {SCENES.map((s) => {
        const from = t;
        t += s.dur;
        return (
          <Sequence key={s.id} from={from} durationInFrames={s.dur} name={s.id}>
            <SceneShell dur={s.dur}>{render(s.id, s.dur)}</SceneShell>
          </Sequence>
        );
      })}
      <Grade />
      <Grain />
      <Vignette />
      <AudioLayer />
    </AbsoluteFill>
  );
};
