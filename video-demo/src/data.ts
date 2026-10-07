// Semua angka di video berasal dari sumber yang disebut di sini.
// Baris demo & rantai audit = keluaran nyata golden model (hardware-satria/model/golden.py),
// yang bit-exact dengan RTL (regresi 10.000/10.000 transaksi).

export const SOURCES = {
  ppatk2025: "PPATK 2025, via ANTARA 29 Jan 2026",
  ppatkJudol: "Catatan Capaian Strategis PPATK 2025 (GoodStats)",
  ppatkKripto: "Ketua PPATK, via Bisnis.com 7 Feb 2025",
  bssn: "BSSN Jan–Nov 2025, via Investortrust",
  uu: "UU No. 8/2010 Pasal 26; POJK No. 8/2023",
};

export type DemoRow = {
  label: string; verdict: string; reasons: string; cycles: number | "-"; token: string; action: string;
};

// Dihasilkan dari demo_dashboard/app.py (DemoEngine) — lihat scripts/README di proyek.
export const DEMO_ROWS: DemoRow[] = [
  { label: "Transfer sah (klien baru)", verdict: "ACCEPT", reasons: "—", cycles: 750, token: "4a2caa178b2a", action: "Dieksekusi (token valid)" },
  { label: "Transfer sah", verdict: "ACCEPT", reasons: "—", cycles: 411, token: "6ed6970c5e37", action: "Dieksekusi (token valid)" },
  { label: "Transfer ke-6 dalam 30 detik", verdict: "FLAG", reasons: "VELOCITY", cycles: 411, token: "f36f35f4daa8", action: "Dieksekusi + kandidat LTKM" },
  { label: "Nominal Rp250 juta", verdict: "ESCALATE", reasons: "AMOUNT", cycles: 411, token: "a7e8b5c900c4", action: "Ditunda, ditinjau petugas" },
  { label: "Host ubah nominal (Rp480 → 48 jt)", verdict: "REJECT", reasons: "INTEGRITY", cycles: 407, token: "5fc5e58501e1", action: "Ditolak: rekaman diubah" },
  { label: "Host kirim ulang rekaman lama", verdict: "REJECT", reasons: "REPLAY", cycles: 411, token: "e3beb70e5fb3", action: "Ditolak: replay" },
  { label: "Transaksi setelah root ubah aturan", verdict: "REJECT", reasons: "VAULT", cycles: "-", token: "000000000000", action: "Fail-closed (TAMPER, zeroize)" },
];

export const CHAIN: Array<{ seq: number; verdict: string; token: string }> = [
  { seq: 4, verdict: "ACCEPT", token: "2211e85f10" },
  { seq: 5, verdict: "ACCEPT", token: "fd34fe612e" },
  { seq: 6, verdict: "ACCEPT", token: "ed13b04a65" },
  { seq: 7, verdict: "FLAG", token: "f36f35f4da" },
  { seq: 8, verdict: "ESCALATE", token: "a7e8b5c900" },
  { seq: 9, verdict: "REJECT", token: "5fc5e58501" },
];
export const CHAIN_TAMPERED_SEQ = 7; // verify_chain: "rantai putus pada seq 7"

// Durasi adegan (frame @30 fps). Setiap batas = kelipatan 20 frame (1 ketukan pada 90 BPM).
export const SCENES = [
  { id: "hook", dur: 300 },
  { id: "data", dur: 760 },
  { id: "celah", dur: 440 },
  { id: "solusi", dur: 340 },
  { id: "arsitektur", dur: 560 },
  { id: "pipeline", dur: 600 },
  { id: "demo", dur: 960 },
  { id: "audit", dur: 420 },
  { id: "bukti", dur: 580 },
  { id: "penutup", dur: 440 },
] as const;

export const sceneStart = (id: (typeof SCENES)[number]["id"]): number => {
  let t = 0;
  for (const s of SCENES) {
    if (s.id === id) return t;
    t += s.dur;
  }
  throw new Error(id);
};

export const TOTAL_FRAMES = SCENES.reduce((a, s) => a + s.dur, 0); // 5400 = 3 menit
