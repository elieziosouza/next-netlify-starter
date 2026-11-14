// Quiz relâmpago (03/11/2026): 7 palavras, "como se fala em inglês?", contador de 3 s e revelação com confete, placar no canto.
// Formato que mais cresceu no nicho em outubro de 2026 (ver instagram/swipe.md). Tempos: timings/quizrest.json.
import React from "react";
import { AbsoluteFill, spring } from "remotion";
import TM from "./timings/quizrest.json";
import { useT, env, Chip, Outline, Emoji, Center, Pop, Cena, Chamada, Licao, CapaBase, Confete, Anel,
  INK, YEL, MUTED, GREEN, C_THE } from "./kit";
const T = TM.t as Record<string, number>;

const WORDS: { pt: string; en: string; e: string; tip?: string }[] = [
  { pt: "mesa", en: "table", e: "ic/table.png" },
  { pt: "cardápio", en: "menu", e: "ic/menu.png" },
  { pt: "garçom", en: "waiter", e: "ic/waiter.png" },
  { pt: "reserva", en: "reservation", e: "ic/booking.png" },
  { pt: "prato principal", en: "main course", e: "ic/dish.png" },
  { pt: "conta", en: "bill", e: "ic/receipt.png", tip: "bill = conta · nos EUA também se diz check" },
  { pt: "gorjeta", en: "tip", e: "ic/tip.png" },
];

const Abertura: React.FC = () => (
  <Cena a={0} b={T.q0}>
    <Pop at={0.05} y={300}><Chip bg={GREEN} size={38}>BÁSICO · A1 · RESTAURANTE</Chip></Pop>
    <Pop at={T.title} y={540} from={0.3}><div style={{ font: "400 190px Anton", color: YEL, ...Outline, textAlign: "center", lineHeight: 0.95 } as any}>QUICK<br />QUIZ</div></Pop>
    <Pop at={T.title + 0.6} y={800}><Chip bg="rgba(8,20,48,.9)" size={46} style={{ border: `4px solid ${YEL}` }}>7 PALAVRAS · 3 SEGUNDOS CADA</Chip></Pop>
    <Pop at={T.pt0} y={930}><div style={{ font: "800 54px Montserrat", color: "#fff", ...Outline, WebkitTextStroke: "8px " + INK } as any}>Você consegue? <Emoji e="⏱️" size={56} /></div></Pop>
  </Cena>
);

/** uma pergunta: número n/7, palavra em português, contador, revelação em verde com confete */
const Pergunta: React.FC<{ i: number }> = ({ i }) => {
  const { t } = useT(); const w = WORDS[i]; const a = T["q" + i]; const b = i < 6 ? T["q" + (i + 1)] : T.cta;
  const { start: c0, reveal: rv } = TM.quiz[i]; const k = env(t, a - 0.05, b + 0.15, 0.25, 0.2); if (k <= 0) return null;
  const rvd = t >= rv; const sp = spring({ frame: Math.round((t - rv) * 30), fps: 30, config: { damping: 9 } });
  return (<AbsoluteFill style={{ opacity: k }}>
    <Pop at={a} y={300}><div style={{ font: "400 120px Anton", color: YEL, ...Outline } as any}>{i + 1}<span style={{ color: MUTED, fontSize: 70 }}>/7</span></div></Pop>
    <Pop at={a + 0.1} y={470}><Emoji e={w.e} size={120} style={{ transform: `rotate(${5 * Math.sin(t * 4)}deg)` }} /></Pop>
    <Pop at={a + 0.15} y={640}><div style={{ font: "800 40px Montserrat", color: MUTED, letterSpacing: 3 }}>COMO SE FALA EM INGLÊS?</div></Pop>
    <Pop at={a + 0.2} y={740} dx={240}><div style={{ font: "400 112px Anton", color: "#fff", ...Outline, whiteSpace: "nowrap" } as any}>{w.pt}</div></Pop>
    <Confete t0={rv} x0={540} y0={910} />
    {t >= c0 && t < rv && <Anel c0={c0} />}
    {rvd && <Center y={920}><div style={{ transform: `scale(${0.4 + 0.6 * sp})` }}>
      <div style={{ background: GREEN, color: "#fff", font: "400 104px Anton", padding: "6px 48px", borderRadius: 34, boxShadow: `0 16px 40px rgba(0,0,0,.4), 0 0 60px ${GREEN}88`, whiteSpace: "nowrap" }}>
        {w.en.toUpperCase()} <Emoji e="✅" size={80} style={{ verticalAlign: -6 }} /></div></div></Center>}
    {rvd && w.tip && t >= rv + 0.9 && <Pop at={rv + 0.9} y={1090}><Chip bg="rgba(8,20,48,.94)" size={34} style={{ border: `4px solid ${C_THE}` }}>{w.tip}</Chip></Pop>}
  </AbsoluteFill>);
};

/** placar no canto: uma bolinha por palavra, acende na revelação */
const Placar: React.FC = () => {
  const { t } = useT(); const k = env(t, T.q0, T.cta, 0.3, 0.3); if (k <= 0) return null;
  return <div style={{ position: "absolute", top: 172, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 14, opacity: k }}>
    {WORDS.map((_, i) => { const on = t >= TM.quiz[i].reveal; const cur = t >= T["q" + i] && !on;
      return <div key={i} style={{ width: 30, height: 30, borderRadius: "50%", background: on ? GREEN : "rgba(255,255,255,.12)", border: `3px solid ${cur ? YEL : on ? GREEN : "rgba(255,255,255,.25)"}`,
        transform: `scale(${cur ? 1.15 + 0.08 * Math.sin(t * 8) : 1})` }} />; })}
  </div>;
};

export const QuizRest: React.FC = () => (
  <Licao tm={TM}>
    <Abertura />
    {WORDS.map((_, i) => <Pergunta key={i} i={i} />)}
    <Placar />
    <Chamada titulo="ACERTOU QUANTAS?" pedido="COMENTA SEU PLACAR" />
  </Licao>
);

export const QuizRestCapa: React.FC = () => (
  <CapaBase tm={TM} tt={TM.quiz[0].start + 0.5}>
    <Center y={260}><Chip bg={GREEN} size={40}>BÁSICO · A1 · RESTAURANTE</Chip></Center>
    <Center y={470}><div style={{ font: "400 150px Anton", color: YEL, ...Outline, textAlign: "center", lineHeight: 1 } as any}>COMO SE FALA<br />EM INGLÊS?</div></Center>
    <Center y={760}><div style={{ display: "flex", gap: 26 }}>{[WORDS[0], WORDS[1], WORDS[4], WORDS[5]].map((w) => <Emoji key={w.pt} e={w.e} size={100} />)}</div></Center>
    <Center y={930}><div style={{ font: "400 88px Anton", color: "#fff", ...Outline } as any}>garçom? gorjeta?</div></Center>
    <Center y={1080}><div style={{ font: "800 54px Montserrat", color: "#fff", ...Outline, WebkitTextStroke: "8px " + INK } as any}>7 PALAVRAS · 3 SEGUNDOS <Emoji e="⏱️" size={56} /></div></Center>
    <Center y={1220}><Chip bg={C_THE} size={46}>QUANTAS VOCÊ ACERTA?</Chip></Center>
  </CapaBase>
);
