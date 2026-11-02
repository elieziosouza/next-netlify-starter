// Kit das aulas do Teacher Eliezio no Remotion: fundo, avatar, legenda karaokê, quiz com contador e confete, chamada final.
// Cada aula passa os seus tempos (timings/*.json, gerados por scripts/prep_aula.py) pelo <Licao tm={...}>.
import React, { useState, createContext, useContext } from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig, spring, Easing, random, delayRender, continueRender } from "remotion";
import { CameraMotionBlur } from "@remotion/motion-blur";

export const NAVY = "#0c1c3a", INK = "#101624", YEL = "#ffd640", MUTED = "#b4c4e0", PT = "#ffe696";
export const C_A = "#4096ff", C_AN = "#34be6e", C_THE = "#ec5454", GREEN = "#2eb85c", GREY = "#5a6888", RED = "#dc2828";
export const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
type TMT = { fps: number; total: number; quiz: { start: number; reveal: number }[]; caps: any[]; expr: [number, number][]; amp: number[]; t: Record<string, number> };
const Ctx = createContext<{ tm: TMT; hl: Record<string, string> }>(null as any);
export const useTM = () => useContext(Ctx).tm;
// ---------- fontes (espera carregar antes de desenhar o quadro)
const FONTS: [string, string, string][] = [["Anton", "Anton-Regular.ttf", "400"], ["Montserrat", "Montserrat-Bold.ttf", "700"],
  ["Montserrat", "Montserrat-ExtraBold.ttf", "800"], ["Montserrat", "Montserrat-Black.ttf", "900"]];
export const useFonts = () => {
  const [h] = useState(() => delayRender("fontes"));
  useState(() => {
    Promise.all(FONTS.map(([fam, file, w]) => new FontFace(fam, `url(${staticFile("fonts/" + file)})`, { weight: w }).load().then((f) => (document.fonts as any).add(f))))
      .then(() => continueRender(h));
    return 0;
  });
};

// ---------- utilidades de animação
export const useT = () => { const f = useCurrentFrame(); const { fps } = useVideoConfig(); return { t: f / fps, fps, f }; };
/** entrada com mola: escala 0.6→1 com leve passada, sai do desfoque e desliza de baixo */
export const usePop = (at: number, opts: { damping?: number; from?: number; dx?: number; dy?: number } = {}) => {
  const { f, fps } = useT();
  const s = spring({ frame: f - Math.round(at * fps), fps, config: { damping: opts.damping ?? 11, stiffness: 170, mass: 0.8 } });
  const lin = clamp((f - at * fps) / (0.3 * fps));
  return { s, style: { opacity: lin, transform: `translate(${(opts.dx ?? 0) * (1 - s)}px, ${(opts.dy ?? 26) * (1 - s)}px) scale(${(opts.from ?? 0.6) + (1 - (opts.from ?? 0.6)) * s})`, filter: `blur(${(1 - lin) * 14}px)` } as React.CSSProperties, visible: f >= at * fps };
};
/** visibilidade de uma cena: entra em 0,3 s e sai em 0,25 s */
export const env = (t: number, a: number, b: number, fi = 0.3, fo = 0.25) => clamp((t - a) / fi) * clamp((b - t) / fo);

