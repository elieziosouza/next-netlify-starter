import React from "react";
import { Composition, Still, registerRoot } from "remotion";
import { GuerraParaguai, GuerraParaguaiCapa } from "./GuerraParaguai";
import TM from "./gp.json";
const Root: React.FC = () => (<>
  <Composition id="GuerraParaguai" component={GuerraParaguai} width={1080} height={1920} fps={TM.fps} durationInFrames={Math.round(TM.total * TM.fps)} />
  <Still id="GuerraParaguaiCapa" component={GuerraParaguaiCapa} width={1080} height={1920} />
</>);
registerRoot(Root);
