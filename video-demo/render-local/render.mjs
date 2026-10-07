// Render lokal tanpa npm: esbuild (bundel) → Chromium/Playwright (frame) → ffmpeg (encode + mix audio).
// Pemakaian:
//   node render-local/render.mjs --stills 15,300,2400        # frame tunggal ke out/check_<f>.png
//   node render-local/render.mjs --video [--workers 4]       # out/satria-chip-demo.mp4
import { spawn, execFileSync } from "node:child_process";
import { mkdirSync, writeFileSync, existsSync, rmSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..");
const DIST = join(HERE, "dist");
const OUT = join(ROOT, "out");
mkdirSync(DIST, { recursive: true });
mkdirSync(OUT, { recursive: true });

const GLOBAL = execFileSync("npm", ["root", "-g"]).toString().trim();
const esbuild = require(process.env.ESBUILD_PATH || "/opt/npm-tools/node_modules/esbuild");
const { chromium } = require(join(GLOBAL, "playwright"));

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };

// ------------------------------------------------------------------ bundel
await esbuild.build({
  entryPoints: [join(HERE, "entry.tsx")],
  bundle: true, outfile: join(DIST, "bundle.js"), format: "iife", jsx: "automatic",
  alias: { remotion: join(HERE, "remotion-shim.tsx") },
  nodePaths: [GLOBAL], define: { "process.env.NODE_ENV": '"production"' }, logLevel: "warning",
});
// bundel kedua: daftar isyarat audio untuk mixing
await esbuild.build({
  entryPoints: [join(ROOT, "src", "audio.ts")], bundle: true, platform: "node", format: "esm",
  outfile: join(DIST, "audio.mjs"), logLevel: "warning",
  alias: { remotion: join(HERE, "remotion-shim.tsx") }, nodePaths: [GLOBAL],
});
writeFileSync(join(DIST, "index.html"), `<!doctype html><html><head><meta charset="utf-8">
<base href="${pathToFileURL(ROOT + "/").href}">
<style>html,body{margin:0;padding:0;background:#060A14;width:1920px;height:1080px;overflow:hidden}
#root{position:relative;width:1920px;height:1080px;overflow:hidden}</style></head>
<body><div id="root"></div><script src="${pathToFileURL(join(DIST, "bundle.js")).href}"></script></body></html>`);

const FPS = 30;

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on("pageerror", (e) => console.error("pageerror:", e.message));
  await page.goto(pathToFileURL(join(DIST, "index.html")).href);
  await page.waitForFunction(() => typeof window.__setFrame === "function" && (window.__pendingRenders || 0) === 0, null, { timeout: 60000 });
  await page.evaluate(() => document.fonts.ready);
  return page;
}

async function renderFrame(page, f) {
  await page.evaluate(async (fr) => {
    window.__setFrame(fr);
    const imgs = Array.from(document.images);
    await Promise.all(imgs.map((im) => (im.complete ? (im.decode ? im.decode().catch(() => {}) : null) : new Promise((r) => { im.onload = r; im.onerror = r; }))));
  }, f);
}

const browser = await chromium.launch({ args: ["--disable-web-security", "--allow-file-access-from-files"] });

if (args.includes("--stills")) {
  const frames = opt("--stills", "0").split(",").map(Number);
  const page = await openPage(browser);
  for (const f of frames) {
    await renderFrame(page, f);
    await page.screenshot({ path: join(OUT, `check_${f}.png`) });
    console.log("still", f);
  }
  await browser.close();
  process.exit(0);
}

// ------------------------------------------------------------------ video
const AUDIO_ONLY = args.includes("--audio-only");
const total = await (await openPage(browser)).evaluate(() => window.__total);
const workers = Number(opt("--workers", "4"));
const limit = Number(opt("--frames", String(total)));
const chunk = Math.ceil(limit / workers);
const parts = [];

if (!AUDIO_ONLY) await Promise.all(Array.from({ length: workers }).map(async (_, w) => {
  const start = w * chunk;
  const end = Math.min(limit, start + chunk);
  if (start >= end) return;
  const part = join(OUT, `part_${w}.mp4`);
  parts[w] = part;
  const ff = spawn("ffmpeg", ["-y", "-v", "error", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
    "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-r", String(FPS), part], { stdio: ["pipe", "inherit", "inherit"] });
  const page = await openPage(browser);
  for (let f = start; f < end; f++) {
    await renderFrame(page, f);
    const buf = await page.screenshot({ type: "jpeg", quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
    if ((f - start) % 300 === 0) console.log(`worker ${w}: frame ${f} / ${end - 1}`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on("close", r));
  await page.close();
}));
await browser.close();

const list = join(OUT, "parts.txt");
const silent = join(OUT, "video_silent.mp4");
if (AUDIO_ONLY) {
  execFileSync("ffmpeg", ["-y", "-v", "error", "-i", join(OUT, opt("--out", "satria-chip-demo.mp4")), "-map", "0:v", "-c", "copy", silent]);
} else {
  writeFileSync(list, parts.filter(Boolean).map((p) => `file '${p}'`).join("\n"));
  execFileSync("ffmpeg", ["-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", list, "-c", "copy", silent]);
}

// ------------------------------------------------------------------ audio
const { SFX_CUES, MUSIC } = await import(pathToFileURL(join(DIST, "audio.mjs")).href);
const durS = limit / FPS;
const inputs = ["-i", join(ROOT, "public", MUSIC.file)];
const filters = [];
filters.push(`[0:a]atrim=0:${durS},volume=${MUSIC.volume},afade=t=in:st=0:d=${MUSIC.fadeIn / FPS},afade=t=out:st=${Math.max(0, durS - MUSIC.fadeOut / FPS)}:d=${MUSIC.fadeOut / FPS}[m]`);
const cues = SFX_CUES.filter((c) => c.at < limit);
cues.forEach((c, i) => {
  inputs.push("-i", join(ROOT, "public", c.file));
  const ms = Math.round((c.at / FPS) * 1000);
  filters.push(`[${i + 1}:a]adelay=${ms}|${ms},volume=${c.volume}[s${i}]`);
});
filters.push(`[m]${cues.map((_, i) => `[s${i}]`).join("")}amix=inputs=${cues.length + 1}:normalize=0:duration=first,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[aout]`);
const mixed = join(OUT, "audio_mix.m4a");
execFileSync("ffmpeg", ["-y", "-v", "error", ...inputs, "-filter_complex", filters.join(";"), "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-t", String(durS), mixed]);

const final = join(OUT, opt("--out", "satria-chip-demo.mp4"));
execFileSync("ffmpeg", ["-y", "-v", "error", "-i", silent, "-i", mixed, "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", final]);
for (const p of [...parts.filter(Boolean), list, silent, mixed]) if (existsSync(p)) rmSync(p);
console.log("selesai:", final);
