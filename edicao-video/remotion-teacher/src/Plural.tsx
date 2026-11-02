// Aula "Plural" (s6-a1, 02/11/2026). Tempos: timings/plural.json (scripts/prep_aula.py + aulas/aula_plural.py).
import React from "react";
import { AbsoluteFill } from "remotion";
import TM from "./timings/plural.json";
import { useT, env, Chip, Box, Outline, Emoji, Center, Pop, Cena, Card, capW, Quiz, Chamada, Licao, CapaBase, QuizItem,
  INK, YEL, MUTED, C_A, C_AN, C_THE, GREY, RED } from "./kit";
const T = TM.t as Record<string, number>;
const W = { font: "400 112px Anton", color: "#fff", ...Outline } as any;

/** linha "📕 book → book[S]": a palavra entra em `at1` e o plural com a terminação em caixa colorida em `at2` */
const Linha: React.FC<{ e: string; one: string; stem: string; end: string; c: string; at1: number; at2: number; y: number; strike?: string; tail?: string; size?: number }> = ({ e, one, stem, end, c, at1, at2, y, strike, tail = "", size = 112 }) => {
  const { t } = useT();
  return (<Pop at={at1} y={y} dx={260}><div style={{ display: "flex", alignItems: "center", gap: 26, ...W, fontSize: size } as any}>
    <Emoji e={e} size={size * 0.95} />
    <span>{strike && t >= at2 ? <>{one.slice(0, one.lastIndexOf(strike))}<span style={{ color: GREY, textDecoration: "line-through", textDecorationColor: C_THE, textDecorationThickness: 9 }}>{strike}</span>{one.slice(one.lastIndexOf(strike) + strike.length)}</> : one}</span>
    {t >= at2 && <span style={{ display: "inline-flex", alignItems: "center", gap: 26, opacity: Math.min(1, (t - at2) / 0.2) }}>
      <span style={{ color: YEL, fontSize: size * 0.8 }}>→</span><span>{stem}<Box c={c} size={size} tight>{end}</Box>{tail}</span></span>}
  </div></Pop>);
};

