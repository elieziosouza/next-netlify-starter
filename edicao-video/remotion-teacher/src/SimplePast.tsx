// Aula de sala HORIZONTAL (1920x1080) "Simple Past · What did you do last weekend?" (7ª e 8ª série, 06/11/2026), para compartilhar a tela.
// Pouco movimento (o compartilhamento trava com animação rápida), letra grande, sem contador e sem respostas.
// No fim, duas telas paradas para copiar no caderno: EXPLICAÇÃO e LIÇÃO (também exportadas como imagens). Tempos: timings/simplepast.json.
import React from "react";
import { AbsoluteFill, Img, staticFile, spring, Easing } from "remotion";
import TM from "./timings/simplepast.json";
import { useFonts, useT, env, Emoji, INK, YEL, MUTED, PT, C_A, C_AN, C_THE, GREEN, RED, NAVY, clamp } from "./kit";
const T = TM.t as Record<string, number>;
const MX = 460, MW = 1400;                                            // área principal (à direita do avatar)
const F = (w: number, s: number) => `${w} ${s}px Montserrat`;
const OUT: React.CSSProperties = { WebkitTextStroke: "8px " + INK, paintOrder: "stroke fill" } as any;

/** entrada curta e suave (sem desfoque de movimento): sobe 20 px e aparece em 0,35 s */
const In: React.FC<{ at: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ at, children, style }) => {
  const { t, f, fps } = useT(); if (t < at) return null;
  const s = spring({ frame: f - Math.round(at * fps), fps, config: { damping: 16, stiffness: 140 } });
  return <div style={{ opacity: clamp((t - at) / 0.3), transform: `translateY(${20 * (1 - s)}px)`, ...style }}>{children}</div>;
};
const Scene: React.FC<{ a: number; b: number; children: React.ReactNode }> = ({ a, b, children }) => {
  const { t } = useT(); const k = env(t, a, b, 0.35, 0.3); if (k <= 0) return null;
  return <div style={{ position: "absolute", left: MX, top: 150, width: MW, height: 720, opacity: k, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 26 }}>{children}</div>;
};
const Title: React.FC<{ children: React.ReactNode; color?: string; size?: number }> = ({ children, color = "#fff", size = 96 }) => (
  <div style={{ font: `400 ${size}px Anton`, color, ...OUT, lineHeight: 1.05, textAlign: "center" } as any}>{children}</div>
);
const Pill: React.FC<{ bg: string; color?: string; size?: number; children: React.ReactNode }> = ({ bg, color = "#fff", size = 40, children }) => (
  <div style={{ display: "inline-block", background: bg, color, font: F(800, size), padding: `${size * 0.3}px ${size * 0.75}px`, borderRadius: 999, whiteSpace: "nowrap", boxShadow: "0 8px 24px rgba(0,0,0,.35)" }}>{children}</div>
);
/** cartão com duas camadas douradas por trás (padrão do canal), parado */
const Card: React.FC<{ children: React.ReactNode; border?: string; w?: number; pad?: string }> = ({ children, border = YEL, w, pad = "26px 44px" }) => (
  <div style={{ position: "relative", width: w }}>
    {[24, 12].map((o) => <div key={o} style={{ position: "absolute", inset: 0, transform: `translate(${o}px, ${o}px)`, borderRadius: 30, border: `3px solid ${border}`, opacity: o === 24 ? 0.25 : 0.5, background: "rgba(8,20,48,.6)" }} />)}
    <div style={{ position: "relative", background: "rgba(8,20,48,.94)", border: `4px solid ${border}`, borderRadius: 30, padding: pad, boxShadow: "0 18px 40px rgba(0,0,0,.4)" }}>{children}</div>
  </div>
);
const Verb: React.FC<{ base: string; past: React.ReactNode; color: string; at: number; size?: number }> = ({ base, past, color, at, size = 78 }) => (
  <In at={at}><div style={{ display: "flex", alignItems: "center", gap: 26, font: `400 ${size}px Anton`, color: "#fff" }}>
    <span style={{ minWidth: 220, textAlign: "right" }}>{base}</span><span style={{ color: YEL, fontSize: size * 0.8 }}>→</span><span style={{ minWidth: 260 }}>{past}</span>
  </div></In>
);
const End: React.FC<{ c: string; children: React.ReactNode }> = ({ c, children }) => <span style={{ background: c, borderRadius: 12, padding: "0 10px", margin: "0 2px", color: "#fff" }}>{children}</span>;

