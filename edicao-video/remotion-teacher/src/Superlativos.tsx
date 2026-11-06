// Aula "Superlativos" (06/11/2026). Tempos: timings/superlativos.json (scripts/prep_aula.py + aulas/aula_superlativos.py).
import React from "react";
import TM from "./timings/superlativos.json";
import { useT, Chip, Box, Outline, Emoji, Center, Pop, Cena, Card, Quiz, Chamada, Licao, CapaBase, QuizItem,
  INK, YEL, MUTED, C_A, C_AN, C_THE, GREY, RED } from "./kit";
const T = TM.t as Record<string, number>;
const W = { font: "400 104px Anton", color: "#fff", ...Outline } as any;

/** linha "🏀 tall → the tall[EST]": o adjetivo entra em `at1` e o superlativo com a terminação em caixa colorida em `at2` */
const Linha: React.FC<{ e: string; one: string; pre?: string; stem: string; end: string; c: string; at1: number; at2: number; y: number; strike?: string; size?: number }> = ({ e, one, pre = "the", stem, end, c, at1, at2, y, strike, size = 104 }) => {
  const { t } = useT();
  return (<Pop at={at1} y={y} dx={250}><div style={{ display: "flex", alignItems: "center", gap: 22, ...W, fontSize: size } as any}>
    <Emoji e={e} size={size * 0.9} />
    <span>{strike && t >= at2 ? <>{one.slice(0, one.lastIndexOf(strike))}<span style={{ color: GREY, textDecoration: "line-through", textDecorationColor: C_THE, textDecorationThickness: 9 }}>{strike}</span></> : one}</span>
    {t >= at2 && <span style={{ display: "inline-flex", alignItems: "center", gap: 22, opacity: Math.min(1, (t - at2) / 0.2) }}>
      <span style={{ color: YEL, fontSize: size * 0.8 }}>→</span><span><span style={{ color: MUTED, fontSize: size * 0.75 }}>{pre} </span>{stem}<Box c={c} size={size} tight>{end}</Box></span></span>}
  </div></Pop>);
};

