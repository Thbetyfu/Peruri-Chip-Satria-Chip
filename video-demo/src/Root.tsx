import React from "react";
import { Composition } from "remotion";
import { Main } from "./Main";
import { TOTAL_FRAMES } from "./data";
import { theme } from "./theme";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="SatriaDemo"
    component={Main}
    durationInFrames={TOTAL_FRAMES}
    fps={theme.video.fps}
    width={theme.video.width}
    height={theme.video.height}
  />
);
