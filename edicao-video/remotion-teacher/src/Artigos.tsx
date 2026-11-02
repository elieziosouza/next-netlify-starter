// Aula "A, an, the" (s5-a1, 01/11/2026). Tempos: timings/artigos.json (scripts/prep_aula.py + aulas/aula_artigos.py).
import React from "react";
import { AbsoluteFill } from "remotion";
import TM from "./timings/artigos.json";
import { useT, env, Chip, Box, Outline, Emoji, Center, Pop, Cena, Card, capW, Quiz, Chamada, Licao, CapaBase, QuizItem,
  INK, YEL, MUTED, C_A, C_AN, C_THE, GREY, RED } from "./kit";
const T = TM.t as Record<string, number>;
const Gancho: React.FC = () => {
  const ws = TM.caps[0].words.slice(2);   // "a," "an," "and" "the."
  const tiles: [string, string, number][] = [["A", C_A, ws[0].t], ["AN", C_AN, ws[1].t], ["THE", C_THE, ws[3].t]];
  return (<Cena a={0} b={T.uni}>
    <Pop at={0.05} y={300}><Chip bg={C_AN} size={38}>BÁSICO · A1</Chip></Pop>
    {tiles.map(([s, c, at], i) => <Pop key={s} at={at} y={590} dx={(i - 1) * 300} from={0.3}>
      <div style={{ transform: `translateX(${(i - 1) * 300}px)` }}><div style={{ font: "400 170px Anton" }}><Box c={c} size={170}>{s}</Box></div></div></Pop>)}
    <Pop at={ws[3].t + 0.3} y={830}><div style={{ font: "800 46px Montserrat", color: MUTED, letterSpacing: 6 }}>ARTIGOS EM INGLÊS</div></Pop>
  </Cena>);
};
const University: React.FC = () => {
  const { t } = useT(); const a = T.uni + 0.1, b = capW(TM as any, 1, "an") , m = capW(TM as any, 1, "many");
  return (<Cena a={T.uni} b={T.a}>
    <Pop at={a} y={470}><Card w={760}><span style={{ font: "400 110px Anton", color: "#fff" }}>A UNIVERSITY</span></Card></Pop>
    <Pop at={a + 0.5} y={600}><span style={{ font: "800 54px Montserrat", color: MUTED }}>ou</span></Pop>
    <Pop at={b} y={730}><Card w={760}><span style={{ font: "400 110px Anton", color: "#fff" }}>AN UNIVERSITY</span></Card></Pop>
    <Pop at={m} y={930}><Chip bg={RED} size={46}><Emoji e="🤯" size={46} style={{ marginRight: 14, verticalAlign: -6 }} />MUITA GENTE ERRA</Chip></Pop>
    {t > b + 0.4 && <Center y={600}><div style={{ position: "absolute", left: 870, font: "400 140px Anton", color: YEL, ...Outline, transform: `rotate(${8 * Math.sin(t * 3)}deg)` } as any}>?</div></Center>}
  </Cena>);
};
const Regra: React.FC<{ a: number; b: number; chip: string; c: string; rows: [string, string, string, number][]; extra?: React.ReactNode }> = ({ a, b, chip, c, rows, extra }) => (
  <Cena a={a} b={b}>
    <Pop at={a + 0.05} y={300}><Chip bg={c} size={46}>{chip}</Chip></Pop>
    {rows.map(([e, art, noun, at], i) => <Pop key={i} at={at} y={520 + i * 200} dx={260}>
      <div style={{ display: "flex", alignItems: "center", gap: 34 }}><Emoji e={e} size={120} />
        <span style={{ font: "400 120px Anton", color: "#fff", ...Outline } as any}><Box c={c} size={120}>{art}</Box> {noun}</span></div></Pop>)}
    {extra}
  </Cena>
);
const Vogais: React.FC<{ at: number }> = ({ at }) => (
  <>{"AEIOU".split("").map((v, i) => <Pop key={v} at={at + i * 0.12} y={960}><div style={{ transform: `translateX(${(i - 2) * 140}px)` }}>
    <div style={{ width: 110, height: 110, borderRadius: 26, border: `5px solid ${C_AN}`, background: "rgba(8,20,48,.8)", color: "#fff", font: "400 76px Anton", display: "grid", placeItems: "center" }}>{v}</div></div></Pop>)}</>
);
const SomLetra: React.FC = () => {
  const { t } = useT(); const k = env(t, T.som1 + 0.3, T.som2 - 0.05, 0.3, 0.25); if (k <= 0) return null;
  return <AbsoluteFill style={{ opacity: k }}><Pop at={T.som1 + 0.3} y={640}><div style={{ display: "flex", alignItems: "center", gap: 40, font: "400 120px Anton", color: "#fff", ...Outline } as any}>
    <span><Emoji e="🔊" size={110} /> SOM</span><span style={{ color: YEL, transform: `scale(${1 + 0.08 * Math.sin(t * 6)})`, display: "inline-block" }}>&gt;</span>
    <span style={{ color: MUTED }}><Emoji e="🔤" size={110} /> LETRA</span></div></Pop></AbsoluteFill>;
};
const Som: React.FC = () => (
  <Cena a={T.som} b={T.the}>
    <Pop at={T.som1} y={300}><Chip bg={YEL} color={INK} size={46}>VALE O SOM, NÃO A LETRA</Chip></Pop>
    <SomLetra />
    <Pop at={T.som2} y={540} dx={260}><div style={{ textAlign: "center" }}>
      <div style={{ font: "400 118px Anton", color: "#fff", ...Outline } as any}><Box c={C_A} size={118}>a</Box> <span style={{ color: YEL, textDecoration: "underline", textDecorationThickness: 8, textUnderlineOffset: 14 }}>u</span>niversity</div>
      <Chip bg="rgba(8,20,48,.85)" size={36} style={{ border: `3px solid ${C_A}`, marginTop: 10 }}>"U" com som de "iu" → A</Chip></div></Pop>
    <Pop at={T.som3} y={830} dx={260}><div style={{ textAlign: "center" }}>
      <div style={{ font: "400 118px Anton", color: "#fff", ...Outline } as any}><Box c={C_AN} size={118}>an</Box> <span style={{ color: GREY, textDecoration: "line-through", textDecorationThickness: 10, textDecorationColor: C_THE }}>h</span>our</div>
      <Chip bg="rgba(8,20,48,.85)" size={36} style={{ border: `3px solid ${C_AN}`, marginTop: 10 }}>"H" mudo: começa com vogal → AN</Chip></div></Pop>
  </Cena>
);
const The: React.FC = () => (
  <Regra a={T.the} b={T.quiz} chip="THE = ALGO ESPECÍFICO" c={C_THE} rows={[["☀️", "the", "sun", T.the1], ["📕", "the", "book", T.the2]]}
    extra={<>
      <Pop at={T.the2 + 0.45} y={840}><span style={{ font: "800 44px Montserrat", color: MUTED }}>on the table</span></Pop>
      {["o", "a", "os", "as"].map((w, i) => <Pop key={w} at={T.thept + 0.2 + i * 0.3} y={990}><div style={{ transform: `translateX(${(i - 1.5) * 170}px)` }}>
        <Chip bg={C_THE} size={50} style={{ minWidth: 120, textAlign: "center" }}>{w}</Chip></div></Pop>)}
    </>} />
);
const QUIZ: QuizItem[] = [
  { e: "🍊", answer: "an", after: "orange", opts: [["a orange", false], ["an orange", true]], tip: <>ORANGE começa com <b style={{ color: C_AN }}>som de vogal</b> → AN</> },
  { e: "👕", answer: "a", after: "uniform", opts: [["a uniform", true], ["an uniform", false]], tip: <>UNIFORM soa <b style={{ color: C_A }}>"iu"</b> → A</> },
];
export const Artigos: React.FC = () => (
  <Licao tm={TM} hl={{ '"a"': C_A, '"an"': C_AN, '"the"': C_THE }}>
    <Gancho /><University />
    <Regra a={T.a} b={T.an} chip="A + SOM DE CONSOANTE" c={C_A} rows={[["🐶", "a", "dog", T.a1], ["🚗", "a", "car", T.a2]]} />
    <Regra a={T.an} b={T.som} chip="AN + SOM DE VOGAL" c={C_AN} rows={[["🍎", "an", "apple", T.an1], ["🥚", "an", "egg", T.an2]]} extra={<Vogais at={T.an + 0.6} />} />
    <Som /><The /><Quiz items={QUIZ} /><Chamada />
  </Licao>
);

