// Quiz relâmpago do passeio turístico (18/11/2026); base: QuizHotel (03/11/2026): 7 palavras, "como se fala em inglês?", contador de 3 s e revelação com confete, placar no canto.
// Formato que mais cresceu no nicho em outubro de 2026 (ver instagram/swipe.md). Tempos: timings/quizpasseio.json.
import React from "react";
import { AbsoluteFill, spring } from "remotion";
import TM from "./timings/quizpasseio.json";
import { useT, env, clamp, Chip, Outline, Emoji, Center, Pop, Cena, Chamada, Licao, CapaBase, Confete, Anel,
  INK, YEL, MUTED, GREEN, C_THE } from "./kit";
const T = TM.t as Record<string, number>;

const WORDS: { pt: string; en: string; e: string; tip?: string }[] = [
  { pt: "ingresso", en: "ticket", e: "ic/ticket.png" },
  { pt: "mapa", en: "map", e: "ic/map.png" },
  { pt: "guia", en: "tour guide", e: "ic/guide.png" },
  { pt: "museu", en: "museum", e: "ic/museum.png" },
  { pt: "lembrança", en: "souvenir", e: "ic/souvenir.png" },
  { pt: "fila", en: "line", e: "ic/queue.png", tip: "line (EUA) · queue (Reino Unido)" },
  { pt: "ponto turístico", en: "landmark", e: "ic/landmark.png", tip: "tourist attraction também serve" },
];


/** partículas de luz subindo devagar atrás de tudo (profundidade) */
const Bokeh: React.FC = () => {
  const { t } = useT();
  return (<AbsoluteFill style={{ pointerEvents: "none" }}>{Array.from({ length: 16 }, (_, i) => {
    const r = (n: number) => { const x = Math.sin(i * 12.9898 + n * 78.233) * 43758.5453; return x - Math.floor(x); };
    const sz = 40 + r(1) * 110, sp = 14 + r(2) * 26, x = r(3) * 1080, y0 = r(4) * 2100;
    const y = 2100 - ((y0 + t * sp) % 2300) + 100, a = 0.05 + 0.08 * r(5);
    return <div key={i} style={{ position: "absolute", left: x + 30 * Math.sin(t * 0.5 + i), top: y, width: sz, height: sz, borderRadius: "50%", background: `radial-gradient(circle, rgba(255,214,64,${a * 2}), rgba(255,214,64,0) 70%)` }} />;
  })}</AbsoluteFill>);
};

/** faixa de luz que cruza a tela quando entra a pergunta */
const Varrida: React.FC<{ a: number }> = ({ a }) => {
  const { t } = useT(); const u = (t - a) / 0.55; if (u < 0 || u > 1) return null;
  return <div style={{ position: "absolute", top: -100, left: -400 + 1900 * u, width: 260, height: 2200, transform: "rotate(18deg)", background: "linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,.22), rgba(255,255,255,0))", opacity: 1 - 0.4 * u }} />;
};

/** onda de choque saindo da resposta */
const Onda: React.FC<{ rv: number; y: number }> = ({ rv, y }) => {
  const { t } = useT(); const u = (t - rv) / 0.7; if (u < 0 || u > 1) return null;
  return <div style={{ position: "absolute", left: 540 - 200, top: y - 200, width: 400, height: 400, borderRadius: "50%", border: `${10 - 8 * u}px solid ${YEL}`, transform: `scale(${0.5 + 2.6 * u})`, opacity: 1 - u }} />;
};

