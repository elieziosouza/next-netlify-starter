// Canudos (22/11/2026): documentário animado 2D plano, vertical 1080x1920, 56 s. Tempos: ./can.json (scripts/historia/can_timings.py).
// Novidade: legenda com a palavra falada em dourado.
import React from "react";
import { AbsoluteFill } from "remotion";
import { feature } from "topojson-client";
import { geoMercator, geoPath } from "d3-geo";
import topo from "world-atlas/countries-50m.json";
import TM from "./can.json";
import { P, clamp, ease, rnd, useT, FONT, Grain, Vig, Sc, Puffs, Star, Hills, Cartela, Flash } from "./GuerraParaguai";

const M = TM.M as Record<string, number>;
const SAN = ["Brazil", "Argentina", "Paraguay", "Uruguay", "Bolivia", "Peru", "Colombia", "Venezuela", "Guyana", "Suriname"];
const fc: any = feature(topo as any, (topo as any).objects.countries);
const BR = fc.features.find((f: any) => f.properties.name === "Brazil");
const projB = geoMercator().fitExtent([[70, 340], [1010, 1470]], BR);
const gB = geoPath(projB);
const NEIGH = fc.features.filter((f: any) => SAN.includes(f.properties.name)).map((f: any) => ({ n: f.properties.name as string, d: gB(f) as string })).filter((x: any) => x.d);
const CAN = projB([-39.1, -10.0]) as [number, number];

// ------------------------------------------------------------ peças
const Mandacaru: React.FC<{ x: number; y: number; s?: number; c: string }> = ({ x, y, s = 1, c }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`} fill={c}><rect x="-14" y="-150" width="28" height="150" rx="14" />
    <path d="M-14 -70 L-52 -70 L-52 -118 L-34 -118 L-34 -90 L-14 -90 Z" /><path d="M14 -50 L50 -50 L50 -104 L32 -104 L32 -72 L14 -72 Z" /></g>);
const Arbusto: React.FC<{ x: number; y: number; s?: number; c: string }> = ({ x, y, s = 1, c }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`} stroke={c} strokeWidth="6" fill="none" strokeLinecap="round">
    <path d="M0 0 L0 -60 M0 -30 L-34 -66 M0 -40 L30 -80 M0 -60 L-14 -96 M-34 -66 L-52 -64 M30 -80 L52 -78" /></g>);
const Fig: React.FC<{ x: number; y: number; s?: number; ph?: number; c?: string; bundle?: boolean; rifle?: boolean; walk?: boolean }> = ({ x, y, s = 1, ph = 0, c = "#12151c", bundle, rifle, walk = true }) => {
  const { t } = useT(); const bob = walk ? 4 * Math.sin(t * 6 + ph) : 0, sw = walk ? 7 * Math.sin(t * 6 + ph) : 0;
  return (<g transform={`translate(${x} ${y + bob}) scale(${s})`} fill={c}><circle cx="0" cy="-92" r="13" /><path d="M-15 -76 L15 -76 L18 -22 L-18 -22 Z" />
    <rect x={-16 + sw} y="-22" width="12" height="58" /><rect x={4 - sw} y="-22" width="12" height="58" />
    {bundle && <circle cx="-6" cy="-112" r="16" />}{rifle && <g><line x1="22" y1="-120" x2="22" y2="30" stroke={c} strokeWidth="5" /><path d="M-6 -104 L34 -104 L34 -98 L-6 -98 Z" /></g>}</g>);
};
const Casa: React.FC<{ x: number; y: number; s?: number; fire?: boolean; wall?: string; roof?: string; ruin?: boolean }> = ({ x, y, s = 1, fire, wall = "#c9a171", roof = "#8a6a38", ruin }) => {
  const { t } = useT();
  return (<g transform={`translate(${x} ${y}) scale(${s})`}><rect x="-56" y="-62" width="112" height="62" fill={wall} />
    {ruin ? <path d="M-70 -62 L-20 -88 L0 -70 L30 -92 L70 -62 Z" fill={roof} opacity=".55" /> : <path d="M-74 -60 L0 -118 L74 -60 Z" fill={roof} />}
    <path d="M-14 0 L-14 -38 Q0 -50 14 -38 L14 0 Z" fill="#2a1e14" />
    {fire && <g>{[-40, -10, 24, 46].map((fx, i) => <path key={i} d={`M${fx - 16} -62 Q${fx - 6} ${-100 - 14 * Math.sin(t * 9 + i)} ${fx} ${-128 - 22 * Math.sin(t * 7 + i * 2)} Q${fx + 8} -96 ${fx + 16} -62 Z`} fill={i % 2 ? "#ffb23c" : "#ff6a2a"} opacity=".92" />)}</g>}</g>);
};
const Igreja: React.FC<{ x: number; y: number; s?: number; wall?: string; roof?: string; dark?: boolean }> = ({ x, y, s = 1, wall = "#e4d4b0", roof = "#7a4a2a", dark }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}><rect x="-110" y="-150" width="220" height="150" fill={wall} /><path d="M-124 -146 L0 -230 L124 -146 Z" fill={roof} />
    <rect x="-150" y="-210" width="46" height="210" fill={wall} /><rect x="104" y="-210" width="46" height="210" fill={wall} />
    <path d="M-158 -208 L-127 -250 L-96 -208 Z" fill={roof} /><path d="M96 -208 L127 -250 L158 -208 Z" fill={roof} />
    <path d="M-30 0 L-30 -80 Q0 -108 30 -80 L30 0 Z" fill="#2a1e14" /><circle cx="0" cy="-130" r="16" fill={dark ? "#1a1420" : "#7a6a4a"} />
    <rect x="-3" y="-282" width="6" height="40" fill={dark ? "#1a1420" : "#4a3a22"} /><rect x="-16" y="-270" width="32" height="6" fill={dark ? "#1a1420" : "#4a3a22"} /></g>);

