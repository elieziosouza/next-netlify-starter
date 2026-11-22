import React from "react";
import { Composition, Still, registerRoot } from "remotion";
import { GuerraParaguai, GuerraParaguaiCapa } from "./GuerraParaguai";
import TM from "./gp.json";
import { Palmares, PalmaresCapa } from "./Palmares";
import TP from "./pal.json";
import { Trincheira3D } from "./Trincheira3D";
import { Canudos, CanudosCapa } from "./Canudos";
import TC from "./can.json";
const Root: React.FC = () => (<>
  <Composition id="GuerraParaguai" component={GuerraParaguai} width={1080} height={1920} fps={TM.fps} durationInFrames={Math.round(TM.total * TM.fps)} />
  <Still id="GuerraParaguaiCapa" component={GuerraParaguaiCapa} width={1080} height={1920} />
  <Composition id="Palmares" component={Palmares} width={1080} height={1920} fps={TP.fps} durationInFrames={Math.round(TP.total * TP.fps)} />
  <Still id="PalmaresCapa" component={PalmaresCapa} width={1080} height={1920} />
  <Composition id="Trinc3DAlto" component={() => <Trincheira3D mode="alto" />} width={1080} height={1920} fps={30} durationInFrames={150} />
  <Composition id="Trinc3DDentro" component={() => <Trincheira3D mode="dentro" />} width={1080} height={1920} fps={30} durationInFrames={150} />
  <Composition id="Canudos" component={Canudos} width={1080} height={1920} fps={TC.fps} durationInFrames={Math.round(TC.total * TC.fps)} />
  <Still id="CanudosCapa" component={CanudosCapa} width={1080} height={1920} />
</>);
registerRoot(Root);