// capas
export const ArtigosCapa: React.FC = () => {
  return (<CapaBase tm={TM} tt={6.8}>
    <Center y={260}><Chip bg={C_AN} size={40}>BÁSICO · A1</Chip></Center>
    <Center y={480}><div style={{ font: "400 190px Anton", color: "#fff", ...Outline } as any}><Box c={C_A} size={190}>A</Box> <span style={{ fontSize: 110, color: MUTED }}>ou</span> <Box c={C_AN} size={190}>AN</Box></div></Center>
    <Center y={720}><div style={{ font: "400 130px Anton", color: YEL, ...Outline } as any}>VOCÊ ERRA ESSA?</div></Center>
    <Center y={900}><div style={{ font: "400 100px Anton", color: "#fff", ...Outline } as any}><span style={{ color: MUTED }}>___</span> university</div></Center>
    <Center y={1040}><div style={{ font: "400 100px Anton", color: "#fff", ...Outline } as any}><span style={{ color: MUTED }}>___</span> hour</div></Center>
    <Center y={1230}><Chip bg={C_THE} size={46}>QUIZ COM RESPOSTA</Chip></Center>
  </CapaBase>);
};
export const ArtigosCapa2: React.FC = () => {
  const Op: React.FC<{ n: number; s: string; rot: number }> = ({ n, s, rot }) => (
    <div style={{ width: 860, height: 170, borderRadius: 40, background: "#fff", border: `7px solid ${YEL}`, display: "flex", alignItems: "center", position: "relative", transform: `rotate(${rot}deg)`, boxShadow: "0 20px 44px rgba(0,0,0,.45)" }}>
      <div style={{ position: "absolute", left: 26, width: 112, height: 112, borderRadius: "50%", background: INK, color: "#fff", font: "800 60px Montserrat", display: "grid", placeItems: "center" }}>{n}</div>
      <div style={{ flex: 1, textAlign: "center", font: "400 104px Anton", color: INK, paddingLeft: 90 }}>{s}</div></div>
  );
  return (<CapaBase tm={TM} tt={46.5}>
    <Center y={260}><Chip bg={C_AN} size={40}>BÁSICO · A1</Chip></Center>
    <Center y={520}><div style={{ font: "400 150px Anton", color: YEL, ...Outline, textAlign: "center", lineHeight: 1 } as any}>QUAL ESTÁ<br />CERTO?</div></Center>
    <Center y={830}><Op n={1} s="A UNIVERSITY" rot={-2} /></Center>
    <Center y={1040}><Op n={2} s="AN UNIVERSITY" rot={1.5} /></Center>
    <Center y={1240}><div style={{ font: "800 50px Montserrat", color: "#fff", ...Outline, WebkitTextStroke: "8px " + INK } as any}>MUITA GENTE ERRA ESSA <Emoji e="🤯" size={54} /></div></Center>
    <Center y={1350}><Chip bg={C_THE} size={42}>QUIZ COM RESPOSTA</Chip></Center>
  </CapaBase>);
};