// ---------- peças visuais
export const Chip: React.FC<{ bg: string; color?: string; size?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ bg, color = "#fff", size = 40, children, style }) => (
  <div style={{ display: "inline-block", background: bg, color, font: `800 ${size}px Montserrat`, padding: `${size * 0.32}px ${size * 0.7}px`, borderRadius: 999,
    boxShadow: "0 10px 30px rgba(0,0,0,.35)", whiteSpace: "nowrap", letterSpacing: 0.5, ...style }}>{children}</div>
);
export const Box: React.FC<{ c: string; size: number; tight?: boolean; children: React.ReactNode }> = ({ c, size, tight, children }) => (
  <span style={{ background: c, color: "#fff", borderRadius: size * 0.2, padding: `0 ${size * (tight ? 0.08 : 0.16)}px`, margin: `0 ${tight ? 2 : size * 0.1}px`, display: "inline-block", lineHeight: 1.25,
    boxShadow: `0 6px 0 rgba(0,0,0,.25), 0 0 40px ${c}66` }}>{children}</span>
);
export const Outline: React.CSSProperties = { WebkitTextStroke: "10px " + INK, paintOrder: "stroke fill" } as any;
export const Emoji: React.FC<{ e: string; size: number; style?: React.CSSProperties }> = ({ e, size, style }) => (
  <span style={{ fontFamily: "Noto Color Emoji", fontSize: size, lineHeight: 1, display: "inline-block", filter: "drop-shadow(0 8px 14px rgba(0,0,0,.35))", ...style }}>{e}</span>
);
export const Center: React.FC<{ y: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ y, children, style }) => (
  <div style={{ position: "absolute", left: 0, right: 0, top: y, display: "flex", justifyContent: "center", transform: "translateY(-50%)", ...style }}>{children}</div>
);
export const Pop: React.FC<{ at: number; y: number; dx?: number; from?: number; children: React.ReactNode }> = ({ at, y, dx, from, children }) => {
  const p = usePop(at, { dx, from }); if (!p.visible) return null;
  return <Center y={y}><div style={p.style}>{children}</div></Center>;
};

export const Fundo: React.FC = () => (
  <AbsoluteFill style={{ background: "radial-gradient(ellipse 90% 70% at 50% 42%, #1f4d9e 0%, #123372 45%, #0a1a38 100%)" }}>
    <AbsoluteFill style={{ backgroundImage: "linear-gradient(rgba(255,255,255,.035) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,.035) 2px, transparent 2px)", backgroundSize: "60px 60px" }} />
    <Center y={100}><div style={{ background: "#fff", color: INK, font: "800 24px Montserrat", padding: "17px 44px", borderRadius: 30 }}>ENGLISH CLASS · Teacher Eliezio</div></Center>
  </AbsoluteFill>
);

// ---------- avatar 3D: troca de expressão com fusão, balanço e brilho guiados pela voz
export const Avatar: React.FC<{ tt?: number }> = ({ tt }) => {
  const TM = useTM(); const { t: t0, f } = useT(); const t = tt ?? t0;
  const amp = tt !== undefined ? 0 : (TM.amp[Math.min(f, TM.amp.length - 1)] ?? 0);
  const ex = TM.expr as [number, number][]; let i = 0; ex.forEach((e, k) => { if (e[0] <= t) i = k; });
  const cur = ex[i][1], prv = i ? ex[i - 1][1] : cur, k = clamp((t - ex[i][0]) / 0.18);
  const bob = -10 * amp + 3 * Math.sin(t * 1.7), sc = 1 + 0.04 * amp, rot = 2 * Math.sin(t * 2.3) * (0.3 + amp);
  return (
    <div style={{ position: "absolute", left: 540 - 198, top: 1715 - 198 + bob, width: 396, height: 396, transform: `scale(${sc})` }}>
      <div style={{ position: "absolute", inset: -40, borderRadius: "50%", background: YEL, opacity: (90 + 90 * amp) / 255, filter: "blur(24px)" }} />
      <div style={{ position: "absolute", inset: 0, borderRadius: "50%", background: YEL }} />
      <div style={{ position: "absolute", left: 18, top: 18, width: 360, height: 360, transform: `rotate(${rot}deg)` }}>
        <Img src={staticFile(`av/av3d_${prv}.png`)} style={{ position: "absolute", width: 360, height: 360 }} />
        <Img src={staticFile(`av/av3d_${cur}.png`)} style={{ position: "absolute", width: 360, height: 360, opacity: k }} />
      </div>
    </div>
  );
};

