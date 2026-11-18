// Aula "Cores e adjetivos" (s7-a1, 18/11/2026). Tempos: timings/cores.json (scripts/prep_aula.py + aulas/aula_cores.py).
import React from "react";
import TM from "./timings/cores.json";
import { useT, Chip, Box, Outline, Emoji, Center, Pop, Cena, Card, Quiz, Chamada, Licao, CapaBase, QuizItem,
  INK, YEL, MUTED, C_A, C_AN, C_THE, GREY, RED, PT } from "./kit";
const T = TM.t as Record<string, number>;
const W = { font: "400 112px Anton", color: "#fff", ...Outline } as any;

/** "a [red] car": adjetivo em caixa azul, substantivo em caixa verde */
const Frase: React.FC<{ e: string; art: string; adj: string; noun: string; at: number; y: number; size?: number; artC?: string }> = ({ e, art, adj, noun, at, y, size = 100, artC }) => (
  <Pop at={at} y={y} dx={260}><div style={{ display: "flex", alignItems: "center", gap: 22, ...W, fontSize: size } as any}>
    <Emoji e={e} size={size * 0.95} />
    {artC ? <Box c={artC} size={size} tight>{art}</Box> : <span>{art}</span>}
    <Box c={C_A} size={size} tight>{adj}</Box><Box c={C_AN} size={size} tight>{noun}</Box>
  </div></Pop>
);

const Gancho: React.FC = () => {
  const { t } = useT();
  const wob = t > T.care ? 5 * Math.sin((t - T.care) * 18) * Math.exp(-(t - T.care) * 2) : 0;
  return (<Cena a={0} b={T.cor - 0.1}>
    <Pop at={0.05} y={265}><Chip bg={C_AN} size={38}>BÁSICO · A1</Chip></Pop>
    <Pop at={T.tit} y={500} from={0.3}><div style={{ font: "400 170px Anton", color: YEL, ...Outline, textAlign: "center", lineHeight: 0.95 } as any}>COLORS<br /><span style={{ fontSize: 110, color: "#fff" }}>& ADJECTIVES</span></div></Pop>
    <Pop at={T.car1} y={800}><Card w={780}><span style={{ font: "400 100px Anton", color: "#fff" }}>A CAR RED?</span></Card></Pop>
    <Pop at={T.car2} y={990}><div style={{ transform: `rotate(${wob}deg)` }}><Card w={780} border={t > T.care ? C_THE : undefined}><span style={{ font: "400 100px Anton", color: "#fff" }}>A RED CAR?</span></Card></div></Pop>
    <Pop at={T.care} y={1140}><Chip bg={RED} size={50}><Emoji e="⚠️" size={48} style={{ marginRight: 14, verticalAlign: -6 }} />CUIDADO!</Chip></Pop>
  </Cena>);
};

const CORES: { en: string; pt: string; c: string; ink?: string; k: string; kp: string }[] = [
  { en: "RED", pt: "vermelho", c: "#e53935", k: "c0", kp: "p0" }, { en: "BLUE", pt: "azul", c: "#1e88e5", k: "c1", kp: "p1" }, { en: "GREEN", pt: "verde", c: "#43a047", k: "c2", kp: "p2" },
  { en: "YELLOW", pt: "amarelo", c: "#fdd835", k: "c3", kp: "p3" }, { en: "BLACK", pt: "preto", c: "#222a38", k: "c4", kp: "p4" }, { en: "WHITE", pt: "branco", c: "#f6f8fc", k: "c5", kp: "p5" },
];
const Cores: React.FC = () => {
  const { t } = useT();
  return (<Cena a={T.cor} b={T.r1 - 0.1}>
    <Pop at={T.cor + 0.05} y={300}><Chip bg={YEL} color={INK} size={46}>AS CORES · COLORS</Chip></Pop>
    {CORES.map((c, i) => { const at = T[c.k], x = 540 + ((i % 3) - 1) * 300, y = 560 + Math.floor(i / 3) * 390;
      return (<React.Fragment key={c.en}>
        <Pop at={at} y={y}><div style={{ transform: `translateX(${(x - 540)}px)`, display: "grid", justifyItems: "center", gap: 10 }}>
          <div style={{ width: 190, height: 190, borderRadius: "50%", background: `radial-gradient(circle at 32% 28%, rgba(255,255,255,.55), ${c.c} 55%)`, border: "6px solid rgba(255,255,255,.85)", boxShadow: `0 16px 30px rgba(0,0,0,.4), 0 0 40px ${c.c}66` }} />
          <span style={{ font: "400 66px Anton", color: "#fff", ...Outline } as any}>{c.en}</span>
          {t >= T[c.kp] && <span style={{ font: "800 38px Montserrat", color: PT, opacity: Math.min(1, (t - T[c.kp]) / 0.2) }}>{c.pt}</span>}
        </div></Pop></React.Fragment>); })}
  </Cena>);
};

