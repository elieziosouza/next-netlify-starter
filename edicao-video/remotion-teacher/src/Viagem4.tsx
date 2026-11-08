// Mini curso "Inglês para viajar", Aula 4: Pagar a conta e a gorjeta (08/11/2026). Horizontal 1920x1080.
// Tempos: timings/viagem4.json (scripts/prep_aula.py + aulas/aula_viagem4.py). A simulação (garçom + respostas na voz dele) está na trilha de voz.
import React from "react";
import { AbsoluteFill, Img, staticFile, spring, Easing } from "remotion";
import TM from "./timings/viagem4.json";
import { useFonts, useT, env, Emoji, INK, YEL, MUTED, PT, C_A, C_AN, C_THE, GREEN, RED, clamp } from "./kit";
const T = TM.t as Record<string, number>;
const MX = 460, MW = 1400;
const F = (w: number, s: number) => `${w} ${s}px Montserrat`;
const OUT: React.CSSProperties = { WebkitTextStroke: "8px " + INK, paintOrder: "stroke fill" } as any;
const BG = "radial-gradient(ellipse 80% 90% at 60% 40%, #1f4d9e 0%, #123372 45%, #0a1a38 100%)";

const In: React.FC<{ at: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ at, children, style }) => {
  const { t, f, fps } = useT(); if (t < at) return null;
  const s = spring({ frame: f - Math.round(at * fps), fps, config: { damping: 16, stiffness: 140 } });
  return <div style={{ opacity: clamp((t - at) / 0.3), transform: `translateY(${20 * (1 - s)}px)`, ...style }}>{children}</div>;
};
const Scene: React.FC<{ a: number; b: number; children: React.ReactNode; gap?: number }> = ({ a, b, children, gap = 24 }) => {
  const { t } = useT(); const k = env(t, a, b, 0.35, 0.3); if (k <= 0) return null;
  return <div style={{ position: "absolute", left: MX, top: 120, width: MW, height: 760, opacity: k, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap }}>{children}</div>;
};
const Title: React.FC<{ children: React.ReactNode; color?: string; size?: number }> = ({ children, color = "#fff", size = 96 }) => (
  <div style={{ font: `400 ${size}px Anton`, color, ...OUT, lineHeight: 1.05, textAlign: "center" } as any}>{children}</div>
);
const Pill: React.FC<{ bg: string; color?: string; size?: number; children: React.ReactNode }> = ({ bg, color = "#fff", size = 40, children }) => (
  <div style={{ display: "inline-block", background: bg, color, font: F(800, size), padding: `${size * 0.3}px ${size * 0.75}px`, borderRadius: 999, whiteSpace: "nowrap", boxShadow: "0 8px 24px rgba(0,0,0,.35)" }}>{children}</div>
);
const Card: React.FC<{ children: React.ReactNode; border?: string; w?: number; pad?: string; dim?: boolean }> = ({ children, border = YEL, w, pad = "20px 36px", dim }) => (
  <div style={{ position: "relative", width: w, opacity: dim ? 0.45 : 1, transition: "opacity .2s" }}>
    {[18, 9].map((o) => <div key={o} style={{ position: "absolute", inset: 0, transform: `translate(${o}px, ${o}px)`, borderRadius: 26, border: `3px solid ${border}`, opacity: o === 18 ? 0.25 : 0.5, background: "rgba(8,20,48,.6)" }} />)}
    <div style={{ position: "relative", background: "rgba(8,20,48,.94)", border: `4px solid ${border}`, borderRadius: 26, padding: pad, boxShadow: "0 18px 40px rgba(0,0,0,.4)" }}>{children}</div>
  </div>
);
/** frase em inglês grande + tradução embaixo */
const Frase: React.FC<{ en: React.ReactNode; pt: string; at: number; w?: number; border?: string; e?: string; size?: number }> = ({ en, pt, at, w = 660, border = YEL, e, size = 54 }) => {
  const { t } = useT();
  return (<In at={at}><Card w={w} border={border}><div style={{ display: "flex", alignItems: "center", gap: 20 }}>
    {e && <Emoji e={e} size={size * 1.1} />}
    <div><div style={{ font: `400 ${size}px Anton`, color: "#fff", lineHeight: 1.1 }}>{en}</div><div style={{ font: F(700, 26), color: MUTED, marginTop: 4 }}>{pt}</div></div>
  </div></Card></In>);
};
/** pergunta do oficial → resposta */
const QA: React.FC<{ q: string; pt: string; a: string; at: number; aAt: number; a2?: string; a2At?: number }> = ({ q, pt, a, at, aAt, a2, a2At }) => {
  const { t } = useT();
  return (<In at={at}><div style={{ display: "flex", alignItems: "center", gap: 26, width: 1360 }}>
    <Card w={760} border={C_A} pad="12px 26px"><div style={{ font: `400 46px Anton`, color: "#fff" }}>{q}</div><div style={{ font: F(700, 23), color: MUTED }}>{pt}</div></Card>
    {t >= aAt && <div style={{ display: "flex", alignItems: "center", gap: 16, opacity: clamp((t - aAt) / 0.25) }}><span style={{ font: `400 50px Anton`, color: YEL }}>→</span>
      <Pill bg={GREEN} size={34}>{a}</Pill>{a2 && a2At && t >= a2At && <Pill bg={GREEN} size={28}>{a2}</Pill>}</div>}
  </div></In>);
};


