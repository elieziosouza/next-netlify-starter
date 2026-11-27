// Aula "As horas" (s9-a1, 26/11/2026). Tempos: timings/horas.json (scripts/prep_aula.py + aulas/aula_horas.py).
// Melhoria desta aula: relógio de ponteiros que gira até a hora falada (o ponteiro dos minutos varre o mostrador) e fatia colorida mostrando o quarto de hora.
import React from "react";
import { AbsoluteFill } from "remotion";
import TM from "./timings/horas.json";
import { useT, useTM, Chip, Box, Outline, Emoji, Center, Pop, Cena, Card, Chamada, Licao, CapaBase, Confete, Anel, Opcao, clamp, env,
  INK, YEL, MUTED, C_A, C_AN, C_THE, GREEN, RED, PT } from "./kit";
const T = TM.t as Record<string, number>;
const eo = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const eio = (x: number) => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const H = (h: number, m = 0) => h * 60 + m;

/** relógio de ponteiros: keys = [instante, minutos desde 0h]; os ponteiros giram suavemente de uma hora para a outra */
type Fatia = { a: number; b: number; c: string; at: number };
const Relogio: React.FC<{ keys: [number, number][]; size: number; fatia?: Fatia; tt?: number }> = ({ keys, size, fatia, tt }) => {
  const { t: t0 } = useT(); const t = tt ?? t0;
  let m = keys[0][1];
  for (let i = 1; i < keys.length; i++) { const [at, v] = keys[i]; m = m + (v - m) * eio((t - at) / 0.9); }
  const ma = (m % 60) * 6, ha = ((m / 60) % 12) * 30;
  const arc = (a: number, b: number, r: number) => { const p = (mm: number) => { const g = (mm * 6 - 90) * Math.PI / 180; return [100 + r * Math.cos(g), 100 + r * Math.sin(g)]; };
    const [x0, y0] = p(a), [x1, y1] = p(b); return `M 100 100 L ${x0} ${y0} A ${r} ${r} 0 ${b - a > 30 ? 1 : 0} 1 ${x1} ${y1} Z`; };
  const fk = fatia ? eo((t - fatia.at) / 0.5) : 0;
  return <svg width={size} height={size} viewBox="0 0 200 200" style={{ filter: "drop-shadow(0 16px 24px rgba(0,0,0,.45))", overflow: "visible" }}>
    <circle cx={100} cy={100} r={94} fill="#f6f8fc" stroke={YEL} strokeWidth={8} />
    {fatia && fk > 0 && <path d={arc(fatia.a, fatia.a + (fatia.b - fatia.a) * fk, 86)} fill={fatia.c} opacity={0.42} />}
    {Array.from({ length: 60 }).map((_, i) => { const g = (i * 6 - 90) * Math.PI / 180, big = i % 5 === 0, r0 = big ? 80 : 84;
      return <line key={i} x1={100 + r0 * Math.cos(g)} y1={100 + r0 * Math.sin(g)} x2={100 + 89 * Math.cos(g)} y2={100 + 89 * Math.sin(g)} stroke={big ? INK : "#9aa6c0"} strokeWidth={big ? 3 : 1.2} strokeLinecap="round" />; })}
    {Array.from({ length: 12 }).map((_, i) => { const n = i + 1, g = (n * 30 - 90) * Math.PI / 180;
      return <text key={n} x={100 + 67 * Math.cos(g)} y={100 + 67 * Math.sin(g) + 7} textAnchor="middle" style={{ font: "400 20px Anton", fill: INK }}>{n}</text>; })}
    <line x1={100} y1={100} x2={100} y2={52} stroke={INK} strokeWidth={8} strokeLinecap="round" transform={`rotate(${ha} 100 100)`} />
    <line x1={100} y1={112} x2={100} y2={28} stroke={C_THE} strokeWidth={5} strokeLinecap="round" transform={`rotate(${ma} 100 100)`} />
    <circle cx={100} cy={100} r={7} fill={INK} stroke={YEL} strokeWidth={2.5} />
  </svg>;
};
/** horário digital em caixinha */
const Digital: React.FC<{ s: string; c?: string; fs?: number }> = ({ s, c = C_A, fs = 64 }) => (
  <div style={{ background: INK, border: `4px solid ${c}`, borderRadius: 18, padding: "4px 22px", font: `800 ${fs}px Montserrat`, color: "#fff", letterSpacing: 2, boxShadow: `0 0 24px ${c}66` }}>{s}</div>
);
const Linha: React.FC<{ d: string; en: string; c?: string }> = ({ d, en, c }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 26 }}><Digital s={d} c={c} /><span style={{ font: "400 70px Anton", color: "#fff", ...Outline } as any}>{en}</span></div>
);