// ---------------------------------------------------------------- cenas da aula
const Intro = () => (
  <Scene a={0} b={T.words}>
    <In at={0.1}><Pill bg={C_A} size={36}>SIMPLE PAST</Pill></In>
    <In at={1.6}><Title size={130} color={YEL}>THE SIMPLE PAST</Title></In>
    <In at={3.2}><Title size={76}>What did you do last weekend?</Title></In>
    <In at={4.0}><div style={{ display: "flex", gap: 40 }}><Emoji e="⚽" size={96} /><Emoji e="🏖️" size={96} /><Emoji e="🍕" size={96} /><Emoji e="🎬" size={96} /></div></In>
    <In at={5.1}><div style={{ font: F(700, 42), color: PT }}>O que você fez no último fim de semana?</div></In>
  </Scene>
);
const Words = () => {
  const ws: [string, string, number][] = [["yesterday", "ontem", T.w1], ["last night", "ontem à noite", T.w2], ["last weekend", "no último fim de semana", T.w3], ["two days ago", "dois dias atrás", T.w4]];
  return (<Scene a={T.words} b={T.reg}>
    <In at={T.words}><Title size={84}>FINISHED ACTIONS · <span style={{ color: YEL }}>PAST</span></Title></In>
    <In at={T.words + 0.4}><div style={{ font: F(700, 38), color: PT }}>Ações que começaram e terminaram no passado</div></In>
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 28, marginTop: 10 }}>
      {ws.map(([en, pt, at]) => <In key={en} at={at}><Card w={600} pad="18px 30px"><div style={{ font: `400 64px Anton`, color: YEL }}>{en}</div><div style={{ font: F(700, 32), color: MUTED }}>{pt}</div></Card></In>)}
    </div>
  </Scene>);
};
const Regular = () => (
  <Scene a={T.reg} b={T.irr}>
    <In at={T.reg}><Pill bg={C_A} size={44}>RULE 1 · REGULAR VERBS</Pill></In>
    <div style={{ display: "flex", gap: 60, alignItems: "flex-start" }}>
      <In at={T.reg + 1.2}><Card border={C_A}><div style={{ font: F(800, 40), color: MUTED, textAlign: "center", marginBottom: 14 }}>+ <span style={{ color: "#fff" }}>ED</span></div>
        <Verb base="play" past={<>play<End c={C_A}>ed</End></>} color={C_A} at={T.r1} /><Verb base="watch" past={<>watch<End c={C_A}>ed</End></>} color={C_A} at={T.r2} /></Card></In>
      {T.rE <= 999 && <In at={T.rE}><Card border={C_AN}><div style={{ font: F(800, 32), color: MUTED, textAlign: "center", marginBottom: 14 }}>termina em <span style={{ color: "#fff" }}>E</span>: só <span style={{ color: "#fff" }}>+ D</span></div>
        <Verb base="like" past={<>like<End c={C_AN}>d</End></>} color={C_AN} at={T.rE1} size={70} />
        <In at={T.rY}><div style={{ font: F(800, 32), color: MUTED, textAlign: "center", margin: "22px 0 14px" }}>consoante + <span style={{ color: "#fff" }}>Y</span>: troca por <span style={{ color: "#fff" }}>IED</span></div></In>
        <Verb base="study" past={<>stud<End c={C_THE}>ied</End></>} color={C_THE} at={T.rY1} size={70} /></Card></In>}
    </div>
    <In at={37.7}><div style={{ font: F(700, 38), color: PT }}>Nos regulares, coloque <b style={{ color: "#fff" }}>-ED</b> no final.</div></In>
  </Scene>
);
const Irregular = () => {
  const vs: [string, string, number][] = [["go", "went", T.i1], ["eat", "ate", T.i2], ["have", "had", T.i3], ["see", "saw", T.i4]];
  const { t } = useT(); const same = t >= T.same;
  return (<Scene a={T.irr} b={T.neg}>
    <In at={T.irr}><Pill bg={C_THE} size={44}>RULE 2 · IRREGULAR VERBS</Pill></In>
    {!same && <><Card border={C_THE} pad="22px 60px"><div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", columnGap: 90, rowGap: 6 }}>
      {vs.map(([b, p, at]) => <Verb key={b} base={b} past={<span style={{ color: YEL }}>{p}</span>} color={C_THE} at={at} size={72} />)}</div></Card>
      <In at={48.9}><Pill bg={YEL} color={INK} size={38}>MUDAM: A GENTE DECORA!</Pill></In></>}
    {same && <><In at={T.same}><Title size={70}>THE SAME FOR <span style={{ color: YEL }}>EVERYBODY</span></Title></In>
      <Card border={YEL} pad="22px 60px">{["I", "She", "They"].map((p, i) => <In key={p} at={T.s1 + i * 0.7}><div style={{ font: `400 72px Anton`, color: "#fff" }}>{p} <span style={{ color: YEL }}>played</span></div></In>)}</Card>
      <In at={55.4}><div style={{ font: F(700, 38), color: PT }}>No passado, o verbo é igual para todos (sem S no he, she, it).</div></In></>}
  </Scene>);
};
const Negative = () => (
  <Scene a={T.neg} b={T.q}>
    <In at={T.neg}><Pill bg={RED} size={44}>RULE 3 · NEGATIVE</Pill></In>
    <In at={60.1}><Title size={90}><span style={{ color: YEL }}>DIDN'T</span> + VERBO NORMAL</Title></In>
    <div style={{ display: "flex", gap: 50 }}>
      <In at={T.n1}><Card border={GREEN}><div style={{ font: `400 78px Anton`, color: "#fff" }}>I <span style={{ color: YEL }}>didn't</span> go. <Emoji e="✅" size={64} /></div></Card></In>
      <In at={T.n2}><Card border={RED}><div style={{ font: `400 78px Anton`, color: "#fff" }}>I didn't <span style={{ color: MUTED, textDecoration: "line-through", textDecorationColor: RED, textDecorationThickness: 8 }}>went</span>. <Emoji e="❌" size={64} /></div></Card></In>
    </div>
    <In at={65.6}><div style={{ font: F(700, 38), color: PT }}>Na negativa: <b style={{ color: "#fff" }}>didn't</b> e o verbo normal.</div></In>
  </Scene>
);
const Question = () => (
  <Scene a={T.q} b={T.turn}>
    <In at={T.q}><Pill bg={C_AN} size={44}>RULE 4 · QUESTIONS</Pill></In>
    <In at={70.5}><Title size={90}><span style={{ color: YEL }}>DID</span> + VERBO NORMAL?</Title></In>
    <In at={T.q1}><Card border={C_AN}><div style={{ font: `400 82px Anton`, color: "#fff" }}><span style={{ color: YEL }}>Did</span> you watch the movie?</div></Card></In>
    <div style={{ display: "flex", gap: 40 }}>
      <In at={T.q2}><Pill bg={GREEN} size={46}>Yes, I did.</Pill></In><In at={T.q3}><Pill bg={RED} size={46}>No, I didn't.</Pill></In>
    </div>
    <In at={76.3}><div style={{ font: F(700, 38), color: PT }}>Na pergunta: <b style={{ color: "#fff" }}>Did</b> e o verbo normal.</div></In>
  </Scene>
);
const Turn = () => (
  <Scene a={T.turn} b={T.copy1}>
    <In at={T.turn}><Title size={110} color={YEL}>NOW IT'S YOUR TURN!</Title></In>
    <div style={{ display: "flex", gap: 40, marginTop: 10 }}>
      {[["📓", "COPIE NO CADERNO", 80.6], ["✏️", "RESPONDA AS 5 QUESTÕES", 83.0], ["🏫", "TRAGA NA PRÓXIMA AULA", 85.1]].map(([e, s, at]) =>
        <In key={s as string} at={at as number}><Card w={400} pad="24px 24px"><div style={{ textAlign: "center" }}><Emoji e={e as string} size={90} /><div style={{ font: F(800, 32), color: "#fff", marginTop: 14 }}>{s}</div></div></Card></In>)}
    </div>
  </Scene>
);