// ------------------------------------------------------------ cena A: sertão ao amanhecer
const CenaA: React.FC = () => {
  const { t } = useT();
  return (<Sc a={0} b={3.7} zoom={0.08} ov={<Cartela at={0.2} to={3.4} date="1893" sub="SERTÃO DA BAHIA" fs={92} />}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="ca" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#3b4a78" /><stop offset=".4" stopColor="#d27a6a" /><stop offset=".72" stopColor="#f4b070" /><stop offset="1" stopColor="#f8d89a" /></linearGradient></defs>
      <rect width="1080" height="1500" fill="url(#ca)" /><Star n={18} /><circle cx="300" cy="900" r="130" fill="#ffe7b0" opacity=".95" />
      <Hills y={950} c="#a4695a" amp={90} seed={5} dx={-t * 3} /><Hills y={1040} c="#7a4e4c" amp={80} seed={9} dx={-t * 6} />
      <rect x="0" y="1120" width="1080" height="800" fill="#b98a4e" />
      <path d="M-40 1330 Q300 1290 560 1330 T1120 1300 L1120 1420 L-40 1420 Z" fill="#a37436" opacity=".6" />
      {[90, 330, 540, 770, 990].map((x, i) => <Arbusto key={i} x={x} y={1170 + 14 * (i % 3)} s={1.2 + 0.5 * rnd(i)} c="#4a3524" />)}
      {[160, 930].map((x, i) => <Mandacaru key={i} x={x} y={1190 + 20 * i} s={1.4 + 0.3 * i} c="#2f4a2e" />)}
      <g opacity=".6">{Array.from({ length: 9 }, (_, i) => <ellipse key={i} cx={100 + i * 120 + 20 * Math.sin(t + i)} cy={1330 + (i % 3) * 28} rx="46" ry="8" fill="#8a5e30" />)}</g>
      {Array.from({ length: 6 }, (_, i) => { const u = (t * 0.1 + i / 6) % 1; return <Fig key={i} x={-40 + 1160 * u} y={1620 + 22 * (i % 3)} s={1.1 - 0.15 * (i % 3)} ph={i * 1.3} bundle={i % 2 === 0} c="#241a12" />; })}
    </svg></Sc>);
};

