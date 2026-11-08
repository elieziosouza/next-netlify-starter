import React from "react";
import { Composition, Still, registerRoot } from "remotion";
import { Artigos, ArtigosCapa, ArtigosCapa2 } from "./Artigos";
import { Plural, PluralCapa } from "./Plural";
import TA from "./timings/artigos.json";
import TP from "./timings/plural.json";
import { Quiz7, Quiz7Capa } from "./Quiz7";
import TQ from "./timings/quiz7.json";
import { SimplePast, ExplicacaoStill, LicaoStill, SimplePastCapa } from "./SimplePast";
import TS from "./timings/simplepast.json";
import { Superlativos, SuperlativosCapa } from "./Superlativos";
import TSU from "./timings/superlativos.json";
import { WasWere, WasWereCapa } from "./WasWere";
import TWW from "./timings/waswere.json";
import { Viagem1, Viagem1Capa, Viagem1Capa916, CursoQuadrado, CursoCheckout, CursoModulo } from "./Viagem1";
import TV1 from "./timings/viagem1.json";

// uma composição por aula (vídeo) e uma still por capa
const Root: React.FC = () => (
  <>
    <Composition id="Artigos" component={Artigos} width={1080} height={1920} fps={TA.fps} durationInFrames={Math.round(TA.total * TA.fps)} />
    <Still id="ArtigosCapa" component={ArtigosCapa} width={1080} height={1920} />
    <Still id="ArtigosCapa2" component={ArtigosCapa2} width={1080} height={1920} />
    <Composition id="Plural" component={Plural} width={1080} height={1920} fps={TP.fps} durationInFrames={Math.round(TP.total * TP.fps)} />
    <Still id="PluralCapa" component={PluralCapa} width={1080} height={1920} />
    <Composition id="Quiz7" component={Quiz7} width={1080} height={1920} fps={TQ.fps} durationInFrames={Math.round(TQ.total * TQ.fps)} />
    <Still id="Quiz7Capa" component={Quiz7Capa} width={1080} height={1920} />
    <Composition id="SimplePast" component={SimplePast} width={1920} height={1080} fps={TS.fps} durationInFrames={Math.round(TS.total * TS.fps)} />
    <Still id="SimplePastExplicacao" component={ExplicacaoStill} width={1920} height={1080} />
    <Still id="SimplePastLicao" component={LicaoStill} width={1920} height={1080} />
    <Still id="SimplePastCapa" component={SimplePastCapa} width={1920} height={1080} />
    <Composition id="Superlativos" component={Superlativos} width={1080} height={1920} fps={TSU.fps} durationInFrames={Math.round(TSU.total * TSU.fps)} />
    <Still id="SuperlativosCapa" component={SuperlativosCapa} width={1080} height={1920} />
    <Composition id="WasWere" component={WasWere} width={1080} height={1920} fps={TWW.fps} durationInFrames={Math.round(TWW.total * TWW.fps)} />
    <Still id="WasWereCapa" component={WasWereCapa} width={1080} height={1920} />
    <Composition id="Viagem1" component={Viagem1} width={1920} height={1080} fps={TV1.fps} durationInFrames={Math.round(TV1.total * TV1.fps)} />
    <Still id="Viagem1Capa" component={Viagem1Capa} width={1920} height={1080} />
    <Still id="Viagem1Capa916" component={Viagem1Capa916} width={1080} height={1920} />
    <Still id="CursoQuadrado" component={CursoQuadrado} width={1080} height={1080} />
    <Still id="CursoCheckout" component={CursoCheckout} width={1920} height={480} />
    <Still id="CursoModulo" component={CursoModulo} width={1000} height={1500} />
  </>
);
registerRoot(Root);
