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
import { Viagem2, Viagem2Capa, Viagem2Capa916 } from "./Viagem2";
import TV2 from "./timings/viagem2.json";
import { Viagem3, Viagem3Capa, Viagem3Capa916 } from "./Viagem3";
import TV3 from "./timings/viagem3.json";
import { Viagem4, Viagem4Capa, Viagem4Capa916 } from "./Viagem4";
import TV4 from "./timings/viagem4.json";
import { Viagem7, Viagem7Capa, Viagem7Capa916 } from "./Viagem7";
import TV7 from "./timings/viagem7.json";
import { Viagem6, Viagem6Capa, Viagem6Capa916 } from "./Viagem6";
import TV6 from "./timings/viagem6.json";
import { Viagem5, Viagem5Capa, Viagem5Capa916 } from "./Viagem5";
import TV5 from "./timings/viagem5.json";

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
    <Composition id="Viagem2" component={Viagem2} width={1920} height={1080} fps={TV2.fps} durationInFrames={Math.round(TV2.total * TV2.fps)} />
    <Still id="Viagem2Capa" component={Viagem2Capa} width={1920} height={1080} />
    <Still id="Viagem2Capa916" component={Viagem2Capa916} width={1080} height={1920} />
    <Composition id="Viagem3" component={Viagem3} width={1920} height={1080} fps={TV3.fps} durationInFrames={Math.round(TV3.total * TV3.fps)} />
    <Still id="Viagem3Capa" component={Viagem3Capa} width={1920} height={1080} />
    <Still id="Viagem3Capa916" component={Viagem3Capa916} width={1080} height={1920} />
    <Composition id="Viagem4" component={Viagem4} width={1920} height={1080} fps={TV4.fps} durationInFrames={Math.round(TV4.total * TV4.fps)} />
    <Still id="Viagem4Capa" component={Viagem4Capa} width={1920} height={1080} />
    <Still id="Viagem4Capa916" component={Viagem4Capa916} width={1080} height={1920} />
    <Composition id="Viagem5" component={Viagem5} width={1920} height={1080} fps={TV5.fps} durationInFrames={Math.round(TV5.total * TV5.fps)} />
    <Still id="Viagem5Capa" component={Viagem5Capa} width={1920} height={1080} />
    <Still id="Viagem5Capa916" component={Viagem5Capa916} width={1080} height={1920} />
    <Composition id="Viagem6" component={Viagem6} width={1920} height={1080} fps={TV6.fps} durationInFrames={Math.round(TV6.total * TV6.fps)} />
    <Still id="Viagem6Capa" component={Viagem6Capa} width={1920} height={1080} />
    <Still id="Viagem6Capa916" component={Viagem6Capa916} width={1080} height={1920} />
    <Composition id="Viagem7" component={Viagem7} width={1920} height={1080} fps={TV7.fps} durationInFrames={Math.round(TV7.total * TV7.fps)} />
    <Still id="Viagem7Capa" component={Viagem7Capa} width={1920} height={1080} />
    <Still id="Viagem7Capa916" component={Viagem7Capa916} width={1080} height={1920} />
  </>
);
registerRoot(Root);
