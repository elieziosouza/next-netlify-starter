// Lampião, o Rei do Cangaço (22/11/2026): documentário animado 2D plano, HORIZONTAL 1920x1080, 247 s. Tempos: ./lamp.json (scripts/historia/lamp_timings.py).
// Novidades: formato horizontal, capítulos numerados, mapa do Nordeste com os 7 estados acendendo e barra de progresso por capítulo.
import React from "react";
import { AbsoluteFill } from "remotion";
import { feature } from "topojson-client";
import { geoMercator, geoPath } from "d3-geo";
import statesJson from "./br_states.json";
import TM from "./lamp.json";
import { P, clamp, ease, rnd, useT, FONT, Puffs, Flash } from "./GuerraParaguai";

const M = TM.M as Record<string, number>;
const S = TM.spans as number[][];
const W = 1920, H = 1080;

// ------------------------------------------------------------ mapa (estados do Brasil, fronteiras de hoje)
const FS: any[] = (statesJson as any).features;
const NE = ["Bahia", "Sergipe", "Alagoas", "Pernambuco", "Paraíba", "Rio Grande do Norte", "Ceará", "Piauí"];
const projN = geoMercator().fitExtent([[880, 70], [1860, 1010]], { type: "FeatureCollection", features: FS.filter((f) => NE.includes(f.properties.name)) } as any);
const gN = geoPath(projN);
const STATES = FS.map((f) => ({ n: f.properties.name as string, d: gN(f) as string })).filter((x) => x.d);
const pt = (lon: number, lat: number) => projN([lon, lat]) as [number, number];
const SEVEN: [string, string][] = [["Pernambuco", "PE"], ["Alagoas", "AL"], ["Paraíba", "PB"], ["Rio Grande do Norte", "RN"], ["Ceará", "CE"], ["Bahia", "BA"], ["Sergipe", "SE"]];
const ST = pt(-38.29, -7.99), JUA = pt(-39.32, -7.21), MOS = pt(-37.34, -5.19);

const Grain: React.FC = () => {
  const { f } = useT();
  return (<AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "multiply", opacity: 0.3 }}>
    <svg width={W} height={H}><filter id="gr"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed={f % 9} /><feColorMatrix values="0 0 0 0 .3  0 0 0 0 .22  0 0 0 0 .12  0 0 0 .9 -.12" /></filter><rect width={W} height={H} filter="url(#gr)" /></svg></AbsoluteFill>);
};
const Vig: React.FC = () => <AbsoluteFill style={{ pointerEvents: "none", background: "radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 55%, rgba(8,6,4,.6) 100%)" }} />;
const Sc: React.FC<{ a: number; b: number; zoom?: number; ov?: React.ReactNode; children: React.ReactNode }> = ({ a, b, zoom = 0.06, ov, children }) => {
  const { t } = useT(); if (t < a - 0.01 || t > b + 0.01) return null;
  const k = clamp((t - a) / 0.4) * clamp((b - t) / 0.4), p = clamp((t - a) / (b - a));
  return (<AbsoluteFill style={{ opacity: k }}><div style={{ position: "absolute", inset: 0, transform: `scale(${1 + zoom * p})`, transformOrigin: "50% 45%" }}>{children}</div>{ov}</AbsoluteFill>);
};
const Hills: React.FC<{ y: number; c: string; amp?: number; seed?: number; dx?: number }> = ({ y, c, amp = 90, seed = 1, dx = 0 }) => {
  let d = `M-100 ${y + 500} L-100 ${y}`; for (let i = 0; i <= 22; i++) d += ` L${i * 100 - 100 + dx} ${y - amp * (0.5 + 0.5 * Math.sin(i * 1.3 + seed) * rnd(i + seed))}`; d += ` L2100 ${y + 500} Z`;
  return <path d={d} fill={c} />;
};
const Stars: React.FC<{ n?: number }> = ({ n = 70 }) => (<g>{Array.from({ length: n }, (_, i) => <circle key={i} cx={rnd(i) * W} cy={rnd(i + 50) * 520} r={1 + 2 * rnd(i + 99)} fill="#fff" opacity={0.3 + 0.5 * rnd(i + 7)} />)}</g>);
const Rain: React.FC<{ o?: number }> = ({ o = 0.35 }) => {
  const { t } = useT();
  return (<g stroke="#cfe3f5" strokeWidth="2" opacity={o}>{Array.from({ length: 140 }, (_, i) => { const x = (rnd(i) * (W + 200) - 100 - t * 60 * 0 + 0), y = ((rnd(i + 3) * H + t * 900 * (0.8 + 0.4 * rnd(i + 8))) % (H + 80)) - 40; return <line key={i} x1={x} y1={y} x2={x - 14} y2={y + 36} />; })}</g>);
};