// ------------------------------------------------------------ cena B: mapa do Brasil
const CenaB: React.FC = () => {
  const { t } = useT(); const a = 3.5, z = 1 + 1.35 * ease((t - 4.4) / 2.0), tx = 540 - CAN[0] * z, ty = 830 - CAN[1] * z;
  return (<Sc a={a} b={9.2} zoom={0} ov={<>
    <Cartela at={M.lider - 0.2} to={8.8} date="ANTÔNIO CONSELHEIRO" sub="FUNDA O ARRAIAL DE BELO MONTE" fs={48} />
    <div style={{ position: "absolute", left: 60, top: 212, font: "italic 400 26px PFI", color: "rgba(40,30,18,.8)" }}>mapa com as fronteiras de hoje</div></>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><rect width="1080" height="1920" fill="#e9dcbc" />
      <g stroke="rgba(120,95,55,.18)" strokeWidth="2">{Array.from({ length: 14 }, (_, i) => <line key={i} x1="0" y1={i * 140} x2="1080" y2={i * 140} />)}{Array.from({ length: 9 }, (_, i) => <line key={i} x1={i * 140} y1="0" x2={i * 140} y2="1920" />)}</g>
      <g transform={`translate(${tx} ${ty}) scale(${z})`}>
        {NEIGH.map((m: any) => <path key={m.n} d={m.d} fill={m.n === "Brazil" ? "#c9a25c" : "#d8c9a5"} stroke="#8a7650" strokeWidth={1.4 / z} strokeLinejoin="round" />)}
        <circle cx={CAN[0]} cy={CAN[1]} r={(26 + 12 * Math.sin(t * 6)) / z * 1.2} fill="none" stroke={P.red} strokeWidth={5 / z} opacity={ease((t - 5.4) / 0.4)} />
        <circle cx={CAN[0]} cy={CAN[1]} r={11 / z * 1.2} fill={P.red} opacity={ease((t - 5.2) / 0.3)} />
        {t > 5.8 && <text x={CAN[0] + 32 / z} y={CAN[1] - 24 / z} fontFamily="MS" fontSize={30 / z} fill={P.ink} stroke="#e9dcbc" strokeWidth={5 / z} paintOrder="stroke" letterSpacing="2">CANUDOS</text>}
        {t > 6.2 && <text x={CAN[0] + 32 / z} y={CAN[1] + 14 / z} fontFamily="PFI" fontSize={24 / z} fill="#3a2a14" stroke="#e9dcbc" strokeWidth={4 / z} paintOrder="stroke">interior da Bahia</text>}
      </g></svg></Sc>);
};

// ------------------------------------------------------------ cena C: o arraial de Belo Monte
const Pill: React.FC<{ at: number; y: number; children: React.ReactNode }> = ({ at, y, children }) => {
  const { t } = useT(); const k = ease((t - at) / 0.4); if (k <= 0) return null;
  return <div style={{ position: "absolute", left: 56, top: y, opacity: k, transform: `translateX(${(1 - k) * -80}px)`, padding: "10px 22px", borderRadius: 40, background: "rgba(240,228,201,.94)", color: P.ink, font: "700 26px MB", letterSpacing: 2 }}>{children}</div>;
};
const CenaC: React.FC = () => {
  const { t } = useT(); const a = 9.0, p = t - a;
  const n = 25 + 5 * ease((t - M.n30) / 1.2); const num = t < M.n30 ? Math.round(25 * ease((t - M.n25) / 0.8)) : Math.round(n);
  return (<Sc a={a} b={21.9} zoom={0.07} ov={<>
    <Cartela at={M.belo - 0.2} to={21.5} date="BELO MONTE" sub="O ARRAIAL JUNTO AO RIO VAZA-BARRIS" fs={64} />
    {t > M.n25 - 0.2 && <div style={{ position: "absolute", right: 56, top: 330, textAlign: "right", opacity: ease((t - M.n25 + 0.2) / 0.5), font: "400 120px DMS", color: P.cream, textShadow: "0 6px 20px rgba(0,0,0,.6)" }}>{num}<span style={{ fontSize: 56 }}> mil</span>
      <div style={{ font: "700 22px MB", letterSpacing: 4, color: P.sand }}>MORADORES · ESTIMATIVA</div></div>}
    <Pill at={M.sertanejos - 0.1} y={520}>SERTANEJOS POBRES</Pill><Pill at={M.exesc - 0.1} y={590}>EX-ESCRAVIZADOS</Pill></>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="cc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#6aa0c8" /><stop offset=".75" stopColor="#f3dcae" /><stop offset="1" stopColor="#f6e4b8" /></linearGradient></defs>
      <rect width="1080" height="1300" fill="url(#cc)" />
      <g transform={`translate(${-p * 5} 0)`}><ellipse cx="260" cy="300" rx="260" ry="40" fill="#fff" opacity=".5" /><ellipse cx="880" cy="230" rx="280" ry="36" fill="#fff" opacity=".4" /></g>
      <Hills y={900} c="#b48a58" amp={100} seed={3} dx={-p * 3} /><Hills y={990} c="#9c7444" amp={80} seed={12} dx={-p * 6} />
      <rect x="0" y="1020" width="1080" height="900" fill="#b9915a" />
      {/* rio Vaza-Barris */}
      <path d="M-40 1130 Q270 1090 540 1130 T1120 1110 L1120 1190 Q820 1210 540 1180 T-40 1200 Z" fill="#6ea6bd" />
      <path d="M-40 1150 Q270 1120 540 1150 T1120 1135" stroke="rgba(255,255,255,.35)" strokeWidth="4" fill="none" />
      <Igreja x={540} y={1330} s={1.0} />
      {[110, 260, 800, 950].map((x, i) => <Casa key={i} x={x} y={1330 + 14 * (i % 2)} s={1.1 + 0.1 * i % 2} wall={i % 2 ? "#d6b583" : "#c9a171"} />)}
      {[{ x: 380, y: 1400 }, { x: 700, y: 1410 }, { x: 40, y: 1420 }, { x: 1040, y: 1400 }].map((c, i) => <Casa key={"b" + i} x={c.x} y={c.y} s={0.95} wall="#bf9565" />)}
      <Puffs x={270} y={1220} n={5} sp={18} sz={22} c="#a8a0a0" /><Puffs x={820} y={1230} n={5} sp={18} sz={24} c="#a8a0a0" />
      <rect x="0" y="1450" width="1080" height="800" fill="#a67a44" />
      {Array.from({ length: 7 }, (_, i) => <Fig key={i} x={((p * 36 + i * 170) % 1300) - 100} y={1580 + 26 * (i % 3)} s={1.1} ph={i * 1.4} bundle={i % 3 === 0} c="#241a12" />)}
      {[70, 1010].map((x, i) => <Mandacaru key={i} x={x} y={1500} s={1.5} c="#2f4a2e" />)}
    </svg></Sc>);
};

// ------------------------------------------------------------ cena D: as expedições
const CenaD: React.FC = () => {
  const { t } = useT(); const a = 21.7, p = t - a;
  return (<Sc a={a} b={32.6} zoom={0.07} ov={<>
    <Cartela at={M.repub - 0.3} to={32.2} date="A REPÚBLICA ENVIA TROPAS" sub={t >= M.nov ? "PRIMEIRA EXPEDIÇÃO · NOVEMBRO DE 1896" : "SUSPEITA DE CONSPIRAÇÃO MONARQUISTA"} fs={50} />
    <div style={{ position: "absolute", right: 56, top: 330, display: "flex", gap: 12 }}>{[0, 1, 2, 3].map((i) => { const on = t >= M.primeira + i * 0.3 || (i === 3 && t >= M.quarta - 0.2), x = i < 3 && t >= M.fracas + i * 0.14;
      return <div key={i} style={{ width: 64, height: 64, borderRadius: "50%", border: `5px solid ${on ? P.cream : "rgba(240,228,201,.25)"}`, background: x ? P.red : i === 3 && on ? P.ochre : "rgba(0,0,0,.3)", display: "grid", placeItems: "center", color: i === 3 && on && !x ? P.ink : P.cream, font: "800 32px MS" }}>{x ? "✕" : on ? i + 1 : ""}</div>; })}</div></>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="cd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#4a5c7a" /><stop offset=".55" stopColor="#d49a78" /><stop offset="1" stopColor="#ecc896" /></linearGradient></defs>
      <rect width="1080" height="1300" fill="url(#cd)" />
      <Hills y={930} c="#8a6a5a" amp={100} seed={4} dx={-p * 4} /><Hills y={1020} c="#6a5448" amp={80} seed={13} dx={-p * 8} />
      <rect x="0" y="1060" width="1080" height="900" fill="#a3763e" />
      {[130, 560, 940].map((x, i) => <Mandacaru key={i} x={x} y={1130 + 12 * i} s={1.2} c="#3a5a38" />)}
      <path d="M-40 1500 Q400 1440 1120 1380" stroke="#d9b07a" strokeWidth="80" fill="none" strokeLinecap="round" opacity=".5" />
      {/* tropa em marcha, em fila */}
      {Array.from({ length: 11 }, (_, i) => { const u = (p * 0.07 + i * 0.075) % 1.15 - 0.05; return <Fig key={i} x={-60 + 1200 * u} y={1520 - 100 * u + 22 * (i % 2)} s={1.3 - 0.35 * u} ph={i * 0.9} rifle c="#1c1822" />; })}
      {/* bandeira da tropa */}
      <g opacity={ease((p - 2) / 0.6)}><line x1="940" y1="1100" x2="940" y2="1260" stroke="#2a1e14" strokeWidth="5" /><path d={`M940 1100 Q${980 + 8 * Math.sin(t * 4)} 1112 1030 1106 L1030 1160 Q${980 + 8 * Math.sin(t * 4)} 1166 940 1156 Z`} fill="#3a5a8a" /></g>
    </svg></Sc>);
};

// ------------------------------------------------------------ cena E: cerco e bombardeio
const CenaE: React.FC = () => {
  const { t } = useT(); const a = 32.4, p = t - a;
  const shots = [34.6, 35.3, 36.0, 36.9, 37.6, 38.3];
  return (<Sc a={a} b={39.7} zoom={0.09} ov={<Cartela at={M.quarta - 0.3} to={39.3} date="QUARTA EXPEDIÇÃO" sub="PERTO DE 10 MIL HOMENS" fs={64} />}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="ce" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#241d2e" /><stop offset=".55" stopColor="#8a4638" /><stop offset="1" stopColor="#e88a46" /></linearGradient></defs>
      <rect width="1080" height="1400" fill="url(#ce)" />
      <circle cx="540" cy="1060" r="500" fill="#ff9a3c" opacity=".15" />
      <Hills y={970} c="#3a2428" amp={90} seed={5} dx={-p * 4} />
      <rect x="0" y="1060" width="1080" height="900" fill="#33231a" />
      <Puffs x={200} y={1040} n={9} sp={24} sz={40} c="#2c262c" /><Puffs x={600} y={1060} n={9} sp={24} sz={44} c="#2c262c" />
      <Igreja x={420} y={1250} s={0.9} wall="#6a5238" roof="#2e2018" dark />
      <Casa x={110} y={1270} s={1.2} fire wall="#7a5a3a" roof="#3a2a1a" /><Casa x={720} y={1260} s={1.2} fire wall="#7a5a3a" roof="#3a2a1a" /><Casa x={920} y={1280} s={1.1} fire wall="#7a5a3a" roof="#3a2a1a" />
      {/* cerco: tropa em semicírculo em primeiro plano */}
      {[0, 1, 2, 3, 4, 5].map((i) => <Fig key={i} x={80 + i * 180} y={1600 + 22 * (i % 2)} s={1.25} ph={i * 1.2} rifle walk={false} c="#0e0c10" />)}
      <g><rect x="840" y="1470" width="200" height="34" rx="12" fill="#14121a" transform="rotate(-9 840 1480)" /><circle cx="950" cy="1520" r="44" fill="#14121a" /><circle cx="950" cy="1520" r="20" fill="#2a2630" /></g>
      {shots.map((s, i) => <Flash key={i} x={840} y={1460} at={s} big={1.1} />)}{shots.map((s, i) => <Flash key={"b" + i} x={140 + (i % 3) * 300} y={1230} at={s + 0.45} big={0.8} />)}
    </svg></Sc>);
};

// ------------------------------------------------------------ cena F: 5 de outubro de 1897
const CenaF: React.FC = () => {
  const { t } = useT(); const a = 39.5, p = t - a;
  const k = ease((t - M.n15 + 0.2) / 0.5);
  return (<Sc a={a} b={48.9} zoom={0.1} ov={<>
    <Cartela at={M.cai - 0.2} to={43.5} date="5 DE OUTUBRO DE 1897" sub="CANUDOS CAI" fs={56} />
    {t > M.guerra - 0.3 && <div style={{ position: "absolute", left: 0, right: 0, top: 330, textAlign: "center", opacity: ease((t - M.guerra + 0.3) / 0.5) }}>
      <div style={{ font: "700 24px MB", letterSpacing: 6, color: P.sand }}>MORTOS · ESTIMATIVA</div>
      <div style={{ font: "400 130px DMS", color: P.cream, textShadow: "0 6px 20px rgba(0,0,0,.6)", opacity: Math.max(0.0, k) }}>{t >= M.n30b ? "15 a 30 mil" : t >= M.n15 ? "15 mil" : "—"}</div></div>}</>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="cf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#151a36" /><stop offset=".5" stopColor="#4a4a7a" /><stop offset=".8" stopColor="#d98b78" /><stop offset="1" stopColor="#f3c58a" /></linearGradient></defs>
      <rect width="1080" height="1500" fill="url(#cf)" /><Star n={60} />
      <circle cx="540" cy={1010 - 30 * clamp(p / 8)} r="150" fill="#ffd9a0" opacity=".85" />
      <Hills y={970} c="#5a4c6a" amp={110} seed={8} dx={-p * 3} /><Hills y={1070} c="#3a3250" amp={90} seed={14} dx={-p * 6} />
      <rect x="0" y="1190" width="1080" height="800" fill="#1d1a2a" />
      <Igreja x={540} y={1330} s={1.0} wall="#2a2438" roof="#161220" dark />
      {[{ x: 160, y: 1350 }, { x: 330, y: 1380 }, { x: 760, y: 1380 }, { x: 930, y: 1350 }].map((c, i) => <Casa key={i} x={c.x} y={c.y} s={1.05} ruin wall="#2a2438" roof="#161220" />)}
      <Puffs x={170} y={1260} n={5} sp={22} sz={26} c="#3a3444" /><Puffs x={930} y={1260} n={5} sp={22} sz={26} c="#3a3444" /><Puffs x={540} y={1100} n={5} sp={22} sz={28} c="#3a3444" />
      {[60, 1020].map((x, i) => <Mandacaru key={i} x={x} y={1450} s={1.8} c="#0c0f18" />)}
    </svg></Sc>);
};

// ------------------------------------------------------------ cena G: o livro
const CenaG: React.FC = () => {
  const { t } = useT(); const a = 48.7;
  const k = ease((t - M.sertoes + 0.6) / 0.8);
  return (<Sc a={a} b={56.2} zoom={0.02}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><rect width="1080" height="1920" fill="#14181f" /><g stroke="rgba(240,228,201,.06)" strokeWidth="2">{Array.from({ length: 14 }, (_, i) => <line key={i} x1="0" y1={i * 140} x2="1080" y2={i * 140} />)}</g></svg>
    <div style={{ position: "absolute", left: 270, top: 330, width: 540, height: 760, opacity: k, transform: `scale(${0.85 + 0.15 * k}) rotate(-2deg)`, background: "#6b3a22", borderRadius: "12px 26px 26px 12px", boxShadow: "0 24px 60px rgba(0,0,0,.6)", overflow: "hidden", borderLeft: "26px solid #4a2616" }}>
      <div style={{ margin: "56px 36px 0", border: `4px solid ${P.ochre}`, height: 640, padding: "40px 20px", textAlign: "center", boxSizing: "border-box" }}>
        <div style={{ font: "700 26px MB", letterSpacing: 6, color: P.ochre }}>EUCLIDES DA CUNHA</div>
        <div style={{ font: "400 120px DMS", color: P.cream, lineHeight: 1, marginTop: 70 }}>Os<br />Sertões</div>
        <div style={{ width: 120, height: 5, background: P.ochre, margin: "46px auto 0" }} /></div></div>
    {t > M.livros - 0.3 && <div style={{ position: "absolute", left: 0, right: 0, top: 1170, textAlign: "center", opacity: ease((t - M.livros + 0.3) / 0.5) }}>
      <span style={{ display: "inline-block", padding: "14px 36px", background: P.ochre, color: P.ink, font: "400 46px DMS", letterSpacing: 2 }}>UM LIVRO FUNDAMENTAL DA LITERATURA BRASILEIRA</span></div>}
    <div style={{ position: "absolute", left: 80, right: 80, top: 1450, textAlign: "center", font: "italic 400 27px PFI", color: "rgba(240,228,201,.65)", opacity: ease((t - 52.2) / 0.8) }}>Fonte: Wikipédia (Guerra de Canudos). Números de moradores e de mortos são estimativas.</div>
  </Sc>);
};

// ------------------------------------------------------------ legenda com palavra falada em dourado
const Legenda: React.FC = () => {
  const { t } = useT(); const c = (TM.caps as any[]).find((x) => t >= x.t - 0.02 && t < x.e + 0.18); if (!c) return null;
  const u = clamp((t - c.t) / 0.15);
  return (<><div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 520, background: "linear-gradient(to top, rgba(8,6,4,.72), rgba(8,6,4,0))" }} /><div style={{ position: "absolute", left: 70, right: 70, bottom: 150, textAlign: "center", font: "400 56px PF", color: P.cream, textShadow: "0 4px 14px rgba(0,0,0,.85), 0 0 4px rgba(0,0,0,.9)", opacity: u, transform: `translateY(${(1 - u) * 14}px)`, lineHeight: 1.15 }}>
    {c.words.map((w: any, i: number) => { const on = t >= w.s && t < w.e + 0.04; return <span key={i} style={{ color: on ? P.ochre : P.cream, display: "inline-block", transform: on ? "scale(1.07)" : "none", marginRight: 14 }}>{w.w}</span>; })}</div></>);
};
export const Canudos: React.FC = () => {
  const { t } = useT();
  return (<AbsoluteFill style={{ background: "#0d1017" }}><style>{FONT}</style>
    <CenaA /><CenaB /><CenaC /><CenaD /><CenaE /><CenaF /><CenaG /><Vig /><Grain />{t < 55.2 && <Legenda />}
  </AbsoluteFill>);
};
export const CanudosCapa: React.FC = () => (
  <AbsoluteFill style={{ background: "#161b24" }}><style>{FONT}</style>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs><linearGradient id="cp" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#3b4a78" /><stop offset=".5" stopColor="#d27a6a" /><stop offset=".8" stopColor="#f4b070" /><stop offset="1" stopColor="#f8d89a" /></linearGradient></defs>
      <rect width="1080" height="1920" fill="#161b24" /><rect y="640" width="1080" height="920" fill="url(#cp)" /><circle cx="330" cy="1180" r="150" fill="#ffe7b0" opacity=".95" />
      <Hills y={1190} c="#a4695a" amp={120} seed={5} /><Hills y={1290} c="#7a4e4c" amp={100} seed={9} />
      <rect y="1370" width="1080" height="190" fill="#b98a4e" />
      <Igreja x={640} y={1440} s={0.8} wall="#2a2438" roof="#161220" dark />
      {[{ x: 380, y: 1450 }, { x: 900, y: 1455 }].map((c, i) => <Casa key={i} x={c.x} y={c.y} s={0.85} wall="#2a2438" roof="#161220" />)}
      <Mandacaru x={110} y={1490} s={1.8} c="#0c0f18" /><Mandacaru x={1010} y={1500} s={1.5} c="#0c0f18" />
      <rect y="1556" width="1080" height="364" fill="#161b24" /><rect y="636" width="1080" height="6" fill="#d9a441" /><rect y="1552" width="1080" height="6" fill="#d9a441" />
      <text x="540" y="195" textAnchor="middle" fontFamily="MB" fontSize="27" fill="#d9a441" letterSpacing="7">SERTÃO DA BAHIA · 1893 A 1897</text>
      <text x="540" y="400" textAnchor="middle" fontFamily="DMS" fontSize="190" fill="#f0e4c9">Canudos</text><rect x="440" y="470" width="200" height="6" fill="#d9a441" />
      <text x="540" y="560" textAnchor="middle" fontFamily="PFI" fontSize="44" fill="#f0e4c9">a guerra que virou livro</text>
      <text x="540" y="1690" textAnchor="middle" fontFamily="DMS" fontSize="60" fill="#f0e4c9">De arraial a guerra</text><text x="540" y="1768" textAnchor="middle" fontFamily="DMS" fontSize="60" fill="#d9a441">em 4 expedições</text></svg><Vig />
  </AbsoluteFill>
);
