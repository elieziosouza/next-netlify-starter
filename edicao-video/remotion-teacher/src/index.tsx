import React from "react";
import { Composition, Still, registerRoot } from "remotion";
import { Artigos, ArtigosCapa, ArtigosCapa2 } from "./Artigos";
import { Plural, PluralCapa } from "./Plural";
import TA from "./timings/artigos.json";
import TP from "./timings/plural.json";

// uma composição por aula (vídeo) e uma still por capa
const Root: React.FC = () => (
  <>
    <Composition id="Artigos" component={Artigos} width={1080} height={1920} fps={TA.fps} durationInFrames={Math.round(TA.total * TA.fps)} />
    <Still id="ArtigosCapa" component={ArtigosCapa} width={1080} height={1920} />
    <Still id="ArtigosCapa2" component={ArtigosCapa2} width={1080} height={1920} />
    <Composition id="Plural" component={Plural} width={1080} height={1920} fps={TP.fps} durationInFrames={Math.round(TP.total * TP.fps)} />
    <Still id="PluralCapa" component={PluralCapa} width={1080} height={1920} />
  </>
);
registerRoot(Root);