// ------------------------------------------------------------ peças
const Mandacaru: React.FC<{ x: number; y: number; s?: number; c: string }> = ({ x, y, s = 1, c }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`} fill={c}><rect x="-14" y="-150" width="28" height="150" rx="14" /><path d="M-14 -70 L-52 -70 L-52 -118 L-34 -118 L-34 -90 L-14 -90 Z" /><path d="M14 -50 L50 -50 L50 -104 L32 -104 L32 -72 L14 -72 Z" /></g>);
const Arbusto: React.FC<{ x: number; y: number; s?: number; c: string }> = ({ x, y, s = 1, c }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`} stroke={c} strokeWidth="6" fill="none" strokeLinecap="round"><path d="M0 0 L0 -60 M0 -30 L-34 -66 M0 -40 L30 -80 M0 -60 L-14 -96 M-34 -66 L-52 -64 M30 -80 L52 -78" /></g>);
// cangaceiro: chapéu de couro de aba virada com estrelas, cartucheiras cruzadas e rifle
const Cang: React.FC<{ x: number; y: number; s?: number; ph?: number; c?: string; walk?: boolean; flip?: boolean; rifle?: boolean }> = ({ x, y, s = 1, ph = 0, c = "#12151c", walk = true, flip, rifle = true }) => {
  const { t } = useT(); const bob = walk ? 4 * Math.sin(t * 6 + ph) : 0, sw = walk ? 7 * Math.sin(t * 6 + ph) : 0;
  return (<g transform={`translate(${x} ${y + bob}) scale(${flip ? -s : s} ${s})`} fill={c}>
    <rect x={-16 + sw} y="-22" width="12" height="58" /><rect x="4" y="-22" width="12" height="58" transform={`translate(${-sw} 0)`} /><path d="M-15 -78 L15 -78 L18 -22 L-18 -22 Z" />
    <circle cx="0" cy="-92" r="12" /><path d="M-24 -102 Q-24 -140 0 -144 Q24 -140 24 -102 Z" /><path d="M-52 -100 Q0 -88 52 -100 Q46 -120 38 -124 L-38 -124 Q-46 -120 -52 -100 Z" />
    <circle cx="-44" cy="-107" r="3.5" fill={P.ochre} /><circle cx="44" cy="-107" r="3.5" fill={P.ochre} /><circle cx="0" cy="-124" r="4" fill={P.ochre} />
    <path d="M-14 -76 L16 -30" stroke="#4a4f5a" strokeWidth="5" fill="none" /><path d="M14 -76 L-16 -30" stroke="#4a4f5a" strokeWidth="5" fill="none" />
    {rifle && <g><line x1="-22" y1="-52" x2="30" y2="-66" stroke={c} strokeWidth="6" strokeLinecap="round" /></g>}</g>);
};
const Boi: React.FC<{ x: number; y: number; s?: number; c?: string; flip?: boolean; ph?: number }> = ({ x, y, s = 1, c = "#3a2a20", flip, ph = 0 }) => {
  const { t } = useT(); const bob = 2 * Math.sin(t * 1.5 + ph);
  return (<g transform={`translate(${x} ${y + bob}) scale(${flip ? -s : s} ${s})`} fill={c}><rect x="-60" y="-70" width="120" height="48" rx="22" /><path d="M52 -66 L84 -78 L92 -52 L58 -32 Z" /><path d="M86 -78 L96 -96 M80 -80 L76 -98" stroke={c} strokeWidth="5" fill="none" />
    {[-44, -26, 28, 46].map((lx) => <rect key={lx} x={lx - 5} y="-26" width="10" height="42" />)}<path d="M-60 -60 Q-82 -50 -78 -22" stroke={c} strokeWidth="6" fill="none" strokeLinecap="round" /></g>);
};
const Cavalo: React.FC<{ x: number; y: number; s?: number; c?: string; flip?: boolean; ph?: number; rider?: boolean; speed?: number }> = ({ x, y, s = 1, c = "#1b1612", flip, ph = 0, rider = true, speed = 9 }) => {
  const { t } = useT(); const g = Math.sin(t * speed + ph);
  return (<g transform={`translate(${x} ${y + 3 * Math.abs(g)}) scale(${flip ? -s : s} ${s})`}>
    <g fill={c}><ellipse cx="0" cy="-90" rx="82" ry="34" /><path d="M60 -100 L112 -146 L136 -132 L132 -112 L88 -66 Z" /><path d="M112 -146 L120 -166 L128 -146 Z" /><path d="M-76 -96 Q-110 -70 -104 -20" stroke={c} strokeWidth="9" fill="none" strokeLinecap="round" />
      {[[-52, 1], [-30, -1], [36, -1], [58, 1]].map(([lx, sg], i) => <path key={i} d={`M${lx} -66 L${lx + 16 * g * (sg as number)} -6 L${lx + 20 * g * (sg as number)} 24`} stroke={c} strokeWidth="11" fill="none" strokeLinecap="round" />)}</g>
    {rider && <Cang x={0} y={-96} s={0.78} walk={false} c={c === "#1b1612" ? "#0e0c10" : c} />}</g>);
};
const Casa: React.FC<{ x: number; y: number; s?: number; wall?: string; roof?: string; fire?: boolean; ruin?: boolean }> = ({ x, y, s = 1, wall = "#c9a171", roof = "#8a6a38", ruin }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}><rect x="-70" y="-70" width="140" height="70" fill={wall} />{ruin ? <path d="M-84 -70 L-24 -98 L0 -80 L34 -102 L84 -70 Z" fill={roof} opacity=".6" /> : <path d="M-92 -68 L0 -134 L92 -68 Z" fill={roof} />}<path d="M-16 0 L-16 -46 Q0 -58 16 -46 L16 0 Z" fill="#2a1e14" /><rect x="34" y="-52" width="22" height="26" fill="#2a1e14" opacity=".7" /></g>);
const Barraca: React.FC<{ x: number; y: number; s?: number; c?: string }> = ({ x, y, s = 1, c = "#3a3a44" }) => (<g transform={`translate(${x} ${y}) scale(${s})`}><path d="M-90 0 L0 -96 L90 0 Z" fill={c} /><path d="M-18 0 L0 -50 L18 0 Z" fill="#14141a" /></g>);
const Cerca: React.FC<{ x: number; y: number; w: number; h?: number; c?: string }> = ({ x, y, w, h = 120, c = "#6b4a28" }) => (
  <g>{Array.from({ length: Math.floor(w / 28) }, (_, i) => <path key={i} d={`M${x + i * 28} ${y} L${x + i * 28} ${y - h} L${x + i * 28 + 12} ${y - h - 20} L${x + i * 28 + 24} ${y - h} L${x + i * 28 + 24} ${y} Z`} fill={c} stroke="#3d2a14" strokeWidth="2" />)}<rect x={x} y={y - h * 0.6} width={w} height="9" fill="#3d2a14" opacity=".7" /></g>);

// ------------------------------------------------------------ cartela, pílula, destaques
const Cartela: React.FC<{ at: number; to: number; date: string; sub?: string; y?: number; fs?: number }> = ({ at, to, date, sub, y = 150, fs = 62 }) => {
  const { t } = useT(); if (t < at || t > to + 0.4) return null;
  const k = ease((t - at) / 0.5) * clamp((to + 0.4 - t) / 0.4);
  return (<div style={{ position: "absolute", left: 80 + (1 - k) * -620, top: y, opacity: k, padding: "16px 34px 18px", background: "rgba(16,20,28,.88)", borderLeft: `8px solid ${P.ochre}`, boxShadow: "0 10px 30px rgba(0,0,0,.4)" }}>
    <div style={{ font: `400 ${fs}px DMS`, color: P.cream, letterSpacing: 1.5, lineHeight: 1.05 }}>{date}</div>{sub && <div style={{ font: "700 26px MB", color: P.ochre, letterSpacing: 4, marginTop: 8 }}>{sub}</div>}</div>);
};
const Pill: React.FC<{ at: number; to?: number; x?: number; y: number; right?: boolean; children: React.ReactNode }> = ({ at, to = 999, x = 80, y, right, children }) => {
  const { t } = useT(); const k = ease((t - at) / 0.4) * clamp((to - t) / 0.35); if (k <= 0) return null;
  return <div style={{ position: "absolute", [right ? "right" : "left"]: x, top: y, opacity: k, transform: `translateX(${(1 - k) * (right ? 80 : -80)}px)`, padding: "12px 26px", borderRadius: 40, background: "rgba(240,228,201,.95)", color: P.ink, font: "700 28px MB", letterSpacing: 2 }}>{children}</div>;
};
const Big: React.FC<{ at: number; to?: number; x?: number; y: number; w?: number; align?: "left" | "center" | "right"; size?: number; color?: string; children: React.ReactNode; sub?: string }> = ({ at, to = 999, x = 80, y, w = 760, align = "left", size = 150, color = P.cream, children, sub }) => {
  const { t } = useT(); const k = ease((t - at) / 0.5) * clamp((to - t) / 0.4); if (k <= 0) return null;
  return (<div style={{ position: "absolute", left: x, top: y, width: w, opacity: k, textAlign: align, textShadow: "0 6px 22px rgba(0,0,0,.65)" }}><div style={{ font: `400 ${size}px DMS`, color, lineHeight: 1 }}>{children}</div>{sub && <div style={{ font: "700 24px MB", letterSpacing: 5, color: P.sand, marginTop: 10 }}>{sub}</div>}</div>);
};

