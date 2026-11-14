// Aula "For × Since" (14/11/2026, B1). Tempos: timings/forsince.json (scripts/prep_aula.py + aulas/aula_forsince.py).
// Linha do tempo: FOR = barra de duração com colchetes; SINCE = ponto de partida que corre até o AGORA. Ícones 3D (Canva) no quiz.
import React from "react";
import TM from "./timings/forsince.json";
import { useT, Chip, Box, Outline, Emoji, Center, Pop, Cena, Card, Quiz, Chamada, Licao, CapaBase, QuizItem,
  INK, YEL, MUTED, C_A, C_AN, RED, clamp } from "./kit";
import { At, Barra, Trilho, Pin, TLY, XNOW, C_B1, W } from "./PPSP";
const T = TM.t as Record<string, number>;
const C_FOR = C_A, C_SINCE = C_AN;

/** colchete vertical (marca o começo e o fim de uma duração) */
const Colchete: React.FC<{ x: number; at: number; c: string }> = ({ x, at, c }) => {
  const { t } = useT(); const k = clamp((t - at) / 0.25); if (k <= 0) return null;
  return <div style={{ position: "absolute", left: x - 5, top: TLY - 50 * k, width: 10, height: 100 * k, borderRadius: 5, background: c, boxShadow: `0 0 24px ${c}` }} />;
};
const Ex: React.FC<{ at: number; y: number; kw: string; rest: string; c: string }> = ({ at, y, kw, rest, c }) => (
  <At at={at} x={540} y={y}><Chip bg="#fff" color={INK} size={50}><b style={{ color: c, textTransform: "lowercase" }}>{kw}</b>&nbsp;{rest}</Chip></At>
);

