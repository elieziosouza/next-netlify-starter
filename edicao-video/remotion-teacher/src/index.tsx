import React from "react";
import { Composition, Still, registerRoot } from "remotion";
import { Aula, Capa } from "./Aula";
import T from "./timings.json";

const Root: React.FC = () => (
  <>
    <Composition id="Aula" component={Aula} width={1080} height={1920} fps={T.fps} durationInFrames={Math.round(T.total * T.fps)} />
    <Still id="Capa" component={Capa} width={1080} height={1920} />
  </>
);
registerRoot(Root);