// ------------------------------------------------------------ mapa do Nordeste (usado em vários capítulos)
const MapNE: React.FC<{ fill?: Record<string, string>; focus?: [number, number]; zoomAt?: number; zoomTo?: number; z?: number; children?: (z: number) => React.ReactNode }> = ({ fill = {}, focus, zoomAt = 0, z = 1.9, children }) => {
  const { t } = useT(); const k = focus ? ease((t - zoomAt) / 2.0) : 0, zz = 1 + (z - 1) * k, tx = focus ? 1370 - focus[0] * zz : 0, ty = focus ? 540 - focus[1] * zz : 0;
  return (<svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}><rect width={W} height={H} fill="#e9dcbc" />
    <g stroke="rgba(120,95,55,.18)" strokeWidth="2">{Array.from({ length: 16 }, (_, i) => <line key={i} x1="0" y1={i * 140} x2={W} y2={i * 140} />)}{Array.from({ length: 16 }, (_, i) => <line key={i} x1={i * 140} y1="0" x2={i * 140} y2={H} />)}</g>
    <g transform={focus ? `translate(${tx} ${ty}) scale(${zz})` : undefined}>
      {STATES.map((s) => <path key={s.n} d={s.d} fill={fill[s.n] || (NE.includes(s.n) ? "#d8c9a5" : "#e0d3b0")} stroke="#8a7650" strokeWidth={1.5 / zz} strokeLinejoin="round" />)}
      {children && children(zz)}</g></svg>);
};
const Pin: React.FC<{ p: [number, number]; at: number; z: number; label: string; sub?: string; dx?: number; dy?: number }> = ({ p, at, z, label, sub, dx = 30, dy = -22 }) => {
  const { t } = useT(); const k = ease((t - at) / 0.35);
  return (<g opacity={k}><circle cx={p[0]} cy={p[1]} r={(22 + 10 * Math.sin(t * 6)) / z * 1.1} fill="none" stroke={P.red} strokeWidth={4 / z} /><circle cx={p[0]} cy={p[1]} r={9 / z * 1.1} fill={P.red} />
    <text x={p[0] + dx / z} y={p[1] + dy / z} fontFamily="MS" fontSize={28 / z} fill={P.ink} stroke="#e9dcbc" strokeWidth={5 / z} paintOrder="stroke" letterSpacing="2">{label}</text>
    {sub && <text x={p[0] + dx / z} y={p[1] + (dy + 32) / z} fontFamily="PFI" fontSize={24 / z} fill="#3a2a14" stroke="#e9dcbc" strokeWidth={4 / z} paintOrder="stroke">{sub}</text>}</g>);
};