// ------------------------------------------------------------ gancho
const Gancho: React.FC = () => {
  const { t } = useT();
  return (<Cena a={0} b={T.perg - 0.1}>
    <Pop at={0.05} y={265}><Chip bg={C_AN} size={38}>BÁSICO · A1</Chip></Pop>
    <Pop at={T.tit} y={455} from={0.3}><div style={{ font: "400 150px Anton", color: YEL, ...Outline, textAlign: "center", lineHeight: 0.95 } as any}>TELLING<br /><span style={{ fontSize: 110, color: "#fff" }}>THE TIME</span></div></Pop>
    <Pop at={T.tit + 0.2} y={800}><Relogio size={330} keys={[[0, H(10, 10)], [T.tit + 0.2, H(12, 0)], [T.ask, H(3, 0) + 720]]} /></Pop>
    <Pop at={T.ask} y={1080}><Card w={760}><span style={{ font: "400 84px Anton", color: "#fff" }}>What time is it?</span></Card></Pop>
    <Pop at={T.pt + 2.0} y={1205}><Chip bg="rgba(8,20,48,.9)" size={40} style={{ border: `3px solid ${YEL}` }}>Que horas são?</Chip></Pop>
  </Cena>);
};

// ------------------------------------------------------------ como perguntar
const Pergunta: React.FC = () => {
  const { t } = useT(); const wob = 8 * Math.sin(t * 3);
  return (<Cena a={T.perg} b={T.r1 - 0.1}>
    <Pop at={T.perg + 0.05} y={300}><Chip bg={YEL} color={INK} size={46}>PARA PERGUNTAR</Chip></Pop>
    <Pop at={T.perg2} y={520} from={0.3}><div style={{ font: "400 118px Anton", color: "#fff", ...Outline, textAlign: "center" } as any}>What <span style={{ color: YEL }}>time</span><br />is it?</div></Pop>
    <Pop at={T.pergpt} y={790}><Chip bg={C_THE} size={50}>= Que horas são?</Chip></Pop>
    <Pop at={T.pergpt + 0.3} y={1000}><div style={{ display: "flex", alignItems: "center", gap: 20 }}><Relogio size={230} keys={[[0, H(3, 0)], [T.perg, H(3, 0)]]} /><span style={{ font: "400 160px Anton", color: YEL, ...Outline, display: "inline-block", transform: `rotate(${wob}deg)` } as any}>?</span></div></Pop>
  </Cena>);
};

