// Daftar isyarat audio (satu sumber kebenaran). Dipakai oleh <AudioLayer/> di Remotion
// dan oleh render-local/render.mjs untuk mixing ffmpeg. SFX dimulai 3 frame sebelum visual mendarat.
import { SCENES, TOTAL_FRAMES, sceneStart } from "./data";

export type Cue = { at: number; file: string; volume: number };

const ROW_FIRST = 100; // sama dengan S07Demo
const ROW_STEP = 115;
const LEAD = 3;

const cues: Cue[] = [];
const add = (at: number, file: string, volume: number) => cues.push({ at: Math.max(0, at - LEAD), file, volume });

// whoosh di setiap pergantian adegan
SCENES.forEach((s, i) => { if (i > 0) add(sceneStart(s.id), "audio/whoosh.wav", 0.32); });
// hook
add(8, "audio/shimmer.wav", 0.32);
add(166, "audio/whoosh.wav", 0.26);
// data: 4 kartu
[0, 1, 2, 3].forEach((i) => add(sceneStart("data") + 60 + i * 30, "audio/pop.wav", 0.4));
add(sceneStart("data") + 420, "audio/pop.wav", 0.4);
// celah: tiga serangan
[150, 205, 260].forEach((t) => add(sceneStart("celah") + t, "audio/hit.wav", 0.45));
// solusi
add(sceneStart("solusi") + 6, "audio/bass.wav", 0.6);
// pipeline: titik berjalan + bar
add(sceneStart("pipeline") + 190, "audio/riser.wav", 0.28);
add(sceneStart("pipeline") + 360, "audio/pop.wav", 0.36);
// demo: setiap baris
for (let i = 0; i < 7; i++) add(sceneStart("demo") + ROW_FIRST + i * ROW_STEP, i >= 4 ? "audio/hit.wav" : "audio/pop.wav", i >= 4 ? 0.42 : 0.38);
// audit: manipulasi & rantai putus
add(sceneStart("audit") + 190, "audio/hit.wav", 0.42);
add(sceneStart("audit") + 225, "audio/bass.wav", 0.55);
// bukti: kartu hero
add(sceneStart("bukti") + 70, "audio/shimmer.wav", 0.3);
// penutup
add(sceneStart("penutup") + 230, "audio/bass.wav", 0.55);

export const SFX_CUES: Cue[] = cues;
export const MUSIC = { file: "audio/music.wav", volume: 0.42, fadeIn: 45, fadeOut: 90, total: TOTAL_FRAMES };