// ------------------------------------------------------------ cenas
const sunset = (id: string, a: string, b: string, c: string, d: string) => (<linearGradient id={id} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={a} /><stop offset=".45" stopColor={b} /><stop offset=".75" stopColor={c} /><stop offset="1" stopColor={d} /></linearGradient>);
// 0: abertura
const Abertura: React.FC = () => {
  const { t } = useT();
  return (<Sc a={0} b={12.3} zoom={0.1} ov={<>
    <Cartela at={0.4} to={8.2} date="O REI DO CANGAÇO" sub="SERTÃO DO NORDESTE · DÉCADAS DE 1920 E 1930" fs={70} />
    {t > S[3][0] - 0.2 && <div style={{ position: "absolute", left: 0, right: 0, top: 380, textAlign: "center", opacity: ease((t - S[3][0] + 0.2) / 0.6) * clamp((12.1 - t) / 0.4) }}>
      <div style={{ font: "400 270px DMS", color: P.cream, textShadow: "0 10px 40px rgba(0,0,0,.7)", letterSpacing: 6 }}>LAMPIÃO</div></div>}</>}>
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}><defs>{sunset("ab", "#2b2f5a", "#c0586e", "#f09a62", "#f8cd8a")}</defs>
      <rect width={W} height={760} fill="url(#ab)" /><Stars n={40} /><circle cx="1280" cy="560" r="170" fill="#ffe3a8" opacity=".95" />
      <Hills y={600} c="#8a5a6a" amp={120} seed={4} dx={-t * 4} /><Hills y={690} c="#5a3f50" amp={100} seed={9} dx={-t * 8} />
      <rect y="760" width={W} height="400" fill="#4a3228" />
      {[120, 420, 760, 1500, 1800].map((x, i) => <Arbusto key={i} x={x} y={820 + 20 * (i % 2)} s={1.5 + 0.5 * rnd(i)} c="#241810" />)}
      <Mandacaru x={240} y={900} s={2.0} c="#10150f" /><Mandacaru x={1700} y={880} s={1.7} c="#10150f" />
      <Cang x={1010} y={790} s={3.4} walk={false} c="#0a0a0f" /></svg></Sc>);
};
// capítulo 1: mapa de Pernambuco + sítio
const Cap1a: React.FC = () => {
  const { t } = useT();
  return (<Sc a={S[4][0] - 0.2} b={S[6][0] + 0.2} zoom={0} ov={<>
    <Cartela at={S[4][0]} to={S[5][1]} date="ENTRE 1897 E 1900" sub="NASCE VIRGULINO FERREIRA DA SILVA" fs={58} />
    <Big at={S[4][0] + 3.2} to={S[5][1]} y={470} w={760} size={92}>Vila Bela</Big>
    <div style={{ position: "absolute", left: 80, top: 570, font: "italic 400 40px PFI", color: P.cream, opacity: ease((t - S[5][0]) / 0.5), textShadow: "0 4px 14px rgba(0,0,0,.7)" }}>hoje Serra Talhada, Pernambuco</div>
    <div style={{ position: "absolute", left: 80, bottom: 150, font: "italic 400 24px PFI", color: "rgba(240,228,201,.8)" }}>mapa com as fronteiras de hoje</div></>}>
    <MapNE fill={{ Pernambuco: "#c9a25c" }} focus={ST} zoomAt={S[4][0] + 1} z={1.7}>{(z) => <Pin p={ST} at={S[4][0] + 3} z={z} label="SERRA TALHADA" sub="antiga Vila Bela" />}</MapNE>
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(16,20,28,.78) 0%, rgba(16,20,28,.4) 38%, rgba(16,20,28,0) 55%)" }} /></Sc>);
};
const Cap1b: React.FC = () => {
  const { t } = useT(); const a = S[6][0] - 0.2;
  return (<Sc a={a} b={S[7][0] + 0.2} zoom={0.06} ov={<>
    <Cartela at={S[6][0]} to={S[7][0] - 0.3} date="O MENINO DO SERTÃO" sub="TERCEIRO FILHO · FAMÍLIA DE AGRICULTORES" fs={58} />
    <Pill at={M.terceiro - 0.2} to={M.vaqueiro - 0.3} x={80} y={340}>TERCEIRO FILHO</Pill><Pill at={M.vaqueiro - 0.2} to={S[7][0]} x={80} y={340}>VAQUEIRO NO SÍTIO DO PAI</Pill><Pill at={M.sanfona - 0.3} x={80} y={420}>TOCAVA SANFONA</Pill></>}>
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}><defs>{sunset("c1", "#6aa0c8", "#bfd9e0", "#f5dcae", "#f6e4b8")}</defs>
      <rect width={W} height={720} fill="url(#c1)" /><g transform={`translate(${-(t - a) * 6} 0)`}><ellipse cx="420" cy="220" rx="300" ry="40" fill="#fff" opacity=".5" /><ellipse cx="1300" cy="150" rx="340" ry="36" fill="#fff" opacity=".45" /></g>
      <Hills y={640} c="#b48a58" amp={110} seed={3} dx={-(t - a) * 3} /><Hills y={700} c="#9c7444" amp={80} seed={12} dx={-(t - a) * 5} />
      <rect y="720" width={W} height="400" fill="#b9915a" />
      <Casa x={430} y={800} s={1.5} wall="#d6b583" roof="#8a5a38" /><Cerca x={620} y={830} w={700} h={90} />
      {[1500, 1700, 1380].map((x, i) => <Boi key={i} x={x} y={880 + 30 * i} s={1.0 - 0.05 * i} ph={i * 2} flip={i % 2 === 0} />)}
      <Mandacaru x={110} y={850} s={1.6} c="#2f4a2e" /><Mandacaru x={1860} y={840} s={1.4} c="#2f4a2e" />
      <path d="M0 960 Q600 930 1200 990 T2000 960 L2000 1100 L0 1100 Z" fill="#a37436" />
      {/* vaqueiro a cavalo cruzando */}
      <Cavalo x={((t - a) * 60) % 2300 - 250} y={940} s={1.1} c="#2a1c12" rider={false} speed={5} />
      {/* menino com sanfona */}
      <g transform="translate(1180 1010)"><Cang x={0} y={0} s={1.0} walk={false} rifle={false} c="#2a1c12" /><rect x="14" y="-72" width="44" height="30" rx="6" fill="#8a2b25" transform={`rotate(${-8 + 6 * Math.sin(t * 5)} 30 -58)`} /></g></svg></Sc>);
};
// capítulo 2: briga e mudança, entrada no cangaço
const Cap2a: React.FC = () => {
  const { t } = useT(); const a = S[7][0] - 0.2, p = t - a;
  const carr = clamp((t - S[9][0]) / 8.5);
  return (<Sc a={a} b={S[11][0] + 0.2} zoom={0.06} ov={<>
    <Cartela at={S[7][0]} to={S[9][0] - 0.2} date="1917" sub="BRIGA COM O VIZINHO · ACUSAÇÕES DE ROUBO DE ANIMAIS" fs={72} />
    <Cartela at={S[9][0]} to={S[11][0] - 0.2} date="A FAMÍLIA SE MUDA" sub={t < M.alagoas - 0.3 ? "DENTRO DE PERNAMBUCO" : "PERNAMBUCO → ALAGOAS"} fs={54} /></>}>
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}><defs>{sunset("c2", "#4a5c7a", "#c99a78", "#e6bf8a", "#f1d9a6")}</defs>
      <rect width={W} height={700} fill="url(#c2)" /><Hills y={600} c="#8a6a5a" amp={110} seed={5} dx={-p * 4} /><Hills y={680} c="#6a5448" amp={80} seed={13} dx={-p * 8} />
      <rect y="700" width={W} height="400" fill="#a3763e" />
      {t < S[9][0] ? (<g>
        <Cerca x={200} y={800} w={1500} h={100} />
        {[260, 520, 1500, 1720].map((x, i) => <Boi key={i} x={x} y={900 + 20 * (i % 2)} s={1.0} ph={i} flip={i > 1} />)}
        <Cang x={880} y={980} s={1.6} walk={false} rifle={false} c="#1c1822" /><Cang x={1080} y={980} s={1.6} walk={false} flip rifle={false} c="#2c1a16" />
        <g transform="translate(980 700)" opacity={ease((t - S[7][0] - 3) / 0.6)}><circle r="22" fill={P.ochre} /><path d="M-10 -26 L10 -26 L6 -42 L-6 -42 Z" fill={P.ochre} /><text y="52" textAnchor="middle" fontFamily="MB" fontSize="24" fill={P.cream} letterSpacing="3">CHOCALHO</text></g>
      </g>) : (<g>
        <path d="M-40 940 Q700 900 2000 960" stroke="#d9b07a" strokeWidth="90" fill="none" opacity=".5" />
        <g transform={`translate(${-300 + 2300 * carr} 920)`}><rect x="-110" y="-70" width="220" height="60" fill="#6b4a28" /><rect x="-90" y="-130" width="180" height="60" fill="#b88a50" /><path d="M-100 -130 Q0 -190 100 -130" fill="#e4d4b0" /><circle cx="-70" cy="-6" r="34" fill="none" stroke="#2a1e14" strokeWidth="9" /><circle cx="70" cy="-6" r="34" fill="none" stroke="#2a1e14" strokeWidth="9" /><Boi x={190} y={-8} s={1.0} c="#3a2a20" flip={false} /></g>
        {[160, 760, 1500].map((x, i) => <Mandacaru key={i} x={x} y={820 + 8 * i} s={1.4} c="#3a5a38" />)}
      </g>)}
    </svg></Sc>);
};
const Cap2b: React.FC = () => {
  const { t } = useT(); const a = S[11][0] - 0.2, p = t - a;
  return (<Sc a={a} b={S[14][0] + 0.2} zoom={0.07} ov={<>
    <Cartela at={S[11][0]} to={S[12][0] - 0.3} date="NASCE O APELIDO" sub="VIRGULINO PASSA A SER CHAMADO DE LAMPIÃO" fs={54} />
    <Cartela at={S[12][0]} to={S[14][0] - 0.2} date="ENTRE 1920 E 1921" sub="MORTE DO PAI, JOSÉ FERREIRA" fs={62} />
    <Pill at={M.mae - 0.2} to={S[14][0]} x={80} y={350}>A MÃE TAMBÉM MORRE NESSE PERÍODO</Pill></>}>
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}><defs>{sunset("c3", "#241d2e", "#7a3a48", "#d27a5a", "#efa868")}</defs>
      <rect width={W} height={740} fill="url(#c3)" /><Stars n={30} /><circle cx="420" cy="590" r="140" fill="#ffd9a0" opacity=".8" />
      <Hills y={620} c="#4a2c3a" amp={110} seed={8} dx={-p * 4} /><Hills y={700} c="#2c1c28" amp={90} seed={14} dx={-p * 7} />
      <rect y="760" width={W} height="400" fill="#1d1a2a" />
      {[300, 900, 1500, 1800].map((x, i) => <Mandacaru key={i} x={x} y={830 + 10 * (i % 2)} s={1.7} c="#0a0c12" />)}
      {Array.from({ length: 7 }, (_, i) => { const u = (p * 0.045 + i * 0.1) % 1.3 - 0.15; return <Cang key={i} x={-120 + 2160 * u} y={960 + 24 * (i % 3)} s={1.5 - 0.1 * (i % 3)} ph={i * 1.1} c="#07080d" />; })}
    </svg></Sc>);
};
// capítulo 3: bando de Sinhô Pereira, 7 estados, vida na caatinga
const Cap3a: React.FC = () => {
  const { t } = useT(); const a = S[14][0] - 0.2, p = t - a;
  return (<Sc a={a} b={S[16][0] + 0.2} zoom={0.06} ov={<>
    <Cartela at={S[14][0]} to={S[15][0] - 0.3} date="O BANDO DE SINHÔ PEREIRA" sub="UM DOS CANGACEIROS MAIS CONHECIDOS DA REGIÃO" fs={52} />
    <Cartela at={S[15][0]} to={S[16][0] - 0.2} date="1922" sub="SINHÔ DEIXA O CANGAÇO · LAMPIÃO ASSUME O COMANDO" fs={80} />
    <Pill at={M.cicero - 0.3} to={S[16][0]} x={80} y={380}>ACONSELHADO PELO PADRE CÍCERO</Pill></>}>
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}><defs>{sunset("c4", "#1a1a36", "#3e3a6a", "#b4607a", "#f0a468")}</defs>
      <rect width={W} height={760} fill="url(#c4)" /><Stars n={80} /><Hills y={660} c="#2a2440" amp={110} seed={6} dx={-p * 3} />
      <rect y="760" width={W} height="400" fill="#1a1624" />
      {[200, 1700].map((x, i) => <Mandacaru key={i} x={x} y={840} s={1.8} c="#090b11" />)}
      {/* fogueira */}
      <g transform="translate(960 930)">{[0, 1, 2].map((i) => <path key={i} d={`M${-26 + i * 26} 0 Q${-14 + i * 26} ${-70 - 16 * Math.sin(p * 8 + i)} ${i * 26 - 0} ${-100 - 22 * Math.sin(p * 6 + i * 2)} Q${14 + i * 26} -60 ${26 + i * 26} 0 Z`} fill={i === 1 ? "#ffcf5a" : "#ff7a2a"} opacity=".95" />)}<ellipse cx="0" cy="14" rx="90" ry="12" fill="#2a1c12" /><circle cx="0" cy="-60" r="230" fill="#ff9a3c" opacity=".08" /></g>
      {[560, 720, 1200, 1380, 1530].map((x, i) => <Cang key={i} x={x} y={960 + 18 * (i % 2)} s={1.6} walk={false} c="#05060a" flip={x > 960} />)}
    </svg></Sc>);
};
const Cap3b: React.FC = () => {
  const { t } = useT(); const a = S[16][0] - 0.2;
  const fill: Record<string, string> = {}; SEVEN.forEach(([n], i) => { if (t >= S[16][0] + 1.6 + i * 0.45) fill[n] = "#c9a25c"; });
  const n7 = Math.min(7, Math.max(0, Math.floor((t - (S[16][0] + 1.6)) / 0.45) + 1));
  return (<Sc a={a} b={S[19][0] + 0.2} zoom={0} ov={<>
    <Cartela at={S[16][0]} to={S[19][0] - 0.3} date="16 ANOS DE CANGAÇO" sub="7 ESTADOS DO NORDESTE" fs={60} />
    <Big at={S[16][0] + 1.4} to={S[19][0] - 0.3} y={360} w={700} size={170} color={P.ochre} sub="ESTADOS ATINGIDOS PELO BANDO">{n7}<span style={{ fontSize: 80, color: P.cream }}> / 7</span></Big>
    <Pill at={M.volantes - 0.3} to={S[19][0]} x={80} y={640}>+ DE 200 COMBATES COM AS VOLANTES</Pill>
    <Pill at={M.mil - 0.6} to={S[19][0]} x={80} y={724}>+ DE MIL MORTES · ESTIMATIVA</Pill>
    <div style={{ position: "absolute", left: 80, bottom: 150, font: "italic 400 24px PFI", color: "rgba(40,30,18,.75)" }}>mapa com as fronteiras de hoje</div></>}>
    <MapNE fill={fill}>{() => <g>{SEVEN.map(([n, sg]) => { const f = FS.find((x) => x.properties.name === n); const c = gN.centroid(f) as [number, number]; return t >= S[16][0] + 1.6 ? <text key={n} x={c[0]} y={c[1]} textAnchor="middle" fontFamily="MS" fontSize="34" fill="#3a2a14" opacity=".85">{sg}</text> : null; })}</g>}</MapNE><AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(16,20,28,.8) 0%, rgba(16,20,28,.45) 38%, rgba(16,20,28,0) 55%)" }} /></Sc>);
};
const Cap3c: React.FC = () => {
  const { t } = useT(); const a = S[19][0] - 0.2, p = t - a;
  return (<Sc a={a} b={S[20][0] + 0.2} zoom={0.06} ov={<>
    <Cartela at={S[19][0]} to={S[20][0] - 0.3} date="VIDA NA CAATINGA" sub="A CAVALO · VESTIDOS DE COURO" fs={58} />
    <Pill at={M.coiteiros - 0.2} x={80} y={350}>COITEIROS: ABRIGO E COMIDA</Pill></>}>
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}><defs>{sunset("c5", "#5a7aa0", "#d29a78", "#f0b878", "#f6d89a")}</defs>
      <rect width={W} height={720} fill="url(#c5)" /><Hills y={620} c="#a4695a" amp={100} seed={5} dx={-p * 5} /><Hills y={700} c="#7a4e4c" amp={80} seed={9} dx={-p * 9} />
      <rect y="760" width={W} height="400" fill="#b98a4e" /><path d="M-40 920 Q700 880 2000 930" stroke="#d9b07a" strokeWidth="110" fill="none" opacity=".4" />
      {[160, 500, 1100, 1700].map((x, i) => <Arbusto key={i} x={x} y={820 + 14 * (i % 3)} s={1.6} c="#4a3524" />)}
      <Casa x={1620} y={860} s={1.1} wall="#d6b583" roof="#8a5a38" />
      {[0, 1, 2, 3].map((i) => <Cavalo key={i} x={((p * 120 + i * 420) % 2500) - 300} y={1000 + 18 * (i % 2)} s={1.25 - 0.06 * (i % 2)} ph={i * 1.3} speed={9} />)}
    </svg></Sc>);
};
// capítulo 4: capitão e Mossoró
const Cap4: React.FC = () => {
  const { t } = useT(); const a = S[20][0] - 0.2;
  return (<Sc a={a} b={S[24][0] + 0.2} zoom={0} ov={<>
    <Cartela at={S[20][0]} to={S[21][0] - 0.3} date="MARÇO DE 1926" sub="JUAZEIRO DO NORTE · CEARÁ" fs={60} />
    <Pill at={M.capitao - 0.4} to={S[21][0] - 0.2} x={80} y={360}>PATENTE DE CAPITÃO · PADRE CÍCERO</Pill>
    <Cartela at={S[21][0]} to={S[24][0] - 0.3} date="JUNHO DE 1927" sub="MOSSORÓ · RIO GRANDE DO NORTE" fs={60} />
    <Pill at={S[22][0] - 0.1} to={S[24][0] - 0.2} x={80} y={360}>A CIDADE ESTAVA PREPARADA</Pill>
    <Pill at={M.derrota - 0.6} to={S[24][0] - 0.2} x={80} y={444}>A MAIOR DERROTA DA CARREIRA</Pill>
    <div style={{ position: "absolute", left: 80, bottom: 150, font: "italic 400 24px PFI", color: "rgba(40,30,18,.75)" }}>mapa com as fronteiras de hoje</div></>}>
    <MapNE fill={{ Ceará: t < S[21][0] ? "#c9a25c" : "#d8c9a5", "Rio Grande do Norte": t >= S[21][0] ? "#c9a25c" : "#d8c9a5" }} focus={[(JUA[0] + MOS[0]) / 2, (JUA[1] + MOS[1]) / 2]} zoomAt={S[20][0] + 0.5} z={1.9}>
      {(z) => <g><Pin p={JUA} at={S[20][0] + 1.5} z={z} label="JUAZEIRO DO NORTE" sub="1926" dx={-330} dy={-26} />{t >= S[21][0] && <Pin p={MOS} at={S[21][0] + 0.3} z={z} label="MOSSORÓ" sub="1927" dx={34} dy={-18} />}</g>}</MapNE>
    <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(16,20,28,.78) 0%, rgba(16,20,28,.35) 36%, rgba(16,20,28,0) 52%)" }} /></Sc>);
};
// capítulo 5: Maria Bonita
const Cap5: React.FC = () => {
  const { t } = useT(); const a = S[24][0] - 0.2, p = t - a;
  return (<Sc a={a} b={S[30][0] + 0.2} zoom={0.07} ov={<>
    <Cartela at={S[24][0]} to={S[25][0] - 0.3} date="1930" sub="BAHIA · MARIA GOMES DE OLIVEIRA" fs={80} />
    <Pill at={M.primeira - 0.3} to={S[26][0]} x={80} y={360}>PRIMEIRA MULHER NO BANDO</Pill>
    <Pill at={M.bonita - 0.5} to={S[28][0] - 0.3} x={80} y={360}>“MARIA BONITA”: APELIDO DA IMPRENSA, DEPOIS DA MORTE</Pill>
    <Cartela at={S[28][0]} to={S[30][0] - 0.2} date="1932" sub="NASCE EXPEDITA, A FILHA DO CASAL" fs={72} /></>}>
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}><defs>{sunset("c6", "#3b4a78", "#d27a8a", "#f4b070", "#f8d89a")}</defs>
      <rect width={W} height={760} fill="url(#c6)" /><Stars n={22} /><circle cx="1330" cy="610" r="160" fill="#ffe7b0" opacity=".95" />
      <Hills y={620} c="#a4695a" amp={100} seed={5} dx={-p * 3} /><Hills y={700} c="#7a4e4c" amp={80} seed={9} dx={-p * 6} />
      <rect y="780" width={W} height="400" fill="#b98a4e" />
      <Arbusto x={300} y={850} s={1.6} c="#4a3524" /><Arbusto x={1650} y={860} s={1.8} c="#4a3524" /><Mandacaru x={140} y={880} s={1.7} c="#2f4a2e" />
      {/* casal: ele com chapéu de aba virada, ela com chapéu e vestido */}
      <Cang x={900} y={960} s={2.5} walk={false} rifle={false} c="#0a0a0f" />
      <g transform="translate(1080 960) scale(2.4)" fill="#0a0a0f"><rect x="-12" y="-22" width="10" height="58" /><rect x="4" y="-22" width="10" height="58" /><path d="M-14 -78 L14 -78 L34 -22 L-34 -22 Z" /><circle cx="0" cy="-92" r="12" /><path d="M-22 -102 Q-22 -136 0 -140 Q22 -136 22 -102 Z" /><path d="M-44 -100 Q0 -90 44 -100 Q38 -116 30 -120 L-30 -120 Q-38 -116 -44 -100 Z" /><circle cx="0" cy="-120" r="4" fill={P.ochre} /></g>
      {t >= S[28][0] - 0.2 && <g transform="translate(1480 980)" opacity={ease((t - S[28][0]) / 0.6)}><circle cx="0" cy="-60" r="14" fill="#0a0a0f" /><path d="M-18 -44 L18 -44 L26 0 L-26 0 Z" fill="#0a0a0f" /></g>}
    </svg></Sc>);
};
// capítulo 6: Angicos, 1938
const Cap6a: React.FC = () => {
  const { t } = useT(); const a = S[30][0] - 0.2, p = t - a;
  return (<Sc a={a} b={S[32][0] + 0.2} zoom={0.06} ov={<>
    <Cartela at={S[30][0]} to={S[32][0] - 0.2} date="O CERCO SE FECHA" sub="ESTADO NOVO · GOVERNO DE GETÚLIO VARGAS" fs={60} />
    <Pill at={M.vargas - 0.6} to={S[32][0]} x={80} y={360}>ORDEM: ACABAR COM OS BANDOS QUE NÃO SE RENDESSEM</Pill></>}>
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}><defs>{sunset("c7", "#1a2438", "#3a4a64", "#6a7a8a", "#9aa4a8")}</defs>
      <rect width={W} height={760} fill="url(#c7)" /><Hills y={640} c="#3a4a50" amp={110} seed={10} dx={-p * 4} /><Hills y={710} c="#26343a" amp={90} seed={15} dx={-p * 8} />
      <rect y="760" width={W} height="400" fill="#242c28" />
      {[240, 1000, 1760].map((x, i) => <Arbusto key={i} x={x} y={850 + 10 * i} s={1.6} c="#0e1412" />)}
      {Array.from({ length: 9 }, (_, i) => { const u = (p * 0.04 + i * 0.1) % 1.2 - 0.1; return <Cang key={i} x={2000 - 2100 * u} y={940 + 22 * (i % 3)} s={1.45} ph={i} flip c="#060808" />; })}
      <Rain o={0.25} /></svg></Sc>);
};
const Cap6b: React.FC = () => {
  const { t } = useT(); const a = S[32][0] - 0.2, p = t - a;
  const dawn = clamp((t - S[34][0]) / 5);
  const shots = [174.9, 175.3, 175.8, 176.2, 176.7, 177.1, 177.6, 178.0];
  const tot = t >= M.onze - 0.2;
  return (<Sc a={a} b={S[40][0] + 0.2} zoom={0.07} ov={<>
    <Cartela at={S[32][0]} to={S[35][0] - 0.2} date="27 DE JULHO DE 1938" sub="GROTA DO ANGICO · SERGIPE" fs={60} />
    <Cartela at={S[35][0]} to={S[36][0] - 0.2} date="28 DE JULHO · 5H" sub="A VOLANTE ABRE FOGO COM METRALHADORAS PORTÁTEIS" fs={56} />
    <Pill at={S[33][0]} to={S[34][0] + 4} x={80} y={360}>LUGAR QUE LAMPIÃO ACHAVA SEGURO</Pill>
    <Pill at={M.vinte - 0.3} to={S[37][0] - 0.1} x={80} y={360}>CERCA DE 20 MINUTOS</Pill>
    {tot && <Big at={M.onze - 0.2} to={S[39][0] - 0.2} x={80} y={300} w={700} size={190} color={P.cream} sub="CANGACEIROS MORTOS">{<>11<span style={{ fontSize: 90, color: P.ochre }}> de 34</span></>}</Big>}
    <Pill at={S[38][0] - 0.1} to={S[39][0] - 0.1} x={80} y={560}>ENTRE ELES: LAMPIÃO E MARIA BONITA</Pill>
    <Pill at={S[39][0] - 0.1} to={S[40][0] + 0.1} x={80} y={420}>QUEM OS TRAIU? NÃO SE SABE AO CERTO</Pill></>}>
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}><defs><linearGradient id="c8" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#10162a" /><stop offset=".6" stopColor={dawn > 0.5 ? "#4a4a6a" : "#1c2438"} /><stop offset="1" stopColor={dawn > 0.5 ? "#a8665a" : "#2a3240"} /></linearGradient></defs>
      <rect width={W} height={800} fill="url(#c8)" /><Hills y={660} c="#1c2630" amp={110} seed={11} dx={0} /><Hills y={730} c="#121a22" amp={90} seed={16} />
      <rect y="780" width={W} height="400" fill="#141a1e" />
      {[260, 620, 980, 1340, 1700].map((x, i) => <Barraca key={i} x={x} y={900 + 20 * (i % 2)} s={1.5} c={i % 2 ? "#2c3038" : "#242830"} />)}
      {[420, 1160, 1520].map((x, i) => <Mandacaru key={i} x={x} y={1010} s={1.4} c="#070a0c" />)}
      {t > S[34][0] && t < S[36][0] + 1 && (<g>{[120, 260, 400, 1500, 1640, 1780].map((x, i) => <Cang key={i} x={x} y={1040 + 16 * (i % 2)} s={1.2} walk={false} c="#030405" />)}</g>)}
      {shots.map((s, i) => <Flash key={i} x={220 + (i % 4) * 160} y={820 + (i % 3) * 60} at={s} big={1.0} />)}{shots.map((s, i) => <Flash key={"b" + i} x={1720 - (i % 4) * 150} y={830 + (i % 3) * 50} at={s + 0.2} big={0.9} />)}
      <Rain o={dawn > 0.8 ? 0.18 : 0.4} />
    </svg></Sc>);
};
// capítulo 7: depois da morte
const Cap7: React.FC = () => {
  const { t } = useT(); const a = S[40][0] - 0.2, p = t - a;
  const yr = Math.round(1938 + 31 * ease((t - (S[41][0] - 1.2)) / 2.0));
  return (<Sc a={a} b={S[46][0] + 0.2} zoom={0.05} ov={<>
    <Cartela at={S[40][0]} to={S[42][0] - 0.2} date="DEPOIS DE ANGICOS" sub="AS CABEÇAS SÃO EXIBIDAS NO NORDESTE E LEVADAS A SALVADOR" fs={54} />
    {t > S[41][0] - 0.2 && t < S[42][0] + 0.5 && <div style={{ position: "absolute", left: 80, top: 360, font: "400 190px DMS", color: P.cream, textShadow: "0 8px 26px rgba(0,0,0,.65)", opacity: ease((t - S[41][0] + 0.2) / 0.5) }}>{yr}<div style={{ font: "700 26px MB", letterSpacing: 5, color: P.ochre }}>SEPULTADAS EM SALVADOR · MAIS DE 30 ANOS DEPOIS</div></div>}
    <Cartela at={S[42][0]} to={S[44][0] - 0.2} date="O FIM DO CANGAÇO" sub="OS OUTROS CHEFES DE BANDO SE ENTREGAM" fs={56} />
    <Cartela at={S[44][0]} to={S[46][0] - 0.2} date="TEORIAS" sub="LAMPIÃO TERIA SOBREVIVIDO? A FILHA, EXPEDITA, AS NEGA" fs={56} /></>}>
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}><defs>{sunset("c9", "#1a1a36", "#4a4a7a", "#b4707a", "#f0b078")}</defs>
      <rect width={W} height={780} fill="url(#c9)" /><Stars n={70} /><circle cx="960" cy={640 - 30 * clamp(p / 20)} r="170" fill="#ffd9a0" opacity=".85" />
      <Hills y={640} c="#4a3a5a" amp={120} seed={8} dx={-p * 3} /><Hills y={720} c="#2e2840" amp={90} seed={14} dx={-p * 6} />
      <rect y="800" width={W} height="400" fill="#1a1824" />
      {[180, 560, 1360, 1740].map((x, i) => <Mandacaru key={i} x={x} y={900 + 12 * (i % 2)} s={1.9} c="#07080d" />)}
    </svg></Sc>);
};
// capítulo 8: legado
const Cap8: React.FC = () => {
  const { t } = useT(); const a = S[46][0] - 0.2;
  const card = (at0: number, x: number, ico: React.ReactNode, ttl: string, sub: string, c: string) => { const at = Math.max(at0, S[46][0] + 2.7); return (<div style={{ position: "absolute", left: x, top: 330, width: 520, opacity: ease((t - at) / 0.5), transform: `translateY(${(1 - ease((t - at) / 0.5)) * 60}px)`, background: "rgba(240,228,201,.96)", borderRadius: 24, boxShadow: "0 20px 50px rgba(0,0,0,.5)", overflow: "hidden" }}>
    <div style={{ height: 230, background: c, display: "grid", placeItems: "center" }}>{ico}</div><div style={{ padding: "20px 26px 26px" }}><div style={{ font: "400 52px DMS", color: P.ink, lineHeight: 1.05 }}>{ttl}</div><div style={{ font: "700 22px MB", letterSpacing: 3, color: "#5a4a30", marginTop: 8 }}>{sub}</div></div></div>); };
  const fim = clamp((t - M.lados + 0.4) / 0.6);
  return (<Sc a={a} b={246.6} zoom={0.02}>
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}><rect width={W} height={H} fill="#14181f" /><g stroke="rgba(240,228,201,.06)" strokeWidth="2">{Array.from({ length: 10 }, (_, i) => <line key={i} x1="0" y1={i * 130} x2={W} y2={i * 130} />)}</g></svg>
    <Cartela at={S[46][0]} to={S[48][0] - 0.2} date="O LEGADO" sub="CORDEL · CINEMA · CARNAVAL" fs={64} />
    {card(M.cordel - 0.2, 150, <svg width="150" height="150" viewBox="0 0 150 150"><rect x="30" y="14" width="90" height="122" rx="6" fill="#f0e4c9" stroke="#2a1e14" strokeWidth="6" /><rect x="44" y="30" width="62" height="40" fill="#b4542e" /><line x1="44" y1="86" x2="106" y2="86" stroke="#2a1e14" strokeWidth="5" /><line x1="44" y1="104" x2="92" y2="104" stroke="#2a1e14" strokeWidth="5" /></svg>, "Cordel", "LITERATURA POPULAR", "#b4542e")}
    {card(M.a1953 - 0.4, 700, <svg width="170" height="150" viewBox="0 0 170 150"><rect x="14" y="40" width="142" height="96" rx="8" fill="#14181f" /><path d="M14 40 L40 14 L156 14 L156 40 Z" fill="#f0e4c9" /><path d="M54 14 L40 40 M94 14 L80 40 M134 14 L120 40" stroke="#14181f" strokeWidth="8" /><polygon points="72,70 72,112 108,91" fill="#d9a441" /></svg>, "O Cangaceiro", "FILME DE LIMA BARRETO · 1953", "#24505f")}
    {card(M.a2023 - 0.4, 1250, <svg width="170" height="150" viewBox="0 0 170 150"><path d="M85 12 L100 56 L146 56 L109 84 L123 128 L85 102 L47 128 L61 84 L24 56 L70 56 Z" fill="#d9a441" stroke="#2a1e14" strokeWidth="5" /></svg>, "Carnaval 2023", "IMPERATRIZ LEOPOLDINENSE · CAMPEÃ", "#1f4d3a")}
    {t > S[48][0] - 0.3 && <AbsoluteFill style={{ opacity: ease((t - S[48][0] + 0.3) / 0.5), background: "#14181f" }}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 110, textAlign: "center", font: "400 120px DMS", color: P.cream, opacity: ease((t - S[48][0]) / 0.5) }}>HERÓI OU BANDIDO?</div>
      <div style={{ position: "absolute", left: 200, top: 360, width: 700, opacity: ease((t - S[48][0] - 0.2) / 0.5), borderLeft: `10px solid ${P.red}`, paddingLeft: 36 }}><div style={{ font: "700 26px MB", letterSpacing: 5, color: P.sand }}>PARA AS AUTORIDADES</div><div style={{ font: "400 110px DMS", color: P.cream, lineHeight: 1.05 }}>brutalidade</div></div>
      <div style={{ position: "absolute", left: 1020, top: 360, width: 700, opacity: ease((t - S[49][0]) / 0.5), borderLeft: `10px solid ${P.ochre}`, paddingLeft: 36 }}><div style={{ font: "700 26px MB", letterSpacing: 5, color: P.sand }}>PARA PARTE DOS SERTANEJOS</div><div style={{ font: "400 110px DMS", color: P.cream, lineHeight: 1.05 }}>bravura</div></div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 690, textAlign: "center", opacity: ease((t - M.crimes + 0.2) / 0.5) }}><span style={{ display: "inline-block", padding: "14px 40px", background: P.ochre, color: P.ink, font: "400 54px DMS", letterSpacing: 2 }}>OS CRIMES DO BANDO E O MITO QUE FICOU</span></div>
      {t > M.voce - 0.2 && <div style={{ position: "absolute", left: 0, right: 0, top: 830, textAlign: "center", font: "400 62px DMS", color: P.cream, opacity: ease((t - M.voce + 0.2) / 0.5) }}>E você, como se lembra dele?</div>}
      <div style={{ position: "absolute", left: 80, right: 80, top: 940, textAlign: "center", font: "italic 400 24px PFI", color: "rgba(240,228,201,.6)", opacity: ease((t - 236) / 0.8) }}>Fontes: Wikipédia (Virgulino Ferreira da Silva, Maria Bonita, Cangaço e Massacre de Angico). Datas de nascimento e números de mortes são estimativas e variam entre os historiadores.</div>
    </AbsoluteFill>}
  </Sc>);
};