// ------------------------------------------------------------ regras
const Regra1: React.FC = () => (
  <Cena a={T.r1} b={T.r2 - 0.1}>
    <Pop at={T.r1 + 0.05} y={300}><Chip bg={C_A} size={46}>REGRA 1 · HORA EXATA</Chip></Pop>
    <Pop at={T.r1 + 0.15} y={590}><Relogio size={360} keys={[[0, H(12, 0)], [T.r1a, H(15, 0)]]} /></Pop>
    <Pop at={T.r1a} y={850}><div style={{ font: "400 100px Anton", color: "#fff", ...Outline } as any}><Box c={C_A} size={100} tight>O'CLOCK</Box></div></Pop>
    <Pop at={T.r1b} y={1000}><Linha d="3:00" en="three o'clock" /></Pop>
    <Pop at={T.r1p} y={1125}><Chip bg="rgba(8,20,48,.9)" size={38} style={{ border: `3px solid ${YEL}` }}>hora exata = o'clock</Chip></Pop>
  </Cena>
);
const Regra2: React.FC = () => (
  <Cena a={T.r2} b={T.r3 - 0.1}>
    <Pop at={T.r2 + 0.05} y={300}><Chip bg={C_AN} size={46}>REGRA 2 · MEIA HORA</Chip></Pop>
    <Pop at={T.r2 + 0.15} y={590}><Relogio size={360} keys={[[0, H(3, 0)], [T.r2a, H(3, 30)]]} fatia={{ a: 0, b: 30, c: C_AN, at: T.r2a + 0.5 }} /></Pop>
    <Pop at={T.r2a} y={850}><div style={{ font: "400 100px Anton", color: "#fff", ...Outline } as any}><Box c={C_AN} size={100} tight>HALF PAST</Box></div></Pop>
    <Pop at={T.r2b} y={1000}><Linha d="3:30" en="half past three" c={C_AN} /></Pop>
    <Pop at={T.r2p} y={1125}><Chip bg="rgba(8,20,48,.9)" size={38} style={{ border: `3px solid ${YEL}` }}>half = metade · meia hora</Chip></Pop>
  </Cena>
);
const Regra3: React.FC = () => (
  <Cena a={T.r3} b={T.ez - 0.1}>
    <Pop at={T.r3 + 0.05} y={300}><Chip bg={C_THE} size={46}>REGRA 3 · QUARTER</Chip></Pop>
    <Pop at={T.r3a} y={650} dx={-200}><div style={{ transform: "translateX(-240px)", display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
      <Relogio size={300} keys={[[0, H(3, 0)], [T.r3a, H(3, 15)]]} fatia={{ a: 0, b: 15, c: GREEN, at: T.r3a + 0.6 }} />
      <Digital s="3:15" c={GREEN} fs={54} /><span style={{ font: "400 52px Anton", color: "#fff", ...Outline } as any}>quarter <span style={{ color: GREEN }}>past</span> three</span></div></Pop>
    <Pop at={T.r3b} y={650} dx={200}><div style={{ transform: "translateX(240px)", display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
      <Relogio size={300} keys={[[0, H(3, 0)], [T.r3b, H(3, 45)]]} fatia={{ a: 45, b: 60, c: C_A, at: T.r3b + 0.6 }} />
      <Digital s="3:45" c={C_A} fs={54} /><span style={{ font: "400 52px Anton", color: "#fff", ...Outline } as any}>quarter <span style={{ color: C_A }}>to</span> four</span></div></Pop>
    <Pop at={T.r3q} y={940}><Chip bg={YEL} color={INK} size={42}>quarter = 15 minutos</Chip></Pop>
    <Pop at={T.r3p} y={1060}><div style={{ display: "flex", gap: 24 }}>
      <Chip bg={GREEN} size={38}>past = depois</Chip>{useT().t >= T.r3t && <Chip bg={C_A} size={38}>to = antes</Chip>}</div></Pop>
  </Cena>
);
const Facil: React.FC = () => (
  <Cena a={T.ez} b={T.quiz - 0.1}>
    <Pop at={T.ez + 0.05} y={300}><Chip bg={YEL} color={INK} size={46}>JEITO FÁCIL · EASY WAY</Chip></Pop>
    <Pop at={T.ez + 0.5} y={500}><div style={{ font: "400 84px Anton", color: "#fff", ...Outline, textAlign: "center" } as any}>Fale só os <span style={{ color: YEL }}>números</span></div></Pop>
    <Pop at={T.ez1} y={700} dx={-260}><Linha d="3:15" en="three fifteen" c={GREEN} /></Pop>
    <Pop at={T.ez2} y={860} dx={-260}><Linha d="3:30" en="three thirty" c={C_AN} /></Pop>
  </Cena>
);

// ------------------------------------------------------------ quiz com relógio
type QH = { h: number; ini: number; opts: [string, boolean][]; tip: React.ReactNode };
const QUIZ: QH[] = [
  { h: H(7, 30), ini: H(12, 0), opts: [["half past seven", true], ["half past eight", false]], tip: <>7:30 = <b style={{ color: C_AN }}>half past seven</b></> },
  { h: H(4, 45), ini: H(7, 30), opts: [["quarter past five", false], ["quarter to five", true]], tip: <>4:45 = <b style={{ color: C_AN }}>quarter to five</b></> },
];
const QuizHoras: React.FC = () => {
  const TMx = useTM(); const { t } = useT(); const a = T.quiz, b = T.cta; const k = env(t, a, b); if (k <= 0) return null;
  const qi = t < T.q2 - 0.15 ? 0 : 1; const q = QUIZ[qi]; const { start: c0, reveal: rv } = TMx.quiz[qi];
  const qa = qi === 0 ? T.q1 : T.q2; const qk = qi === 0 ? env(t, qa - 0.05, T.q2 - 0.15, 0.25, 0.2) : env(t, qa - 0.05, b, 0.25, 0.25); const rvd = t >= rv;
  const ok = q.opts.findIndex((o) => o[1]);
  return (<AbsoluteFill style={{ opacity: k }}>
    <Pop at={a} y={290}><Chip bg={YEL} color={INK} size={60}>QUIZ</Chip></Pop>
    <AbsoluteFill style={{ opacity: qk }}>
      <Center y={392}><div style={{ font: "800 36px Montserrat", color: MUTED }}>PERGUNTA {qi + 1} DE 2 · WHAT TIME IS IT?</div></Center>
      <Pop at={qa} y={580}><Relogio size={300} keys={[[0, q.ini], [qa + 0.1, q.h]]} /></Pop>
      <Confete t0={rv} x0={540} y0={790 + ok * 150} />
      {q.opts.map(([s, good], i) => <Opcao key={qi + "-" + i} i={i} s={s} good={good} ta={qa + 0.25 + i * 0.3} rv={rv} />)}
      {t >= c0 && t < rv && <Anel c0={c0} />}
      {t >= rv + 0.2 && <Pop at={rv + 0.2} y={1110}><Chip bg="rgba(8,20,48,.92)" size={40} style={{ border: `4px solid ${YEL}` }}>{q.tip}</Chip></Pop>}
    </AbsoluteFill>
  </AbsoluteFill>);
};

export const HorasAula: React.FC = () => (
  <Licao tm={TM} hl={{}}>
    <Gancho /><Pergunta /><Regra1 /><Regra2 /><Regra3 /><Facil /><QuizHoras /><Chamada />
  </Licao>
);
export const HorasCapa: React.FC = () => (
  <CapaBase tm={TM} tt={4.5}>
    <Center y={245}><Chip bg={C_AN} size={40}>BÁSICO · A1</Chip></Center>
    <Center y={470}><div style={{ font: "400 150px Anton", color: YEL, ...Outline, textAlign: "center", lineHeight: 0.95 } as any}>WHAT TIME<br /><span style={{ color: "#fff" }}>IS IT?</span></div></Center>
    <Center y={830}><Relogio size={360} keys={[[0, H(4, 45)]]} fatia={{ a: 45, b: 60, c: C_A, at: -1 }} tt={5} /></Center>
    <Center y={1085}><Card w={820}><span style={{ font: "400 84px Anton", color: "#fff" }}>quarter <span style={{ color: MUTED }}>____</span> five?</span></Card></Center>
    <Center y={1240}><Chip bg={C_THE} size={46}>VOCÊ SABE DIZER? · QUIZ</Chip></Center>
  </CapaBase>
);