const Gancho: React.FC = () => (
  <Cena a={0} b={T.short}>
    <Pop at={0.05} y={300}><Chip bg={C_AN} size={38}>BÁSICO · A2</Chip></Pop>
    <Pop at={0.3} y={500}><div style={{ display: "flex", alignItems: "flex-end", gap: 18 }}>
      {[["🧍", 120], ["🧍‍♂️", 160], ["🧍", 220]].map(([e, s], i) => <Emoji key={i} e={e as string} size={s as number} />)}</div></Pop>
    <Pop at={0.9} y={720}><Card w={860}><span style={{ font: "400 96px Anton", color: "#fff" }}>WHO IS <span style={{ color: YEL }}>THE TALLEST</span>?</span></Card></Pop>
    <Pop at={2.24} y={960} from={0.3}><div style={{ font: "400 150px Anton", color: YEL, ...Outline } as any}>SUPERLATIVES</div></Pop>
    <Pop at={4.3} y={1130}><Chip bg="rgba(8,20,48,.92)" size={42} style={{ border: `4px solid ${YEL}` }}>quem é o MAIS de todos</Chip></Pop>
  </Cena>
);
const Curtos: React.FC = () => (
  <Cena a={T.short} b={T.y}>
    <Pop at={T.short + 0.05} y={300}><Chip bg={C_A} size={46}>ADJETIVO CURTO</Chip></Pop>
    <Pop at={T.est} y={500} from={0.3}><div style={{ font: "400 170px Anton", color: "#fff", ...Outline } as any}>THE + <Box c={C_A} size={170}>EST</Box></div></Pop>
    <Linha e="🦒" one="tall" stem="tall" end="est" c={C_A} at1={T.s1} at2={T.s2} y={760} />
    <Linha e="🐆" one="fast" stem="fast" end="est" c={C_A} at1={T.f1} at2={T.f2} y={950} />
  </Cena>
);
const RegraY: React.FC = () => (
  <Cena a={T.y} b={T.long}>
    <Pop at={T.y + 0.05} y={300}><Chip bg={C_THE} size={46}>TERMINOU EM Y · DOBRA A CONSOANTE</Chip></Pop>
    <Pop at={T.y0} y={490} from={0.3}><div style={{ display: "flex", alignItems: "center", gap: 26, font: "400 150px Anton", color: "#fff", ...Outline } as any}>
      <span style={{ color: GREY, textDecoration: "line-through", textDecorationColor: C_THE, textDecorationThickness: 12 }}>Y</span><span style={{ color: YEL }}>→</span><Box c={C_THE} size={150}>IEST</Box></div></Pop>
    <Linha e="😄" one="happy" stem="happ" end="iest" strike="y" c={C_THE} at1={T.y1} at2={T.y2} y={720} size={96} />
    <Linha e="🐘" one="big" stem="big" end="gest" c={C_AN} at1={T.b1} at2={T.b2} y={900} size={96} />
    <Pop at={T.bPt} y={1080}><Chip bg="rgba(8,20,48,.92)" size={40} style={{ border: `4px solid ${YEL}` }}>big → bi<b style={{ color: YEL }}>gg</b>est: dobra o G</Chip></Pop>
  </Cena>
);
const Longos: React.FC = () => (
  <Cena a={T.long} b={T.irr}>
    <Pop at={T.long + 0.05} y={300}><Chip bg={C_AN} size={46}>ADJETIVO LONGO</Chip></Pop>
    <Pop at={T.l0} y={520} from={0.3}><div style={{ font: "400 170px Anton" }}><Box c={C_AN} size={170}>THE MOST</Box></div></Pop>
    <Pop at={T.l1} y={760}><div style={{ display: "flex", alignItems: "center", gap: 22, ...W } as any}><Emoji e="🌸" size={96} /><span>beautiful</span></div></Pop>
    <Pop at={T.l2} y={930}><div style={{ ...W, fontSize: 96 } as any}><span style={{ color: YEL }}>→ </span><Box c={C_AN} size={96} tight>the most</Box> beautiful</div></Pop>
  </Cena>
);
const Irregulares: React.FC = () => { const { t } = useT(); return (
  <Cena a={T.irr} b={T.quiz}>
    <Pop at={T.irr + 0.05} y={300}><Chip bg={RED} size={46}>IRREGULARES: É SÓ DECORAR</Chip></Pop>
    {[["👍", "good", "the best", T.i1, T.i2, 560], ["👎", "bad", "the worst", T.i3, T.i4, 800]].map(([e, a, b, t1, t2, y]) =>
      <Pop key={a as string} at={t1 as number} y={y as number}><Card w={900}><div style={{ display: "flex", alignItems: "center", gap: 24, ...W } as any}>
        <Emoji e={e as string} size={96} /><span>{a}</span><span style={{ color: YEL }}>→</span>{t >= (t2 as number) && <span style={{ opacity: Math.min(1, (t - (t2 as number)) / 0.2) }}><Box c={RED} size={104} tight>{b}</Box></span>}</div></Card></Pop>)}
  </Cena>
); };
const QUIZ: QuizItem[] = [
  { e: "🏔️", before: "the", answer: "highest", opts: [["the most high", false], ["the highest", true]], tip: <>HIGH é curto → the high<b style={{ color: C_A }}>EST</b></> },
  { e: "🎉", before: "the", answer: "best", opts: [["the goodest", false], ["the best", true]], tip: <>GOOD é irregular → <b style={{ color: RED }}>THE BEST</b></> },
];
export const Superlativos: React.FC = () => (
  <Licao tm={TM} hl={{ EST: C_A, IEST: C_THE, MOST: C_AN, BEST: RED, WORST: RED }}>
    <Gancho /><Curtos /><RegraY /><Longos /><Irregulares /><Quiz items={QUIZ} /><Chamada />
  </Licao>
);

export const SuperlativosCapa: React.FC = () => (
  <CapaBase tm={TM} tt={4.5}>
    <Center y={260}><Chip bg={C_AN} size={40}>BÁSICO · A2</Chip></Center>
    <Center y={450}><div style={{ font: "400 160px Anton", color: YEL, ...Outline } as any}>SUPERLATIVES</div></Center>
    <Center y={690}><Card w={820}><span style={{ font: "400 110px Anton", color: "#fff" }}>THE GOODEST?</span></Card></Center>
    <Center y={840}><span style={{ font: "800 56px Montserrat", color: MUTED }}>ou</span></Center>
    <Center y={990}><Card w={820}><span style={{ font: "400 110px Anton", color: "#fff" }}>THE BEST?</span></Card></Center>
    <Center y={1200}><Chip bg={RED} size={46}>VOCÊ ERRA ESSA? · QUIZ</Chip></Center>
  </CapaBase>
);