const Abertura: React.FC = () => (
  <Cena a={0} b={T.q0}>
    <Pop at={0.05} y={300}><Chip bg={GREEN} size={38}>BÁSICO · A1 · PASSEIO</Chip></Pop>
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
  const push = 1 + 0.045 * clamp((t - a) / (b - a));                       // câmera se aproxima devagar
  const hop = rvd ? Math.max(0, 1 - (t - rv) / 0.45) : 0;                  // pulinho do ícone na resposta
  const ia = t - (a + 0.1), pop = spring({ frame: Math.round(Math.max(0, ia) * 30), fps: 30, config: { damping: 10 } });
  return (<AbsoluteFill style={{ opacity: k }}>
    <Varrida a={a} />
    <AbsoluteFill style={{ transform: `scale(${push})`, transformOrigin: "540px 700px" }}>
    <Pop at={a} y={285}><div style={{ font: "400 120px Anton", color: YEL, ...Outline } as any}>{i + 1}<span style={{ color: MUTED, fontSize: 70 }}>/7</span></div></Pop>
    <div style={{ position: "absolute", left: 540 - 280, top: 520 - 280, width: 560, height: 560, borderRadius: "50%", opacity: clamp(ia / 0.3) * (rvd ? 1 : 0.8), transform: `scale(${1 + 0.05 * Math.sin(t * 3) + 0.25 * hop})`,
      background: `radial-gradient(circle, ${rvd ? "rgba(46,204,113,.45)" : "rgba(255,214,64,.38)"} 0%, rgba(255,214,64,0) 62%)` }} />
    <div style={{ position: "absolute", left: 540 - 105, top: 520 - 105, width: 210, height: 210, opacity: clamp(ia / 0.15), transform: `translateY(${-30 * hop + 8 * Math.sin(t * 2.6)}px) scale(${(0.3 + 0.7 * pop) * (1 + 0.12 * hop)}) rotate(${5 * Math.sin(t * 2)}deg)` }}>
      <Emoji e={w.e} size={210} style={{ filter: "drop-shadow(0 22px 26px rgba(0,0,0,.45))" }} /></div>
    <div style={{ position: "absolute", left: 540 - 100, top: 650, width: 200, height: 26, borderRadius: "50%", background: "radial-gradient(ellipse, rgba(0,0,0,.4), rgba(0,0,0,0) 70%)", opacity: clamp(ia / 0.3), transform: `scale(${1 - 0.18 * hop})` }} />
    <Pop at={a + 0.15} y={790}><div style={{ font: "800 40px Montserrat", color: MUTED, letterSpacing: 3 }}>COMO SE FALA EM INGLÊS?</div></Pop>
    <Pop at={a + 0.2} y={885} dx={240}><div style={{ font: "400 118px Anton", color: "#fff", ...Outline, whiteSpace: "nowrap" } as any}>{w.pt}</div></Pop>
    <Confete t0={rv} x0={540} y0={1050} />
    <Onda rv={rv} y={1050} />
    {t >= c0 && t < rv && <Anel c0={c0} />}
    {rvd && <Center y={1050}><div style={{ transform: `scale(${0.4 + 0.6 * sp})` }}>
      <div style={{ background: GREEN, color: "#fff", font: "400 104px Anton", padding: "6px 48px", borderRadius: 34, boxShadow: `0 16px 40px rgba(0,0,0,.4), 0 0 60px ${GREEN}88`, whiteSpace: "nowrap", position: "relative", overflow: "hidden" }}>
        {w.en.toUpperCase()} <Emoji e="✅" size={80} style={{ verticalAlign: -6 }} />
        <div style={{ position: "absolute", top: 0, bottom: 0, left: `${-30 + 160 * clamp((t - rv - 0.15) / 0.6)}%`, width: "22%", transform: "skewX(-20deg)", background: "linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,.55), rgba(255,255,255,0))" }} /></div></div></Center>}
    {rvd && w.tip && t >= rv + 0.9 && <Pop at={rv + 0.9} y={1172}><Chip bg="rgba(8,20,48,.94)" size={34} style={{ border: `4px solid ${C_THE}` }}>{w.tip}</Chip></Pop>}
    </AbsoluteFill>
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

export const QuizPasseio: React.FC = () => (
  <Licao tm={TM}>
    <Bokeh />
    <Abertura />
    {WORDS.map((_, i) => <Pergunta key={i} i={i} />)}
    <Placar />
    <Chamada titulo="ACERTOU QUANTAS?" pedido="COMENTA SEU PLACAR" />
  </Licao>
);

export const QuizPasseioCapa: React.FC = () => (
  <CapaBase tm={TM} tt={TM.quiz[0].start + 0.5}>
    <Center y={260}><Chip bg={GREEN} size={40}>BÁSICO · A1 · PASSEIO</Chip></Center>
    <Center y={470}><div style={{ font: "400 150px Anton", color: YEL, ...Outline, textAlign: "center", lineHeight: 1 } as any}>COMO SE FALA<br />EM INGLÊS?</div></Center>
    <Center y={760}><div style={{ display: "flex", gap: 26 }}>{[WORDS[1], WORDS[3], WORDS[4], WORDS[6]].map((w) => <Emoji key={w.pt} e={w.e} size={100} />)}</div></Center>
    <Center y={930}><div style={{ font: "400 88px Anton", color: "#fff", ...Outline } as any}>fila? lembrança?</div></Center>
    <Center y={1080}><div style={{ font: "800 54px Montserrat", color: "#fff", ...Outline, WebkitTextStroke: "8px " + INK } as any}>7 PALAVRAS · 3 SEGUNDOS <Emoji e="⏱️" size={56} /></div></Center>
    <Center y={1220}><Chip bg={C_THE} size={46}>QUANTAS VOCÊ ACERTA?</Chip></Center>
  </CapaBase>
);