const Intro = () => (
  <Scene a={0} b={T.conta}>
    <In at={0.1}><Pill bg={C_A} size={34}>✈️ INGLÊS PARA VIAJAR · MINI CURSO</Pill></In>
    <In at={0.6}><div style={{ display: "flex", gap: 50 }}><Emoji e="🧾" size={120} /><Emoji e="💳" size={120} /><Emoji e="💵" size={120} /></div></In>
    <In at={1.83}><Title size={110} color={YEL}>AULA 4 · PAGAR E GORJETA</Title></In>
    <In at={T.goal}><div style={{ font: F(700, 40), color: PT, textAlign: "center" }}>Pedir a conta, pagar e entender a gorjeta</div></In>
  </Scene>
);
const Conta = () => (
  <Scene a={T.conta} b={T.pag}>
    <In at={T.conta}><Pill bg={C_AN} size={44}>1 · A CONTA 🧾</Pill></In>
    <Frase at={T.c1} w={1000} e="🙋" en="Can I have the check, please?" pt="Pode me trazer a conta, por favor?" size={64} />
    <In at={T.cb}><div style={{ display: "flex", gap: 30 }}><Pill bg={C_A} size={44}>🇺🇸 check</Pill><Pill bg={C_THE} size={44}>🇬🇧 bill</Pill></div></In>
  </Scene>
);
const Pagar = () => (
  <Scene a={T.pag} b={T.gor}>
    <In at={T.pag}><Pill bg={C_A} size={44}>2 · NA HORA DE PAGAR 💳</Pill></In>
    <div style={{ display: "flex", flexDirection: "column", gap: 26, marginTop: 10 }}>
      <Frase at={T.p1} w={1000} e="💳" en="Can I pay by card?" pt="Posso pagar com cartão?" size={58} />
      <Frase at={T.p2} w={1000} e="➗" en="Can we split the bill?" pt="Podemos dividir a conta?" size={58} />
      <Frase at={T.e1} w={1000} e="❗" en="I think there's a mistake." pt="Acho que tem um erro." size={58} border={RED} />
    </div>
  </Scene>
);
const Gorjeta = () => (
  <Scene a={T.gor} b={T.tip}>
    <In at={T.gor}><Pill bg={C_THE} size={44}>3 · A GORJETA 💵</Pill></In>
    <Frase at={T.g1} w={1000} e="❓" en="Is the tip included?" pt="A gorjeta está incluída?" size={62} />
    <In at={T.gc}><Card border={YEL}><div style={{ display: "flex", alignItems: "center", gap: 20 }}><Emoji e="🇺🇸" size={70} />
      <div style={{ font: F(800, 36), color: "#fff" }}>Nos EUA a gorjeta costuma ficar entre <b style={{ color: YEL }}>15% e 20%</b></div></div></Card></In>
    <Frase at={T.g2} w={1000} e="🪙" en="Keep the change." pt="Pode ficar com o troco." size={62} />
  </Scene>
);
const Dica = () => (
  <Scene a={T.tip} b={T.sim}>
    <In at={T.tip}><Title size={110} color={YEL}>💡 DICA DE OURO</Title></In>
    <In at={T.tip + 1.3}><div style={{ font: F(700, 40), color: PT }}>Antes de pagar, procure na conta:</div></In>
    <In at={46.5}><div style={{ display: "flex", gap: 30 }}><Pill bg={C_A} size={60}>service charge</Pill><Pill bg={C_AN} size={60}>gratuity</Pill></div></In>
    <In at={50.31}><div style={{ font: F(700, 40), color: PT }}>Se estiver escrito, a gorjeta <b style={{ color: "#fff" }}>já está incluída</b>.</div></In>
    <In at={T.train}><Pill bg={YEL} color={INK} size={40}>AGORA VAMOS TREINAR</Pill></In>
  </Scene>
);
const SIM: [number, number, "r" | "v", string][] = [[58.25, 59.4, "r", "How was everything?"], [59.85, 62.65, "v", "It was great! Can I have the check, please?"], [63.1, 64.55, "r", "Sure, here you go."], [65.0, 66.4, "v", "Is the tip included?"], [66.85, 68.8, "r", "No, it's not included."], [69.25, 70.7, "v", "Can I pay by card?"], [71.15, 73.05, "r", "Of course. Just tap here."], [73.5, 74.29, "v", "Thank you!"], [74.74, 75.87, "r", "Have a great night!"]];
const Simulacao = () => {
  const { t } = useT(); let lr = -1, lv = -1; SIM.forEach((s, k) => { if (t >= s[0] - 0.1) { if (s[2] === "r") lr = k; else lv = k; } });
  const r = lr >= 0 ? SIM[lr] : null, v = lv >= 0 ? SIM[lv] : null;
  const talking = (s: any) => s && t >= s[0] && t <= s[1];
  return (<Scene a={T.sim} b={T.quiz} gap={34}>
    <In at={T.sim}><Pill bg={C_THE} size={40}>SIMULAÇÃO · A CONTA 🧾</Pill></In>
    <div style={{ display: "flex", alignItems: "center", gap: 30, width: 1300 }}>
      <div style={{ textAlign: "center", width: 200 }}><Emoji e="🧑‍🍳" size={150} style={{ transform: `scale(${talking(r) ? 1 + 0.04 * Math.sin(t * 20) : 1})` }} /><div style={{ font: F(800, 26), color: MUTED }}>WAITER</div></div>
      {r && <Card w={1060} border={C_A} dim={!talking(r) && !!v && v[0] > r[0]}><div style={{ font: `400 62px Anton`, color: "#fff" }}>{r[3]}</div></Card>}
    </div>
    <div style={{ display: "flex", alignItems: "center", gap: 30, width: 1300, justifyContent: "flex-end", minHeight: 180 }}>
      {v && <><Card w={1060} border={GREEN} dim={!talking(v) && !!r && r[0] > v[0]}><div style={{ font: `400 62px Anton`, color: YEL }}>{v[3]}</div></Card>
        <div style={{ textAlign: "center", width: 200 }}><Emoji e="🙋" size={130} style={{ transform: `scale(${talking(v) ? 1 + 0.04 * Math.sin(t * 20) : 1})` }} /><div style={{ font: F(800, 26), color: MUTED }}>VOCÊ</div></div></>}
    </div>
  </Scene>);
};
const QuizH = () => {
  const { t } = useT(); const { start: c0, reveal: rv } = TM.quiz[0]; const rvd = t >= rv; const n = Math.ceil(rv - t);
  const opt = (s: string, good: boolean, i: number) => (<In key={s} at={T.qopt + i * 1.6}><div style={{ display: "flex", alignItems: "center", gap: 18, width: 1100, padding: "16px 30px", borderRadius: 22,
    background: rvd ? (good ? GREEN : "rgba(8,20,48,.7)") : "#fff", color: rvd ? "#fff" : INK, font: F(800, 44), opacity: rvd && !good ? 0.55 : 1 }}>
    <span style={{ width: 60, height: 60, borderRadius: "50%", background: rvd ? "rgba(255,255,255,.25)" : INK, color: "#fff", display: "grid", placeItems: "center", font: F(800, 32), flex: "none" }}>{"AB"[i]}</span>
    <span style={{ textDecoration: rvd && !good ? "line-through" : "none" }}>{s}</span>{rvd && <span style={{ marginLeft: "auto" }}>{good ? "✅" : "❌"}</span>}</div></In>);
  return (<Scene a={T.quiz} b={T.pdf} gap={28}>
    <In at={T.quiz}><Pill bg={YEL} color={INK} size={52}>QUIZ</Pill></In>
    <In at={T.q1}><div style={{ display: "flex", alignItems: "center", gap: 24 }}><Emoji e="➗" size={100} /><Card border={C_A}><span style={{ font: `400 72px Anton`, color: "#fff" }}>Você quer dividir a conta…</span></Card></div></In>
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>{opt("Keep the change.", false, 0)}{opt("Can we split the bill?", true, 1)}</div>
    <div style={{ height: 120, display: "grid", placeItems: "center" }}>
      {t >= c0 && !rvd && <div style={{ width: 110, height: 110, borderRadius: "50%", border: `8px solid ${YEL}`, display: "grid", placeItems: "center", font: `400 70px Anton`, color: "#fff" }}>{n}</div>}
      {t >= T.after && <In at={T.after}><Pill bg="rgba(8,20,48,.92)" size={34}>Keep the change → é para <b style={{ color: YEL }}>deixar o troco</b></Pill></In>}
    </div>
  </Scene>);
};
const Fim = () => (
  <Scene a={T.pdf} b={TM.total + 1} gap={30}>
    <In at={T.pdf}><Card border={YEL}><div style={{ display: "flex", alignItems: "center", gap: 24 }}><Emoji e="📄" size={90} />
      <div><div style={{ font: `400 60px Anton`, color: "#fff" }}>NO PDF DA AULA</div><div style={{ font: F(700, 30), color: MUTED }}>mais frases para pagar + vocabulário</div></div></div></Card></In>
    <In at={T.pdf + 3.0}><Pill bg={C_AN} size={44}>PRÓXIMA AULA: 🗺️ NA RUA</Pill></In>
    <In at={T.cta}><Pill bg="#fff" color={INK} size={44}>FOLLOW @teacher.eliezio</Pill></In>
  </Scene>
);