// ---------- legenda karaokê: inglês (palavra já falada em amarelo) e português embaixo
const Linha: React.FC<{ words: { w: string; t: number }[]; t: number; size: number; base: string; hl: boolean; weight: number }> = ({ words, t, size, base, hl, weight }) => { const HL = useContext(Ctx).hl; return (
  <div style={{ font: `${weight} ${size}px Montserrat`, color: base, textAlign: "center", maxWidth: 960, lineHeight: 1.38, ...Outline, WebkitTextStroke: `${size * 0.16}px ${INK}` } as any}>
    {words.map((w, i) => {
      const said = hl && t >= w.t - 0.02; const key = w.w.replace(/[:,.!?]$/, "");
      const box = hl ? HL[key] ?? HL[w.w] : undefined;
      const pulse = said ? 1 + 0.08 * Math.exp(-(t - w.t) * 9) : 1;
      return <span key={i} style={{ display: "inline-block", marginRight: size * 0.26, transform: `scale(${pulse})`, color: said ? YEL : base }}>
        {box ? <span style={{ background: box, color: "#fff", borderRadius: 10, padding: "0 10px", WebkitTextStroke: "0px" } as any}>{w.w}</span> : w.w}</span>;
    })}
  </div>
); };
export const Legenda: React.FC = () => {
  const TM = useTM(); const { t } = useT(); const c = TM.caps.find((c) => t >= c.start - 0.05 && t < c.until); if (!c) return null;
  const k = Easing.out(Easing.cubic)(clamp((t - c.start) / 0.25));
  const pt = (c as any).pt; const kp = pt ? Easing.out(Easing.cubic)(clamp((t - pt.start) / 0.25)) : 0;
  const neutral = c.words[0].w.startsWith("Quiz") || c.words[0].w.startsWith("Next");
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 1300, transform: "translateY(-50%)", display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
      <div style={{ opacity: k, transform: `scale(${0.92 + 0.08 * k})`, filter: `blur(${(1 - k) * 8}px)` }}>
        <Linha words={c.words} t={t} size={c.lang === "en" ? 54 : 48} weight={c.lang === "en" ? 800 : 700} base={c.lang === "en" ? "#fff" : PT} hl={c.lang === "en" && !neutral} />
      </div>
      {pt && t >= pt.start - 0.05 && <div style={{ opacity: kp, filter: `blur(${(1 - kp) * 8}px)` }}><Linha words={pt.words} t={t} size={40} weight={700} base={PT} hl={false} /></div>}
    </div>
  );
};

