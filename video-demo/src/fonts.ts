// Memuat font lokal dari public/fonts lewat FontFace + delayRender,
// sehingga frame pertama tidak dirender dengan font bawaan sistem.
import { continueRender, delayRender, staticFile } from "remotion";

const FONTS: Array<[family: string, file: string, weight: string]> = [
  ["Inter Display", "fonts/InterDisplay-Bold.otf", "700"],
  ["Inter Display", "fonts/InterDisplay-SemiBold.otf", "600"],
  ["Inter", "fonts/Inter-Regular.otf", "400"],
  ["Inter", "fonts/Inter-Medium.otf", "500"],
  ["DejaVu Sans Mono", "fonts/DejaVuSansMono.ttf", "400"],
];

let loaded = false;

export const ensureFonts = () => {
  if (loaded || typeof document === "undefined") return;
  loaded = true;
  const handle = delayRender("Memuat font");
  Promise.all(
    FONTS.map(([family, file, weight]) => {
      const face = new FontFace(family, `url('${staticFile(file)}')`, { weight });
      return face.load().then((f) => document.fonts.add(f));
    }),
  )
    .then(() => continueRender(handle))
    .catch((err) => {
      console.error(err);
      continueRender(handle);
    });
};