// ---------------------------------------------------------------- telas para copiar (paradas, tela cheia, sem avatar nem legenda)
const CopyHead: React.FC<{ tag: string; title: string }> = ({ tag, title }) => (
  <div style={{ position: "absolute", left: 80, right: 80, top: 40, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
    <div><div style={{ font: F(800, 26), color: YEL, letterSpacing: 4 }}>ENGLISH · SIMPLE PAST · {tag}</div><div style={{ font: `400 64px Anton`, color: "#fff" }}>{title}</div></div>
    <Pill bg={RED} size={34}>⏸ PAUSE E COPIE NO CADERNO</Pill>
  </div>
);
const Line: React.FC<{ children: React.ReactNode; size?: number; color?: string }> = ({ children, size = 30, color = "#fff" }) => <div style={{ font: F(700, size), color, lineHeight: 1.5 }}>{children}</div>;
const B: React.FC<{ children: React.ReactNode; c?: string }> = ({ children, c = YEL }) => <b style={{ color: c, fontWeight: 800 }}>{children}</b>;
export const Explicacao: React.FC = () => (
  <AbsoluteFill style={{ background: "#0a1a38" }}>
    <CopyHead tag="EXPLICAÇÃO" title="Simple Past · ações terminadas no passado" />
    <div style={{ position: "absolute", left: 80, right: 80, top: 190, bottom: 40, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 40 }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        <Card w={850} pad="14px 30px"><Line><B>Palavras de passado:</B> yesterday (ontem) · last night (ontem à noite) · last weekend (no último fim de semana) · two days ago (dois dias atrás)</Line></Card>
        <Card w={850} pad="14px 30px" border={C_A}><Line><B c={C_A}>1. Regulares: + ED</B></Line><Line>play → play<B>ed</B> · watch → watch<B>ed</B></Line>
          <Line>termina em E: + D → like → like<B>d</B></Line><Line>consoante + Y: Y vira IED → stud<B>ied</B></Line></Card>
        <Card w={850} pad="14px 30px" border={C_THE}><Line><B c={C_THE}>2. Irregulares: mudam (decorar)</B></Line><Line>go → <B>went</B> · eat → <B>ate</B> · have → <B>had</B> · see → <B>saw</B></Line>
          <Line size={27} color={MUTED}>O verbo é igual para todos: I played · she played · they played</Line></Card>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        <Card w={850} pad="14px 30px" border={RED}><Line><B c={RED}>3. Negativa: DIDN'T + verbo normal</B></Line><Line>I <B>didn't</B> go. (nunca: I didn't went)</Line><Line>She <B>didn't</B> play.</Line></Card>
        <Card w={850} pad="14px 30px" border={C_AN}><Line><B c={C_AN}>4. Pergunta: DID + verbo normal</B></Line><Line><B>Did</B> you watch the movie?</Line><Line>Yes, I did. / No, I didn't.</Line></Card>
        <Card w={850} pad="14px 30px"><Line size={29}><B>Lembre:</B> regular + -ed (play → played). Irregular muda (go → went, eat → ate). Depois de <B>did / didn't</B>, o verbo fica normal: I didn't <B>go</B>.</Line></Card>
      </div>
    </div>
  </AbsoluteFill>
);
const QS: [string, string[]][] = [["Yesterday I ______ soccer with my friends.", ["play", "played", "playing", "plays"]], ["She ______ to the beach last weekend.", ["go", "goes", "went", "goed"]],
  ["We ______ pizza last night.", ["ate", "eat", "eated", "eating"]], ["They ______ study for the test yesterday.", ["don't", "didn't", "doesn't", "not"]], ["______ you watch the movie last night?", ["Do", "Does", "Are", "Did"]]];
export const Licao: React.FC = () => (
  <AbsoluteFill style={{ background: "#0a1a38" }}>
    <CopyHead tag="LIÇÃO" title="Choose the correct answer." />
    <div style={{ position: "absolute", left: 80, right: 80, top: 200, display: "flex", flexDirection: "column", gap: 18 }}>
      {QS.map(([q, os], i) => <Card key={i} w={1760} pad="14px 30px"><div style={{ display: "flex", alignItems: "center", gap: 26 }}>
        <div style={{ width: 62, height: 62, borderRadius: "50%", background: YEL, color: INK, font: `400 40px Anton`, display: "grid", placeItems: "center", flex: "none" }}>{i + 1}</div>
        <div style={{ font: F(800, 36), color: "#fff", flex: 1 }}>{q}</div>
        <div style={{ display: "flex", gap: 14 }}>{os.map((o, j) => <div key={j} style={{ font: F(700, 30), color: "#fff", border: "2px solid rgba(255,255,255,.35)", borderRadius: 14, padding: "6px 16px", minWidth: 150 }}><b style={{ color: YEL }}>{"abcd"[j]}</b>&nbsp; {o}</div>)}</div>
      </div></Card>)}
      <div style={{ font: F(700, 30), color: MUTED, marginTop: 6 }}>Dica: yesterday, last night e last weekend pedem o passado. · Traga respondida na próxima aula.</div>
    </div>
  </AbsoluteFill>
);

// ---------------------------------------------------------------- moldura: avatar à esquerda, legenda embaixo, barra de progresso
const Avatar = () => {
  const { t, f } = useT(); const amp = TM.amp[Math.min(f, TM.amp.length - 1)] ?? 0;
  const ex = TM.expr as [number, number][]; let i = 0; ex.forEach((e, k) => { if (e[0] <= t) i = k; });
  const cur = ex[i][1], prv = i ? ex[i - 1][1] : cur, k = clamp((t - ex[i][0]) / 0.18); const bob = -6 * amp;
  return (<div style={{ position: "absolute", left: 230 - 165, top: 560 - 165 + bob, width: 330, height: 330 }}>
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
const HL: Record<string, string> = { "ED.": C_A, "D.": C_AN, "D,": C_AN, "DIDN'T,": RED, "DIDN'T": RED, "DID,": C_AN, "DID": C_AN };
const Caption = () => {
  const { t } = useT(); const c = (TM.caps as any[]).find((c) => t >= c.start - 0.05 && t < c.until); if (!c || t > T.copy1 - 0.2) return null;
  const k = Easing.out(Easing.cubic)(clamp((t - c.start) / 0.25)); const pt = c.pt;
  const line = (ws: any[], size: number, base: string, hl: boolean) => <div style={{ width: "100%", font: F(800, size), color: base, textAlign: "center", lineHeight: 1.35, ...OUT, WebkitTextStroke: `${size * 0.14}px ${INK}` } as any}>
    {ws.map((w: any, i: number) => { const said = hl && t >= w.t - 0.02; const box = hl ? HL[w.w.toUpperCase()] : undefined;
      return <React.Fragment key={i}><span style={{ marginRight: size * 0.06, color: said ? YEL : base }}>{box ? <span style={{ background: box, color: "#fff", borderRadius: 8, padding: "0 8px", WebkitTextStroke: "0px" } as any}>{w.w}</span> : w.w}</span>{" "}</React.Fragment>; })}</div>;
  return (<div style={{ position: "absolute", left: MX, width: MW, top: 895, opacity: k, display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
    {line(c.words, c.lang === "en" ? 46 : 40, c.lang === "en" ? "#fff" : PT, c.lang === "en")}
    {pt && t >= pt.start - 0.05 && line(pt.words, 36, PT, false)}
  </div>);
};
export const SimplePast: React.FC = () => {
  useFonts(); const { t } = useT(); const copy = t >= T.copy1;
  return (<AbsoluteFill style={{ background: "radial-gradient(ellipse 80% 90% at 60% 40%, #1f4d9e 0%, #123372 45%, #0a1a38 100%)" }}>
    <AbsoluteFill style={{ backgroundImage: "linear-gradient(rgba(255,255,255,.03) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,.03) 2px, transparent 2px)", backgroundSize: "60px 60px" }} />
    {!copy && <>
      <div style={{ position: "absolute", left: MX, width: MW, top: 40, display: "flex", justifyContent: "center" }}><div style={{ background: "#fff", color: INK, font: F(800, 26), padding: "14px 40px", borderRadius: 30 }}>ENGLISH CLASS · Teacher Eliezio</div></div>
      <div style={{ position: "absolute", left: 60, top: 40 }}><Pill bg={C_AN} size={26}>7ª e 8ª série</Pill></div>
      <Intro /><Words /><Regular /><Irregular /><Negative /><Question /><Turn />
      <Avatar /><Caption />
      <div style={{ position: "absolute", left: 60, right: 60, top: 1050, height: 10, borderRadius: 5, background: "#3c5480" }}><div style={{ width: `${clamp(t / T.copy1) * 100}%`, height: 10, borderRadius: 5, background: YEL }} /></div>
    </>}
    {copy && t < T.copy2 && <Explicacao />}
    {t >= T.copy2 && <Licao />}
  </AbsoluteFill>);
};
export const ExplicacaoStill: React.FC = () => { useFonts(); return <Explicacao />; };
export const LicaoStill: React.FC = () => { useFonts(); return <Licao />; };
export const SimplePastCapa: React.FC = () => {
  useFonts();
  return (<AbsoluteFill style={{ background: "radial-gradient(ellipse 80% 90% at 60% 40%, #1f4d9e 0%, #123372 45%, #0a1a38 100%)", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 24 }}>
    <Pill bg={C_AN} size={34}>7ª e 8ª série · ENGLISH CLASS</Pill>
    <Title size={170} color={YEL}>SIMPLE PAST</Title>
    <Title size={80}>What did you do last weekend?</Title>
    <div style={{ display: "flex", gap: 30 }}><Pill bg={C_A} size={36}>play → played</Pill><Pill bg={C_THE} size={36}>go → went</Pill><Pill bg={RED} size={36}>didn't + verbo</Pill><Pill bg={C_AN} size={36}>Did...?</Pill></div>
  </AbsoluteFill>);
};