const Gancho: React.FC = () => (
  <Cena a={0} b={T.pp}>
    <Pop at={0.1} y={300}><Chip bg={C_B1} color={INK} size={38}>INTERMEDIÁRIO · B1</Chip></Pop>
    <Pop at={1.69} y={560} from={0.3}><div style={{ font: "400 220px Anton", color: "#fff", ...Outline, background: "none" } as any}><Box c={C_FOR} size={200} tight>FOR</Box></div></Pop>
    <Pop at={2.35} y={790}><Chip bg="#fff" color={INK} size={46}>VERSUS</Chip></Pop>
    <Pop at={2.95} y={1010} from={0.3}><div style={{ font: "400 220px Anton" } as any}><Box c={C_SINCE} size={200} tight>SINCE</Box></div></Pop>
  </Cena>
);
const Mistura: React.FC = () => {
  const { t } = useT(); const alt = Math.floor((t - T.pp) / 0.55) % 2 === 0;
  return (
    <Cena a={T.pp} b={T.fo}>
      <Pop at={T.pp + 0.05} y={290}><Chip bg={C_A} size={46}>PRESENT PERFECT</Chip></Pop>
      <Pop at={T.pp + 0.4} y={560}><Card w={900}><span style={{ font: "400 80px Anton", color: "#fff" }}>I HAVE LIVED HERE <Box c={alt ? C_FOR : C_SINCE} size={80} tight>{alt ? "FOR" : "SINCE"}</Box> ...</span></Card></Pop>
      <Pop at={T.pp + 1.5} y={820} from={0.3}><Emoji e="🤔" size={170} /></Pop>
      <Pop at={T.pp + 2.3} y={1020}><Chip bg="rgba(8,20,48,.92)" size={42} style={{ border: `4px solid ${YEL}` }}>todo mundo mistura as duas</Chip></Pop>
    </Cena>
  );
};
const For: React.FC = () => (
  <Cena a={T.fo} b={T.si}>
    <Pop at={T.fo + 0.05} y={290}><Chip bg={C_FOR} size={46}>FOR</Chip></Pop>
    <Pop at={T.fo + 0.4} y={410} from={0.3}><div style={{ ...W, fontSize: 104 } as any}>QUANTO <Box c={C_FOR} size={104} tight>TEMPO</Box></div></Pop>
    <Trilho at={T.fo + 0.3} />
    <Colchete x={300} at={T.fo + 1.0} c={C_FOR} />
    <Barra x0={300} x1={700} at={T.fo + 1.1} c={C_FOR} h={34} dur={0.7} glow />
    <Colchete x={700} at={T.fo + 1.7} c={C_FOR} />
    <At at={T.fo + 1.9} x={500} y={TLY - 95} from={0.4}><Chip bg="#fff" color={INK} size={38}>duração</Chip></At>
    <Ex at={T.fo1} y={950} kw="for" rest="two years" c={C_FOR} />
    <Ex at={T.fo2} y={1045} kw="for" rest="ten minutes" c={C_FOR} />
    <Ex at={T.fo3} y={1140} kw="for" rest="a long time" c={C_FOR} />
  </Cena>
);
const Since: React.FC = () => (
  <Cena a={T.si} b={T.cmp}>
    <Pop at={T.si + 0.05} y={290}><Chip bg={C_SINCE} size={46}>SINCE</Chip></Pop>
    <Pop at={T.si + 0.4} y={410} from={0.3}><div style={{ ...W, fontSize: 104 } as any}>DESDE <Box c={C_SINCE} size={104} tight>QUANDO</Box></div></Pop>
    <Trilho at={T.si + 0.3} />
    <Barra x0={430} x1={XNOW} at={T.si1} c={C_SINCE} h={34} dur={0.8} glow />
    <Pin at={T.si1} x={430} label="2020" up c={C_SINCE} />
    <Barra x0={730} x1={XNOW} at={T.si2} c={C_SINCE} h={34} dur={0.5} glow />
    <Pin at={T.si2} x={730} label="Monday" up c={C_SINCE} />
    <Barra x0={170} x1={XNOW} at={T.si3} c={C_SINCE} h={34} dur={0.9} glow />
    <Pin at={T.si3} x={170} label="I was a kid" up c={C_SINCE} />
    <Ex at={T.si1} y={950} kw="since" rest="2020" c={C_SINCE} />
    <Ex at={T.si2} y={1045} kw="since" rest="Monday" c={C_SINCE} />
    <Ex at={T.si3} y={1140} kw="since" rest="I was a kid" c={C_SINCE} />
  </Cena>
);
const Mesma: React.FC = () => (
  <Cena a={T.cmp} b={T.quiz}>
    <Pop at={T.cmp + 0.05} y={290}><Chip bg={YEL} color={INK} size={46}>MESMA IDEIA</Chip></Pop>
    <At at={T.cmp + 0.2} x={540} y={470}><Card w={960} border={C_FOR}><span style={{ font: "400 62px Anton", color: "#fff" }}>I HAVE LIVED HERE <Box c={C_FOR} size={62} tight>FOR</Box> FIVE YEARS</span></Card></At>
    <At at={T.cmp + 1.2} x={540} y={575}><Chip bg={C_FOR} size={38}>FOR = quanto tempo</Chip></At>
    <At at={T.cmp2} x={540} y={760}><Card w={960} border={C_SINCE}><span style={{ font: "400 62px Anton", color: "#fff" }}>I HAVE LIVED HERE <Box c={C_SINCE} size={62} tight>SINCE</Box> 2020</span></Card></At>
    <At at={T.cmp2 + 0.9} x={540} y={865}><Chip bg={C_SINCE} size={38}>SINCE = desde quando</Chip></At>
    <Pop at={T.cmpPt} y={1020}><Chip bg="rgba(8,20,48,.92)" size={42} style={{ border: `4px solid ${YEL}` }}>mesma ideia, dois jeitos</Chip></Pop>
  </Cena>
);
const QUIZ: QuizItem[] = [
  { e: "ic/briefcase.png", before: "I have worked here", answer: "for", after: "three years", fs: 54,
    opts: [["for", true], ["since", false]],
    tip: <>THREE YEARS = quanto tempo → <b style={{ color: C_FOR }}>FOR</b></> },
  { e: "ic/book.png", before: "I have studied English", answer: "since", after: "2023", fs: 54,
    opts: [["for", false], ["since", true]],
    tip: <>2023 = quando começou → <b style={{ color: C_SINCE }}>SINCE</b></> },
];
export const ForSince: React.FC = () => (
  <Licao tm={TM} hl={{}}>
    <Gancho /><Mistura /><For /><Since /><Mesma /><Quiz items={QUIZ} /><Chamada />
  </Licao>
);
export const ForSinceCapa: React.FC = () => (
  <CapaBase tm={TM} tt={4.5}>
    <Center y={260}><Chip bg={C_B1} color={INK} size={40}>INTERMEDIÁRIO · B1</Chip></Center>
    <Center y={470}><div style={{ font: "400 220px Anton" }}><Box c={C_FOR} size={200} tight>FOR</Box></div></Center>
    <Center y={650}><span style={{ font: "800 54px Montserrat", color: MUTED }}>ou</span></Center>
    <Center y={840}><div style={{ font: "400 220px Anton" }}><Box c={C_SINCE} size={200} tight>SINCE</Box></div></Center>
    <Center y={1080}><Card w={900}><span style={{ font: "400 74px Anton", color: "#fff" }}>I HAVE LIVED HERE ____ 2020</span></Card></Center>
    <Center y={1270}><Chip bg={RED} size={46}>QUAL USAR? · QUIZ</Chip></Center>
  </CapaBase>
);
