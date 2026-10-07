// Titik masuk bundel render lokal: merender <Main/> untuk frame tertentu atas perintah render.mjs.
import React from "react";
import { createRoot } from "react-dom/client";
import { flushSync } from "react-dom";
import { __CfgCtx, __FrameCtx } from "remotion";
import { Main } from "../src/Main";
import { TOTAL_FRAMES } from "../src/data";
import { theme } from "../src/theme";

const cfg = { fps: theme.video.fps, width: theme.video.width, height: theme.video.height, durationInFrames: TOTAL_FRAMES, id: "SatriaDemo" };
const root = createRoot(document.getElementById("root")!);

declare global { interface Window { __setFrame: (f: number) => void; __total: number } }
window.__total = TOTAL_FRAMES;
window.__setFrame = (f: number) => {
  flushSync(() => {
    root.render(
      <__CfgCtx.Provider value={cfg}>
        <__FrameCtx.Provider value={f}>
          <Main />
        </__FrameCtx.Provider>
      </__CfgCtx.Provider>,
    );
  });
};
window.__setFrame(0);