const Gancho: React.FC = () => {
  const p = TM.caps[0].words[2].t;   // "plural"
  return (<Cena a={0} b={T.child}>
    <Pop at={0.05} y={300}><Chip bg={C_AN} size={38}>BÁSICO · A1</Chip></Pop>
    <Pop at={p} y={560} from={0.3}><div style={{ font: "400 210px Anton", color: YEL, ...Outline } as any}>PLURAL</div></Pop>
    <Pop at={p + 0.45} y={800}><div style={{ display: "flex", alignItems: "center", gap: 30 }}><Emoji e="📕" size={120} /><span style={{ ...W, color: YEL }}>→</span><Emoji e="📚" size={130} /></div></Pop>
  </Cena>);
};
const Child: React.FC = () => {
  const { t } = useT(); const c2 = capW(TM as any, 1, "two"), care = capW(TM as any, 1, "careful");
  const wob = t > care ? 5 * Math.sin((t - care) * 18) * Math.exp(-(t - care) * 2) : 0;
  return (<Cena a={T.child} b={T.s}>
    <Pop at={T.child + 0.1} y={480}><Card w={780}><span style={{ font: "400 120px Anton", color: "#fff" }}>ONE CHILD</span></Card></Pop>
    <Pop at={c2} y={700}><div style={{ transform: `rotate(${wob}deg)` }}><Card w={780} border={t > care ? C_THE : undefined}>
      <span style={{ font: "400 120px Anton", color: t > care ? C_THE : "#fff" }}>TWO CHILDS?</span></Card></div></Pop>
    <Pop at={care} y={920}><Chip bg={RED} size={50}><Emoji e="⚠️" size={48} style={{ marginRight: 14, verticalAlign: -6 }} />CUIDADO!</Chip></Pop>
  </Cena>);
};
const RegraS: React.FC = () => (
  <Cena a={T.s} b={T.es}>
    <Pop at={T.s + 0.05} y={300}><Chip bg={C_A} size={46}>A MAIORIA: + S</Chip></Pop>
    <Pop at={T.s + 0.5} y={500} from={0.3}><div style={{ font: "400 200px Anton" }}><Box c={C_A} size={200}>+ S</Box></div></Pop>
    <Linha e="📕" one="book" stem="book" end="s" c={C_A} at1={T.s1} at2={T.s2} y={760} />
    <Linha e="🚗" one="car" stem="car" end="s" c={C_A} at1={T.s2 + 0.5} at2={T.s2 + 0.9} y={950} size={96} />
  </Cena>
);
const RegraES: React.FC = () => (
  <Cena a={T.es} b={T.y}>
    <Pop at={T.es + 0.05} y={300}><Chip bg={C_AN} size={46}>TERMINOU EM S · SH · CH · X</Chip></Pop>
    {["S", "SH", "CH", "X"].map((l, i) => <Pop key={l} at={T.es + 0.6 + i * 0.55} y={470}><div style={{ transform: `translateX(${(i - 1.5) * 190}px)` }}>
      <div style={{ width: 160, height: 120, borderRadius: 26, border: `5px solid ${C_AN}`, background: "rgba(8,20,48,.8)", color: "#fff", font: "400 80px Anton", display: "grid", placeItems: "center" }}>{l}</div></div></Pop>)}
    <Pop at={T.es0} y={610}><Chip bg={C_AN} size={52}>+ ES</Chip></Pop>
    <Linha e="🚌" one="bus" stem="bus" end="es" c={C_AN} at1={T.es1} at2={T.es2} y={790} />
    <Linha e="🍽️" one="dish" stem="dish" end="es" c={C_AN} at1={T.es3} at2={T.es4} y={980} />
  </Cena>
);
const RegraY: React.FC = () => (
  <Cena a={T.y} b={T.irr}>
    <Pop at={T.y + 0.05} y={300}><Chip bg={YEL} color={INK} size={46}>CONSOANTE + Y</Chip></Pop>
    <Pop at={T.y0} y={500} from={0.3}><div style={{ display: "flex", alignItems: "center", gap: 30, font: "400 170px Anton", color: "#fff", ...Outline } as any}>
      <span style={{ color: GREY, textDecoration: "line-through", textDecorationColor: C_THE, textDecorationThickness: 12 }}>Y</span><span style={{ color: YEL }}>→</span><Box c={C_THE} size={170}>IES</Box></div></Pop>
    <Linha e="👶" one="baby" stem="bab" end="ies" c={C_THE} strike="y" at1={T.y1} at2={T.y2} y={760} />
    <Pop at={T.yPt + 0.3} y={960}><Chip bg="rgba(8,20,48,.9)" size={36} style={{ border: `3px solid ${YEL}` }}>Vogal + Y? Só coloca S: boy → boys</Chip></Pop>
  </Cena>
);
const Irregulares: React.FC = () => (
  <Cena a={T.irr} b={T.quiz}>
    <Pop at={T.irr + 0.05} y={300}><Chip bg={C_THE} size={46}>IRREGULARES: É SÓ DECORAR</Chip></Pop>
    <Linha e="🧒" one="child" stem="child" end="ren" c={C_THE} at1={T.irr1} at2={T.irr1 + 0.75} y={500} size={100} />
    <Linha e="👨" one="man" stem="m" end="en" c={C_THE} strike="an" at1={T.irr2} at2={T.irr2 + 0.7} y={690} size={100} />
    <Linha e="🦶" one="foot" stem="f" end="ee" tail="t" c={C_THE} strike="oo" at1={T.irr3} at2={T.irr3 + 0.7} y={880} size={100} />
  </Cena>
);
const QUIZ: QuizItem[] = [
  { e: "⌚", before: "two", answer: "watches", opts: [["two watchs", false], ["two watches", true]], tip: <>WATCH termina em <b style={{ color: C_AN }}>CH</b> → + ES</> },
  { e: "🎉", before: "two", answer: "parties", opts: [["two partys", false], ["two parties", true]], tip: <>consoante + <b style={{ color: C_THE }}>Y</b> → IES</> },
];
export const Plural: React.FC = () => (
  <Licao tm={TM} hl={{ S: C_A, ES: C_AN, IES: C_THE }}>
    <Gancho /><Child /><RegraS /><RegraES /><RegraY /><Irregulares /><Quiz items={QUIZ} /><Chamada />
  </Licao>
);

export const PluralCapa: React.FC = () => (
  <CapaBase tm={TM} tt={4.5}>
    <Center y={260}><Chip bg={C_AN} size={40}>BÁSICO · A1</Chip></Center>
    <Center y={460}><div style={{ font: "400 200px Anton", color: YEL, ...Outline } as any}>PLURAL</div></Center>
    <Center y={700}><Card w={820}><span style={{ font: "400 120px Anton", color: "#fff" }}>TWO CHILDS?</span></Card></Center>
    <Center y={850}><span style={{ font: "800 56px Montserrat", color: MUTED }}>ou</span></Center>
    <Center y={1000}><Card w={820}><span style={{ font: "400 120px Anton", color: "#fff" }}>TWO CHILDREN?</span></Card></Center>
    <Center y={1210}><Chip bg={C_THE} size={46}>VOCÊ ERRA ESSA? · QUIZ</Chip></Center>
  </CapaBase>
);
