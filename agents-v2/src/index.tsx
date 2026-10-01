import React, { useEffect, useState } from "react";
import { Composition, Still, continueRender, delayRender, registerRoot } from "remotion";
import "@fontsource/jersey-10/400.css";
import "@fontsource/silkscreen/400.css";
import "@fontsource/archivo-black/400.css";
import "@fontsource/inter/400.css";
import "@fontsource/inter/800.css";
import { AgentsV2, AgentsV2Landscape, FPS, TOTAL_SEC } from "./AgentsV2";
import { Cover } from "./Cover";

/** Hold the first frame until the webfonts are in, so no frame renders with fallback type. */
const withFonts = (C: React.FC): React.FC => () => {
  const [h] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all(["400 80px 'Jersey 10'", "400 20px Silkscreen", "400 80px 'Archivo Black'", "800 60px Inter", "400 20px Inter"].map((f) => document.fonts.load(f)))
      .then(() => document.fonts.ready).then(() => continueRender(h));
  }, [h]);
  return <C />;
};

const Root: React.FC = () => (
  <>
    <Composition id="AgentsV2" component={withFonts(AgentsV2)} width={1080} height={1920} fps={FPS} durationInFrames={Math.ceil(TOTAL_SEC * FPS)} />
    <Composition id="AgentsV2Landscape" component={withFonts(AgentsV2Landscape)} width={1920} height={1080} fps={FPS} durationInFrames={Math.ceil(TOTAL_SEC * FPS)} />
    <Still id="AgentsV2Cover" component={withFonts(Cover)} width={1080} height={1920} />
  </>
);
registerRoot(Root);
