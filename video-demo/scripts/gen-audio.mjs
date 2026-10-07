// Mensintesis musik latar (3 menit, 90 BPM) dan kit SFX sebagai WAV 16-bit — tanpa aset eksternal.
// Deterministik: memakai PRNG ber-seed, sehingga setiap render menghasilkan audio yang sama.
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const SR = 44100;
const OUT = join(dirname(fileURLToPath(import.meta.url)), "..", "public", "audio");
mkdirSync(OUT, { recursive: true });

let seed = 20261007;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296) * 2 - 1;

function wav(L, R = L) {
  const n = L.length;
  const buf = Buffer.alloc(44 + n * 4);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + n * 4, 4); buf.write("WAVE", 8); buf.write("fmt ", 12);
  buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22); buf.writeUInt32LE(SR, 24);
  buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write("data", 36);
  buf.writeUInt32LE(n * 4, 40);
  for (let i = 0; i < n; i++) {
    buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, L[i])) * 32767), 44 + i * 4);
    buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, R[i])) * 32767), 46 + i * 4);
  }
  return buf;
}
const secs = (s) => Math.round(s * SR);
const save = (name, L, R) => writeFileSync(join(OUT, name), wav(L, R));

// ---------------------------------------------------------------- SFX
{ // whoosh: noise ber-lowpass yang menyapu
  const N = secs(0.45), L = new Float32Array(N), R = new Float32Array(N);
  let a = 0, b = 0;
  for (let i = 0; i < N; i++) {
    const t = i / N, env = Math.sin(Math.PI * Math.pow(t, 0.65)) ** 2, c = 0.04 + 0.22 * Math.sin(Math.PI * t);
    a += c * (rnd() - a); b += c * (rnd() - b);
    L[i] = a * env * 0.9; R[i] = b * env * 0.9;
  }
  save("whoosh.wav", L, R);
}
{ // pop: sinus dengan pitch turun
  const N = secs(0.14), L = new Float32Array(N); let ph = 0;
  for (let i = 0; i < N; i++) { const t = i / N; ph += (2 * Math.PI * (720 - 400 * t)) / SR; L[i] = Math.sin(ph) * Math.exp(-t * 9) * 0.7; }
  save("pop.wav", L);
}
{ // hit: transien + nada rendah (untuk peringatan/serangan)
  const N = secs(0.35), L = new Float32Array(N); let ph = 0;
  for (let i = 0; i < N; i++) {
    const t = i / N; ph += (2 * Math.PI * (180 - 90 * t)) / SR;
    L[i] = (Math.sin(ph) * 0.7 + rnd() * 0.25 * Math.exp(-t * 40)) * Math.exp(-t * 7) * 0.8;
  }
  save("hit.wav", L);
}
{ // bass: thump sinus rendah
  const N = secs(0.7), L = new Float32Array(N); let ph = 0;
  for (let i = 0; i < N; i++) { const t = i / N; ph += (2 * Math.PI * (70 - 30 * t)) / SR; L[i] = Math.sin(ph) * Math.exp(-t * 5) * 0.95; }
  save("bass.wav", L);
}
{ // shimmer: arpeggio sinus halus
  const N = secs(1.1), L = new Float32Array(N), R = new Float32Array(N);
  const notes = [880, 1108.73, 1318.51, 1760];
  for (let i = 0; i < N; i++) {
    const t = i / SR; let s = 0;
    notes.forEach((f, k) => { const st = k * 0.09; if (t > st) s += Math.sin(2 * Math.PI * f * (t - st)) * Math.exp(-(t - st) * 3.2) * 0.18; });
    L[i] = s; R[i] = s * 0.9;
  }
  save("shimmer.wav", L, R);
}
{ // riser: noise + nada naik
  const N = secs(1.6), L = new Float32Array(N); let ph = 0, lp = 0;
  for (let i = 0; i < N; i++) {
    const t = i / N; ph += (2 * Math.PI * (200 + 600 * t * t)) / SR; lp += (0.02 + 0.3 * t) * (rnd() - lp);
    L[i] = (Math.sin(ph) * 0.25 + lp * 0.5) * t * t * 0.8;
  }
  save("riser.wav", L);
}

// ---------------------------------------------------------------- musik latar
{
  const BPM = 90, beat = 60 / BPM, DUR = 180, N = secs(DUR);
  const L = new Float32Array(N), R = new Float32Array(N);
  const midi = (m) => 440 * Math.pow(2, (m - 69) / 12);
  // progresi minor tenang: Am – F – C – G (masing-masing 4 ketukan)
  const chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]];
  const bassN = [45, 41, 48, 43];
  const bar = 4 * beat;
  for (let i = 0; i < N; i++) {
    const t = i / SR;
    const bi = Math.floor(t / bar) % 4;
    const tb = t % bar;
    // pad: sinus berlapis sedikit detune + swell per bar
    const sw = Math.min(1, tb / 0.8) * Math.min(1, (bar - tb) / 0.6);
    let pl = 0, pr = 0;
    for (const m of chords[bi]) {
      const f = midi(m);
      pl += Math.sin(2 * Math.PI * f * t) + 0.5 * Math.sin(2 * Math.PI * f * 1.003 * t);
      pr += Math.sin(2 * Math.PI * f * 0.997 * t) + 0.5 * Math.sin(2 * Math.PI * f * 2 * t) * 0.3;
    }
    pl *= 0.045 * sw; pr *= 0.045 * sw;
    // bass lembut tiap ketukan 1 & 3
    const tbeat = t % (2 * beat);
    const bassEnv = Math.exp(-tbeat * 3.5);
    const bs = Math.sin(2 * Math.PI * midi(bassN[bi]) * t) * bassEnv * 0.16;
    // pulse halus (kick) mulai bar ke-3, berhenti 6 detik sebelum akhir
    const tk = t % beat;
    const kOn = t > 2 * bar && t < DUR - 6 ? 1 : 0;
    const kick = Math.sin(2 * Math.PI * (55 + 60 * Math.exp(-tk * 30)) * tk) * Math.exp(-tk * 12) * 0.22 * kOn;
    // pluck arpeggio per setengah ketukan
    const half = beat / 2, th = t % half, idx = Math.floor(t / half) % 3;
    const pf = midi(chords[bi][idx] + 12);
    const pluck = Math.sin(2 * Math.PI * pf * th) * Math.exp(-th * 9) * 0.05 * (t > bar ? 1 : 0);
    L[i] = pl + bs + kick + pluck * 0.9;
    R[i] = pr + bs + kick + pluck * 1.1;
  }
  // normalisasi ke -3 dBFS
  let peak = 0; for (let i = 0; i < N; i++) peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
  const g = 0.7 / peak; for (let i = 0; i < N; i++) { L[i] *= g; R[i] *= g; }
  save("music.wav", L, R);
}
console.log("audio ->", OUT);