// ---------------------------------------------------------------- moldura: avatar à esquerda, legenda embaixo, barra de progresso
const Avatar = () => {
  const { t, f } = useT(); const inSim = t >= T.sim && t < T.quiz; const amp = inSim ? 0 : (TM.amp[Math.min(f, TM.amp.length - 1)] ?? 0);
  const ex = TM.expr as [number, number][]; let i = 0; ex.forEach((e, k) => { if (e[0] <= t) i = k; });
  const cur = ex[i][1], prv = i ? ex[i - 1][1] : cur, k = clamp((t - ex[i][0]) / 0.18); const bob = -6 * amp;
  return (<div style={{ position: "absolute", left: 230 - 165, top: 520 - 165 + bob, width: 330, height: 330 }}>
    <div style={{ position: "absolute", inset: -30, borderRadius: "50%", background: YEL, opacity: (80 + 80 * amp) / 255, filter: "blur(20px)" }} />
    <div style={{ position: "absolute", inset: 0, borderRadius: "50%", background: YEL }} />
    <div style={{ position: "absolute", left: 15, top: 15, width: 300, height: 300 }}>
      <Img src={staticFile(`av/av3d_${prv}.png`)} style={{ position: "absolute", width: 300, height: 300 }} />
      <Img src={staticFile(`av/av3d_${cur}.png`)} style={{ position: "absolute", width: 300, height: 300, opacity: k }} />
    </div>
    <div style={{ position: "absolute", top: 350, left: -40, right: -40, textAlign: "center", font: F(800, 26), color: "#fff" }}>Teacher Eliezio</div>
    <div style={{ position: "absolute", top: 388, left: -40, right: -40, textAlign: "center", font: F(700, 22), color: MUTED }}>@teacher.eliezio</div>
  </div>);
};
const Caption = () => {
  const { t } = useT(); const c = (TM.caps as any[]).find((c) => t >= c.start - 0.05 && t < c.until); if (!c) return null;
  const k = Easing.out(Easing.cubic)(clamp((t - c.start) / 0.25));
  const line = (ws: any[], size: number, base: string, hl: boolean) => <div style={{ width: "100%", font: F(800, size), color: base, textAlign: "center", lineHeight: 1.35, ...OUT, WebkitTextStroke: `${size * 0.14}px ${INK}` } as any}>
    {ws.map((w: any, i: number) => <React.Fragment key={i}><span style={{ color: hl && t >= w.t - 0.02 ? YEL : base }}>{w.w}</span>{" "}</React.Fragment>)}</div>;
  return (<div style={{ position: "absolute", left: MX, width: MW, top: 905, opacity: k, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
    {line(c.words, c.lang === "en" ? 44 : 38, c.lang === "en" ? "#fff" : PT, c.lang === "en")}
    {c.pt && t >= c.pt.start - 0.05 && line(c.pt.words, 34, PT, false)}
  </div>);
};

export const Viagem4: React.FC = () => {
  useFonts(); const { t } = useT();
  return (<AbsoluteFill style={{ background: BG }}>
    <AbsoluteFill style={{ backgroundImage: "linear-gradient(rgba(255,255,255,.03) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,.03) 2px, transparent 2px)", backgroundSize: "60px 60px" }} />
    <div style={{ position: "absolute", left: MX, width: MW, top: 36, display: "flex", justifyContent: "center" }}><div style={{ background: "#fff", color: INK, font: F(800, 26), padding: "12px 36px", borderRadius: 30 }}>✈️ INGLÊS PARA VIAJAR · Teacher Eliezio</div></div>
    <div style={{ position: "absolute", left: 60, top: 36 }}><Pill bg={C_A} size={26}>AULA 4 de 7</Pill></div>
    <Intro /><Conta /><Pagar /><Gorjeta /><Dica /><Simulacao /><QuizH /><Fim />
    <Avatar /><Caption />
    <div style={{ position: "absolute", left: 60, right: 60, top: 1050, height: 10, borderRadius: 5, background: "#3c5480" }}><div style={{ width: `${clamp(t / TM.total) * 100}%`, height: 10, borderRadius: 5, background: YEL }} /></div>
  </AbsoluteFill>);
};
export const Viagem4Capa: React.FC = () => {
  useFonts();
  return (<AbsoluteFill style={{ background: BG, alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 26 }}>
    <Pill bg={C_A} size={36}>✈️ INGLÊS PARA VIAJAR · AULA 4</Pill>
    <div style={{ display: "flex", gap: 40 }}><Emoji e="🧾" size={130} /><Emoji e="💳" size={130} /><Emoji e="💵" size={130} /></div>
    <Title size={150} color={YEL}>A CONTA E A GORJETA</Title>
    <Title size={70}>Pedir a conta, pagar e dar gorjeta</Title>
    <Pill bg="#fff" color={INK} size={32}>Teacher Eliezio</Pill>
  </AbsoluteFill>);
};
export const Viagem4Capa916: React.FC = () => {
  useFonts();
  return (<AbsoluteFill style={{ background: BG, alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 34 }}>
    <AbsoluteFill style={{ backgroundImage: "linear-gradient(rgba(255,255,255,.04) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,.04) 2px, transparent 2px)", backgroundSize: "60px 60px" }} />
    <Pill bg={C_A} size={38}>✈️ INGLÊS PARA VIAJAR</Pill>
    <div style={{ font: F(800, 40), color: "#fff", letterSpacing: 6 }}>AULA 4 DE 7</div>
    <div style={{ display: "flex", gap: 36 }}><Emoji e="🧾" size={140} /><Emoji e="💳" size={140} /><Emoji e="💵" size={140} /></div>
    <Title size={170} color={YEL}>A CONTA<br />E A GORJETA</Title>
    <Title size={76}>Pedir a conta, pagar<br />e dar gorjeta</Title>
    <div style={{ marginTop: 40, display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
      <div style={{ width: 300, height: 300, borderRadius: "50%", background: YEL, position: "relative", boxShadow: "0 0 0 16px rgba(255,214,64,.25)" }}>
        <Img src={staticFile("av/av3d_1.png")} style={{ position: "absolute", left: 14, top: 14, width: 272, height: 272 }} /></div>
      <Pill bg="#fff" color={INK} size={36}>Teacher Eliezio</Pill>
    </div>
  </AbsoluteFill>);
};