const Regra1: React.FC = () => (
  <Cena a={T.r1} b={T.r2 - 0.1}>
    <Pop at={T.r1 + 0.05} y={300}><Chip bg={C_A} size={46}>REGRA 1</Chip></Pop>
    <Pop at={T.r1h} y={480} from={0.3}><div style={{ display: "flex", alignItems: "center", gap: 22, font: "400 90px Anton", color: "#fff", ...Outline } as any}>
      <Box c={C_A} size={90} tight>ADJETIVO</Box><span style={{ color: YEL }}>+</span><Box c={C_AN} size={90} tight>NOME</Box></div></Pop>
    <Frase e="🚗" art="a" adj="red" noun="car" at={T.r1a} y={760} />
    <Frase e="👜" art="a" adj="blue" noun="bag" at={T.r1b} y={950} />
    <Pop at={T.r1b + 1.2} y={1120}><Chip bg="rgba(8,20,48,.9)" size={36} style={{ border: `3px solid ${YEL}` }}>Em português é o contrário: carro vermelho</Chip></Pop>
  </Cena>
);
const Regra2: React.FC = () => (
  <Cena a={T.r2} b={T.r3 - 0.1}>
    <Pop at={T.r2 + 0.05} y={300}><Chip bg={C_THE} size={46}>REGRA 2</Chip></Pop>
    <Pop at={T.r2h} y={500} from={0.3}><div style={{ display: "flex", alignItems: "center", gap: 26, font: "400 120px Anton", color: "#fff", ...Outline } as any}>
      <Box c={C_A} size={120} tight>ADJETIVO</Box><span style={{ color: C_THE }}>+ S</span><Emoji e="🚫" size={120} /></div></Pop>
    <Frase e="🚗" art="two" adj="red" noun="cars" at={T.r2a} y={780} />
    <Pop at={T.r2b} y={970}><div style={{ display: "flex", alignItems: "center", gap: 22, ...W, fontSize: 96 } as any}>
      <Emoji e="❌" size={90} /><span style={{ color: GREY, textDecoration: "line-through", textDecorationColor: C_THE, textDecorationThickness: 10 }}>two reds cars</span></div></Pop>
  </Cena>
);
const Regra3: React.FC = () => (
  <Cena a={T.r3} b={T.quiz - 0.1}>
    <Pop at={T.r3 + 0.05} y={300}><Chip bg={C_AN} size={46}>REGRA 3 · A × AN</Chip></Pop>
    <Pop at={T.r3h} y={470} from={0.3}><div style={{ display: "flex", alignItems: "center", gap: 26, font: "400 120px Anton", color: "#fff", ...Outline } as any}>
      <Box c={C_A} size={120} tight>A</Box><span style={{ color: YEL, fontSize: 80 }}>ou</span><Box c={C_AN} size={120} tight>AN</Box></div></Pop>
    <Pop at={T.r3h + 0.5} y={640}><Chip bg="rgba(8,20,48,.9)" size={40} style={{ border: `3px solid ${YEL}` }}>depende do SOM da palavra seguinte</Chip></Pop>
    <Frase e="🍎" art="a" artC={C_A} adj="big" noun="apple" at={T.r3a} y={770} size={92} />
    <Frase e="🚗" art="an" artC={C_AN} adj="old" noun="car" at={T.r3b} y={930} size={92} />
    <Frase e="👜" art="an" artC={C_AN} adj="orange" noun="bag" at={T.r3c} y={1090} size={88} />
  </Cena>
);

const QUIZ: QuizItem[] = [
  { e: "🚗", before: "a", answer: "red car", opts: [["a car red", false], ["a red car", true]], tip: <>adjetivo <b style={{ color: C_A }}>antes</b> do substantivo</> },
  { e: "🚗", before: "two", answer: "red cars", opts: [["two reds cars", false], ["two red cars", true]], tip: <>adjetivo <b style={{ color: C_THE }}>nunca</b> leva S</> },
];
export const Cores_: React.FC = () => (
  <Licao tm={TM} hl={{}}>
    <Gancho /><Cores /><Regra1 /><Regra2 /><Regra3 /><Quiz items={QUIZ} /><Chamada />
  </Licao>
);
export { Cores_ as CoresAula };

export const CoresCapa: React.FC = () => (
  <CapaBase tm={TM} tt={4.5}>
    <Center y={245}><Chip bg={C_AN} size={40}>BÁSICO · A1</Chip></Center>
    <Center y={530}><div style={{ font: "400 170px Anton", color: YEL, ...Outline, textAlign: "center", lineHeight: 0.95 } as any}>COLORS<br /><span style={{ fontSize: 110, color: "#fff" }}>& ADJECTIVES</span></div></Center>
    <Center y={770}><div style={{ display: "flex", gap: 22 }}>{["#e53935", "#1e88e5", "#43a047", "#fdd835"].map((c) => <div key={c} style={{ width: 120, height: 120, borderRadius: "50%", background: `radial-gradient(circle at 32% 28%, rgba(255,255,255,.55), ${c} 55%)`, border: "5px solid rgba(255,255,255,.85)" }} />)}</div></Center>
    <Center y={960}><Card w={820}><span style={{ font: "400 110px Anton", color: "#fff" }}>A CAR RED?</span></Card></Center>
    <Center y={1095}><span style={{ font: "800 56px Montserrat", color: MUTED }}>ou</span></Center>
    <Center y={1225}><Card w={820}><span style={{ font: "400 110px Anton", color: "#fff" }}>A RED CAR?</span></Card></Center>
    <Center y={1395}><Chip bg={C_THE} size={46}>VOCÊ ERRA ESSA? · QUIZ</Chip></Center>
  </CapaBase>
);