// ------------------------------------------------------------ capítulos, progresso, legenda
const CH = [{ t: S[4][0], n: "O MENINO DO SERTÃO" }, { t: S[7][0], n: "A BRIGA QUE MUDOU TUDO" }, { t: S[14][0], n: "O REI DO CANGAÇO" }, { t: S[20][0], n: "CAPITÃO E DERROTA" }, { t: S[24][0], n: "MARIA BONITA" }, { t: S[30][0], n: "ANGICOS, 1938" }, { t: S[40][0], n: "DEPOIS DA MORTE" }, { t: S[46][0], n: "O LEGADO" }];
const Capitulos: React.FC = () => {
  const { t } = useT(); let i = -1; CH.forEach((c, k) => { if (t >= c.t) i = k; }); if (i < 0 || t > 243.5) return null;
  const c = CH[i], u = t - c.t, big = u < 2.6, k = big ? ease(u / 0.5) * clamp((2.6 - u) / 0.4) : 0;
  return (<>
    {big && <div style={{ position: "absolute", left: 0, right: 0, top: 470, textAlign: "center", opacity: k }}><div style={{ display: "inline-block", padding: "22px 60px 26px", background: "rgba(16,20,28,.9)", borderTop: `5px solid ${P.ochre}`, borderBottom: `5px solid ${P.ochre}` }}><div style={{ font: "700 26px MB", letterSpacing: 8, color: P.ochre }}>CAPÍTULO {i + 1}</div><div style={{ font: "400 84px DMS", color: P.cream, letterSpacing: 2 }}>{c.n}</div></div></div>}
    <div style={{ position: "absolute", right: 70, top: 60, font: "700 22px MB", letterSpacing: 4, color: "rgba(240,228,201,.9)", textShadow: "0 2px 10px rgba(0,0,0,.8)", opacity: clamp(u / 0.5) }}>{i + 1}/8 · {c.n}</div></>);
};
const Progresso: React.FC = () => {
  const { t } = useT(); if (t < 12 || t > 243.5) return null;
  const x0 = 80, x1 = 1840, p = (t - 12) / (243.5 - 12);
  return (<svg style={{ position: "absolute", left: 0, top: 1030 }} width={W} height="40"><line x1={x0} y1="20" x2={x1} y2="20" stroke="rgba(240,228,201,.25)" strokeWidth="4" /><line x1={x0} y1="20" x2={x0 + (x1 - x0) * p} y2="20" stroke={P.ochre} strokeWidth="5" />
    {CH.map((c, k) => { const cx = x0 + (x1 - x0) * ((c.t - 12) / 231.5); return <circle key={k} cx={cx} cy="20" r={t >= c.t ? 7 : 5} fill={t >= c.t ? P.ochre : "#2a2f3a"} stroke="rgba(240,228,201,.7)" strokeWidth="2" />; })}</svg>);
};
const Legenda: React.FC = () => {
  const { t } = useT(); const c = (TM.caps as any[]).find((x) => t >= x.t - 0.02 && t < x.e + 0.18); if (!c) return null;
  const u = clamp((t - c.t) / 0.15);
  return (<><div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 300, background: "linear-gradient(to top, rgba(8,6,4,.72), rgba(8,6,4,0))" }} />
    <div style={{ position: "absolute", left: 120, right: 120, bottom: 85, textAlign: "center", font: "400 56px PF", color: P.cream, textShadow: "0 4px 14px rgba(0,0,0,.85), 0 0 4px rgba(0,0,0,.9)", opacity: u, transform: `translateY(${(1 - u) * 14}px)`, lineHeight: 1.15 }}>
      {c.words.map((w: any, i: number) => { const on = t >= w.s && t < w.e + 0.04; return <span key={i} style={{ color: on ? P.ochre : P.cream, display: "inline-block", transform: on ? "scale(1.07)" : "none", marginRight: 16 }}>{w.w}</span>; })}</div></>);
};
export const Lampiao: React.FC = () => {
  const { t } = useT();
  return (<AbsoluteFill style={{ background: "#0d1017" }}><style>{FONT}</style>
    <Abertura /><Cap1a /><Cap1b /><Cap2a /><Cap2b /><Cap3a /><Cap3b /><Cap3c /><Cap4 /><Cap5 /><Cap6a /><Cap6b /><Cap7 /><Cap8 />
    <Vig /><Grain /><Capitulos /><Progresso />{t < 244.6 && <Legenda />}
  </AbsoluteFill>);
};
export const LampiaoCapa: React.FC = () => (
  <AbsoluteFill style={{ background: "#12151c" }}><style>{FONT}</style>
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}><defs>{sunset("cp", "#2b2f5a", "#c0586e", "#f09a62", "#f8cd8a")}</defs>
      <rect width={W} height={H} fill="url(#cp)" /><circle cx="1330" cy="640" r="230" fill="#ffe3a8" opacity=".96" />
      <Hills y={700} c="#8a5a6a" amp={130} seed={4} /><Hills y={790} c="#5a3f50" amp={110} seed={9} /><rect y="850" width={W} height="260" fill="#2a1c18" />
      <Mandacaru x={150} y={960} s={2.4} c="#0a0c10" /><Mandacaru x={1780} y={940} s={2.0} c="#0a0c10" /><Arbusto x={520} y={900} s={2} c="#1a100c" />
      <Cang x={1330} y={880} s={4.6} walk={false} c="#07070b" />
      <text x="90" y="300" fontFamily="MB" fontSize="34" fill="#d9a441" letterSpacing="10">A HISTÓRIA COMPLETA</text>
      <text x="80" y="520" fontFamily="DMS" fontSize="250" fill="#f0e4c9" stroke="#12151c" strokeWidth="14" paintOrder="stroke">LAMPIÃO</text>
      <rect x="90" y="566" width="340" height="8" fill="#d9a441" />
      <text x="90" y="680" fontFamily="PF" fontSize="70" fill="#f0e4c9" stroke="#12151c" strokeWidth="10" paintOrder="stroke">herói ou bandido?</text></svg><Vig />
  </AbsoluteFill>);