// ---------- cenas
export const Cena: React.FC<{ a: number; b: number; children: React.ReactNode }> = ({ a, b, children }) => {
  const { t } = useT(); const k = env(t, a, b); if (k <= 0) return null;
  return <AbsoluteFill style={{ opacity: k }}><CameraMotionBlur shutterAngle={200} samples={6}><AbsoluteFill>{children}</AbsoluteFill></CameraMotionBlur></AbsoluteFill>;
};
export const capW = (TM: TMT, ci: number, w: string) => TM.caps[ci].words.find((x: any) => x.w.toLowerCase().startsWith(w))?.t ?? 0;
export const Card: React.FC<{ children: React.ReactNode; border?: string; w?: number }> = ({ children, border = "rgba(255,255,255,.18)", w }) => (
  <div style={{ background: "rgba(8,20,48,.82)", border: `4px solid ${border}`, borderRadius: 30, padding: "18px 44px", minWidth: w, textAlign: "center", boxShadow: "0 18px 40px rgba(0,0,0,.4)" }}>{children}</div>
);
// ---------- quiz com contador, revelação e confete saindo da alternativa certa
const Confete: React.FC<{ t0: number; x0: number; y0: number }> = ({ t0, x0, y0 }) => {
  const { t } = useT(); const u = t - t0; if (u < 0 || u >= 1.8) return null;
  const cols = [YEL, GREEN, C_A, C_THE, "#fff", "#b478ff"]; const al = clamp((1.8 - u) / 0.5);
  return <AbsoluteFill>{Array.from({ length: 90 }).map((_, i) => {
    const a = -Math.PI * (0.05 + 0.9 * random("a" + i)), v = 700 + 800 * random("v" + i), w = 12 + 12 * random("w" + i), ph = 6.28 * random("p" + i), sp = 5 + 6 * random("s" + i);
    const x = x0 + Math.cos(a) * v * u * 0.55 + 18 * Math.sin(u * 3 + ph), y = y0 + Math.sin(a) * v * u + 1500 * u * u;
    return <div key={i} style={{ position: "absolute", left: x, top: y, width: w * Math.abs(Math.cos(u * sp + ph)) + 3, height: w * 0.45, background: cols[i % 6], opacity: al, transform: `rotate(${u * sp * 40 + ph * 57}deg)` }} />;
  })}</AbsoluteFill>;
};
const Anel: React.FC<{ c0: number }> = ({ c0 }) => {
  const { t } = useT(); const u = (t - c0) / 3, n = Math.floor(3 - (t - c0)) + 1, fz = (t - c0) % 1, R = 100, col = n > 1 ? YEL : C_THE, L = 2 * Math.PI * R;
  return <Center y={1135}><div style={{ position: "relative", width: 260, height: 260 }}>
    <svg width={260} height={260} style={{ position: "absolute" }}><circle cx={130} cy={130} r={R} fill="rgba(8,18,40,.9)" stroke="#3c5480" strokeWidth={16} />
      <circle cx={130} cy={130} r={R} fill="none" stroke={col} strokeWidth={16} strokeLinecap="round" strokeDasharray={L} strokeDashoffset={L * u} transform="rotate(-90 130 130)" /></svg>
    <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", font: "400 115px Anton", color: col, transform: `scale(${1 + 0.25 * (1 - Easing.out(Easing.cubic)(clamp(fz / 0.3)))})` }}>{n}</div></div></Center>;
};
const Opcao: React.FC<{ i: number; s: string; good: boolean; ta: number; rv: number }> = ({ i, s, good, ta, rv }) => {
  const { t } = useT(); const p = usePop(ta, { dx: i ? 200 : -200 }); if (!p.visible) return null; const rvd = t >= rv;
  const fill = rvd ? (good ? GREEN : GREY) : "#fff"; const sp = spring({ frame: Math.round((t - rv) * 30), fps: 30, config: { damping: 8 } });
  const sc = rvd && good ? 1 + 0.06 * sp : 1;
  return <Center y={790 + i * 150}><div style={{ ...p.style, opacity: (p.style.opacity as number) * (rvd && !good ? 0.55 : 1) }}>
    <div style={{ width: 760, height: 124, borderRadius: 30, background: fill, border: `5px solid ${rvd ? fill : YEL}`, display: "flex", alignItems: "center", position: "relative", transform: `scale(${sc})`, boxShadow: "0 14px 30px rgba(0,0,0,.35)" }}>
      <div style={{ position: "absolute", left: 20, width: 84, height: 84, borderRadius: "50%", background: rvd ? "#fff" : INK, color: rvd ? fill : "#fff", font: "800 44px Montserrat", display: "grid", placeItems: "center" }}>{i + 1}</div>
      <div style={{ flex: 1, textAlign: "center", font: "800 56px Montserrat", color: rvd ? "#fff" : INK, paddingLeft: 60 }}>{s}</div>
      {rvd && <Emoji e={good ? "✅" : "❌"} size={70} style={{ position: "absolute", right: -100, transform: `scale(${spring({ frame: Math.round((t - rv) * 30), fps: 30 })})` }} />}
    </div></div></Center>;
};
export type QuizItem = { e: string; before?: string; answer: string; after?: string; opts: [string, boolean][]; tip: React.ReactNode };
/** quiz com 2 perguntas: tempos em tm.quiz (contador e revelação) e tm.t.quiz / q1 / q2 / cta */
export const Quiz: React.FC<{ items: QuizItem[] }> = ({ items }) => {
  const TM = useTM(); const T = TM.t; const { t } = useT(); const a = T.quiz, b = T.cta; const k = env(t, a, b); if (k <= 0) return null;
  const qi = t < T.q2 - 0.15 ? 0 : 1; const q = items[qi]; const { start: c0, reveal: rv } = TM.quiz[qi];
  const qa = qi === 0 ? T.q1 : T.q2; const qk = qi === 0 ? env(t, qa - 0.05, T.q2 - 0.15, 0.25, 0.2) : env(t, qa - 0.05, b, 0.25, 0.25); const rvd = t >= rv;
  const ok = q.opts.findIndex((o) => o[1]);
  return (<AbsoluteFill style={{ opacity: k }}>
    <Pop at={a} y={290}><Chip bg={YEL} color={INK} size={60}>QUIZ</Chip></Pop>
    <AbsoluteFill style={{ opacity: qk }}>
      <Center y={400}><div style={{ font: "800 40px Montserrat", color: MUTED }}>PERGUNTA {qi + 1} DE 2</div></Center>
      <Pop at={qa} y={560}><div style={{ display: "flex", alignItems: "center", gap: 30 }}>
        <Emoji e={q.e} size={110} style={{ transform: `rotate(${6 * Math.sin(t * 4)}deg)` }} />
        <span style={{ font: "400 110px Anton", color: "#fff", ...Outline } as any}>{q.before ? q.before + " " : ""}<span style={{ color: rvd ? YEL : MUTED }}>{rvd ? q.answer : "____"}</span>{q.after ? " " + q.after : ""}</span></div></Pop>
      <Confete t0={rv} x0={540} y0={790 + ok * 150} />
      {q.opts.map(([s, good], i) => <Opcao key={qi + "-" + i} i={i} s={s} good={good} ta={qa + 0.25 + i * 0.3} rv={rv} />)}
      {t >= c0 && t < rv && <Anel c0={c0} />}
      {t >= rv + 0.2 && <Pop at={rv + 0.2} y={1110}><Chip bg="rgba(8,20,48,.92)" size={40} style={{ border: `4px solid ${YEL}` }}>{q.tip}</Chip></Pop>}
    </AbsoluteFill>
  </AbsoluteFill>);
};
export const Chamada: React.FC = () => {
  const TM = useTM(); const T = TM.t; const { t } = useT();
  return (<Cena a={T.cta} b={TM.total + 1}>
    <Pop at={T.cta} y={400} from={0.85}><div style={{ font: "400 140px Anton", color: YEL, ...Outline } as any}>ACERTOU?</div></Pop>
    <Pop at={T.cta + 0.1} y={590}><Chip bg={RED} size={50} style={{ transform: `scale(${1 + 0.03 * Math.sin(t * 6)})` }}>COMENTA AQUI</Chip></Pop>
    <Pop at={T.cta + 0.3} y={690}><Emoji e="👇" size={64} style={{ transform: `translateY(${6 * Math.sin(t * 6)}px)` }} /></Pop>
    <Pop at={T.follow} y={800}><Chip bg="#fff" color={INK} size={44} style={{ transform: `scale(${1 + 0.04 * Math.sin(t * 5)})` }}>SIGA @teachereliezio</Chip></Pop>
    <Pop at={T.save} y={910}><Chip bg={YEL} color={INK} size={44}>SALVA PRA REVISAR</Chip></Pop>
  </Cena>);
};
export const Progresso: React.FC = () => {
  const TM = useTM(); const { t } = useT();
  return <div style={{ position: "absolute", left: 60, top: 1880, width: 960, height: 12, borderRadius: 6, background: "#3c5480" }}>
    <div style={{ width: `${clamp(t / TM.total) * 100}%`, height: 12, borderRadius: 6, background: YEL }} /></div>;
};

/** moldura de toda aula: fundo, cenas da aula, legenda, avatar e barra de progresso */
export const Licao: React.FC<{ tm: any; hl?: Record<string, string>; children: React.ReactNode }> = ({ tm, hl = {}, children }) => {
  useFonts(); const { t } = useT();
  return (<Ctx.Provider value={{ tm, hl }}><AbsoluteFill style={{ background: NAVY }}>
    <Fundo />{children}
    {t < tm.total - 0.35 && <Legenda />}
    <Avatar /><Progresso />
  </AbsoluteFill></Ctx.Provider>);
};
/** moldura da capa: fundo e avatar parado na expressão do instante tt */
export const CapaBase: React.FC<{ tm: any; tt: number; children: React.ReactNode }> = ({ tm, tt, children }) => {
  useFonts();
  return (<Ctx.Provider value={{ tm, hl: {} }}><AbsoluteFill style={{ background: NAVY }}><Fundo />{children}<Avatar tt={tt} /></AbsoluteFill></Ctx.Provider>);
};
