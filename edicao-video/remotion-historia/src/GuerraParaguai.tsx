// Guerra do Paraguai (21/11/2026): documentário animado 2D plano, vertical 1080x1920, 58,7 s. Tempos: ./gp.json (gp/build_timings.py).
// Cenários em camadas com profundidade, mapa real (Natural Earth via world-atlas, fronteiras atuais), cartelas de data e números animados.
import React, { useMemo } from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, staticFile } from "remotion";
import { feature } from "topojson-client";
import { geoMercator, geoPath } from "d3-geo";
import topo from "world-atlas/countries-50m.json";
import TM from "./gp.json";

const M = TM.M as Record<string, number>;
const P = { ink: "#12161d", night: "#101a2b", deep: "#1b2a3d", teal: "#24505f", terra: "#c2603a", ochre: "#d9a441", cream: "#f0e4c9", sand: "#cdb98f",
  red: "#b3362b", olive: "#6f8f5a", slate: "#5f84a0", water: "#1f4558", smoke: "#8d8f98" };
const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
const rnd = (a: number) => { const x = Math.sin(a * 127.1 + 4.1) * 43758.5453; return x - Math.floor(x); };
const useT = () => { const f = useCurrentFrame(); const { fps } = useVideoConfig(); return { t: f / fps, f, fps }; };
const FONT = `
@font-face{font-family:DMS;src:url(${staticFile("fonts/DMSerifDisplay-Regular.ttf")})}
@font-face{font-family:PF;src:url(${staticFile("fonts/PlayfairDisplay-Regular.ttf")})}
@font-face{font-family:PFI;src:url(${staticFile("fonts/PlayfairDisplay-Italic.ttf")})}
@font-face{font-family:MS;font-weight:800;src:url(${staticFile("fonts/Montserrat-ExtraBold.ttf")})}
@font-face{font-family:MB;font-weight:700;src:url(${staticFile("fonts/Montserrat-Bold.ttf")})}
@font-face{font-family:AN;src:url(${staticFile("fonts/Anton-Regular.ttf")})}`;

// ------------------------------------------------------------ mapa
const SA = ["Brazil", "Argentina", "Paraguay", "Uruguay", "Bolivia", "Chile", "Peru", "Colombia", "Venezuela", "Ecuador", "Guyana", "Suriname"];
const fc: any = feature(topo as any, (topo as any).objects.countries);
const saF = fc.features.filter((f: any) => SA.includes(f.properties.name));
const proj = geoMercator().fitExtent([[60, 300], [1020, 1480]], { type: "FeatureCollection", features: saF } as any);
const gp = geoPath(proj);
const MAP = saF.map((f: any) => ({ name: f.properties.name as string, d: gp(f) as string, c: gp.centroid(f) as [number, number] }));
const pt = (lon: number, lat: number) => proj([lon, lat]) as [number, number];
const ASU = pt(-57.63, -25.28), COR = pt(-57.65, -19.0), RIO = pt(-43.2, -22.9), BUE = pt(-58.4, -34.6), MON = pt(-56.2, -34.9), PAR = pt(-58.0, -23.4);

const Grain: React.FC = () => {
  const { f } = useT();
  return (<AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "multiply", opacity: 0.32 }}>
    <svg width="1080" height="1920"><filter id="gr"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed={f % 9} /><feColorMatrix values="0 0 0 0 .3  0 0 0 0 .22  0 0 0 0 .12  0 0 0 .9 -.12" /></filter><rect width="1080" height="1920" filter="url(#gr)" /></svg>
  </AbsoluteFill>);
};
const Vig: React.FC = () => <AbsoluteFill style={{ pointerEvents: "none", background: "radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 52%, rgba(8,6,4,.62) 100%)" }} />;

// ------------------------------------------------------------ peças reutilizáveis
const Sc: React.FC<{ a: number; b: number; zoom?: number; ov?: React.ReactNode; children: React.ReactNode }> = ({ a, b, zoom = 0.07, ov, children }) => {
  const { t } = useT(); if (t < a - 0.01 || t > b + 0.01) return null;
  const k = clamp((t - a) / 0.35) * clamp((b - t) / 0.35), p = clamp((t - a) / (b - a));
  return (<AbsoluteFill style={{ opacity: k }}>
    <div style={{ position: "absolute", inset: 0, transform: `scale(${1 + zoom * p})`, transformOrigin: "50% 42%" }}>{children}</div>{ov}
  </AbsoluteFill>);
};
const Puffs: React.FC<{ x: number; y: number; n?: number; sp?: number; c?: string; sz?: number }> = ({ x, y, n = 7, sp = 42, c = P.smoke, sz = 26 }) => {
  const { t } = useT();
  return (<g>{Array.from({ length: n }, (_, i) => { const ph = ((t * sp / 220 + i / n) % 1), r = sz * (0.5 + 1.6 * ph);
    return <circle key={i} cx={x + ph * 120 + 10 * Math.sin(i * 3 + t)} cy={y - ph * 220} r={r} fill={c} opacity={0.55 * (1 - ph)} />; })}</g>);
};
const Water: React.FC<{ y: number; h?: number; c?: string; line?: string; amp?: number }> = ({ y, h = 600, c = P.water, line = "rgba(255,255,255,.12)", amp = 6 }) => {
  const { t } = useT();
  return (<g><rect x="-50" y={y} width="1180" height={h} fill={c} />
    {Array.from({ length: 14 }, (_, i) => { const yy = y + 24 + i * (h / 14) * 0.95, w = 80 + 60 * rnd(i), x0 = ((rnd(i + 9) * 1200 + t * (30 + 9 * (i % 4)) * (i % 2 ? 1 : -1)) % 1300) - 100;
      return <path key={i} d={`M${x0} ${yy} q${w / 4} ${-amp} ${w / 2} 0 t${w / 2} 0`} stroke={line} strokeWidth={3 + (i / 6)} fill="none" strokeLinecap="round" />; })}</g>);
};
const Vapor: React.FC<{ x: number; y: number; s?: number; flip?: boolean; name?: string; pennant?: string; smoke?: boolean; tilt?: number }> = ({ x, y, s = 1, flip, name, pennant = P.red, smoke = true, tilt = 0 }) => {
  const { t } = useT();
  return (<g transform={`translate(${x} ${y}) rotate(${tilt}) scale(${flip ? -s : s} ${s})`}>
    {smoke && <Puffs x={-35} y={-170} />}
    <path d="M-170 0 L170 0 L136 48 L-136 48 Z" fill="#161c28" /><rect x="-166" y="-6" width="332" height="9" fill={P.ochre} opacity=".9" />
    <rect x="-118" y="-54" width="214" height="50" fill={P.sand} /><rect x="-90" y="-104" width="150" height="50" fill={P.cream} />
    {[-70, -35, 0, 35].map((wx) => <rect key={wx} x={wx - 9} y="-90" width="18" height="24" rx="3" fill="#f2c36b" />)}
    <rect x="-100" y="-112" width="190" height="9" fill="#222" /><rect x="-60" y="-174" width="26" height="62" fill="#222" /><rect x="6" y="-166" width="22" height="56" fill="#222" />
    <rect x="-62" y="-178" width="30" height="9" fill={P.red} /><rect x="4" y="-170" width="26" height="8" fill={P.red} />
    <line x1="74" y1="-104" x2="74" y2="-196" stroke="#222" strokeWidth="4" /><path d="M74 -196 L134 -178 L74 -160 Z" fill={pennant} />
    <g transform="translate(-132 8)"><circle r="40" fill="none" stroke="#222" strokeWidth="6" />{Array.from({ length: 8 }, (_, i) => { const a = (t * 2.2 + i * Math.PI / 4);
      return <line key={i} x1="0" y1="0" x2={40 * Math.cos(a)} y2={40 * Math.sin(a)} stroke="#222" strokeWidth="5" />; })}</g>
    {name && <text x="0" y="33" textAnchor="middle" fontFamily="MB" fontSize="17" fill={P.cream} letterSpacing="3" transform={flip ? "scale(-1 1)" : undefined}>{name}</text>}
  </g>);
};
const Flash: React.FC<{ x: number; y: number; at: number; big?: number }> = ({ x, y, at, big = 1 }) => {
  const { t } = useT(); const u = (t - at) / 0.5; if (u < 0 || u > 1) return null;
  return (<g><circle cx={x} cy={y} r={(30 + 90 * u) * big} fill={P.ochre} opacity={(1 - u) * 0.9} /><circle cx={x} cy={y} r={(14 + 40 * u) * big} fill="#fff6d0" opacity={1 - u} />
    <circle cx={x + 40 * u} cy={y - 50 * u} r={(40 + 80 * u) * big} fill={P.smoke} opacity={0.45 * (1 - u)} /></g>);
};
const Star: React.FC<{ n?: number }> = ({ n = 60 }) => (<g>{Array.from({ length: n }, (_, i) => <circle key={i} cx={rnd(i) * 1080} cy={rnd(i + 50) * 800} r={1 + 2 * rnd(i + 99)} fill="#fff" opacity={0.3 + 0.5 * rnd(i + 7)} />)}</g>);
const Hills: React.FC<{ y: number; c: string; amp?: number; seed?: number; dx?: number }> = ({ y, c, amp = 90, seed = 1, dx = 0 }) => {
  let d = `M-60 ${y + 400} L-60 ${y}`; for (let i = 0; i <= 12; i++) d += ` L${i * 100 - 60 + dx} ${y - amp * (0.5 + 0.5 * Math.sin(i * 1.3 + seed) * rnd(i + seed))}`; d += ` L1200 ${y + 400} Z`;
  return <path d={d} fill={c} />;
};
const Cartela: React.FC<{ at: number; to: number; date: string; sub?: string; y?: number; fs?: number }> = ({ at, to, date, sub, y = 130, fs = 58 }) => {
  const { t } = useT(); if (t < at || t > to + 0.4) return null;
  const k = ease((t - at) / 0.5) * clamp((to + 0.4 - t) / 0.4);
  return (<div style={{ position: "absolute", left: 56 + (1 - k) * -520, top: y, opacity: k, padding: "16px 30px 18px", background: "rgba(16,20,28,.86)", borderLeft: `8px solid ${P.ochre}`, boxShadow: "0 10px 30px rgba(0,0,0,.4)" }}>
    <div style={{ font: `400 ${fs}px DMS`, color: P.cream, letterSpacing: 1.5, lineHeight: 1.05 }}>{date}</div>
    {sub && <div style={{ font: "700 26px MB", color: P.ochre, letterSpacing: 4, marginTop: 8 }}>{sub}</div>}
  </div>);
};

// ------------------------------------------------------------ cena 1: porto de Assunção ao entardecer
const Porto: React.FC = () => {
  const { t } = useT(); const stop = ease(t / 3.2), x1 = -380 + 760 * stop;
  const gb = ease((t - 3.5) / 1.8), x2 = 1500 - 520 * gb;
  return (<Sc a={0} b={7.1} zoom={0.08} ov={<>
    <Cartela at={M.d1} to={6.6} date="11 DE NOVEMBRO DE 1864" sub="PORTO DE ASSUNÇÃO" /></>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#1c2440" /><stop offset=".55" stopColor="#8a4a52" /><stop offset=".82" stopColor="#e08a4a" /><stop offset="1" stopColor="#f2b66a" /></linearGradient></defs>
      <rect width="1080" height="1250" fill="url(#dusk)" /><Star n={40} />
      <circle cx="800" cy="930" r="120" fill="#ffd89a" opacity=".85" />
      <g transform={`translate(${-t * 4} 0)`}><Hills y={980} c="#3a3246" amp={80} seed={2} dx={0} /></g>
      <Hills y={1040} c="#2b2538" amp={70} seed={5} dx={-30} />
      {/* cidade ao fundo */}
      <g fill="#1d1a26">{Array.from({ length: 16 }, (_, i) => <rect key={i} x={30 + i * 66} y={1010 - 30 * rnd(i + 3)} width={44 + 14 * rnd(i)} height={50 + 30 * rnd(i + 3)} />)}<circle cx="470" cy="985" r="30" /><rect x="466" y="940" width="8" height="30" /></g>
      <Water y={1090} h={900} c="#173a4d" />
      <g opacity=".5"><ellipse cx="800" cy="1180" rx="90" ry="10" fill="#ffd89a" /><ellipse cx="800" cy="1230" rx="60" ry="8" fill="#ffd89a" /></g>
      {/* cais */}
      <rect x="900" y="1000" width="260" height="22" fill="#3b2c24" />{[920, 980, 1040, 1100].map((px) => <rect key={px} x={px} y="1022" width="12" height="100" fill="#2a1f1a" />)}
      <rect x="1010" y="905" width="8" height="100" fill="#2a1f1a" /><circle cx="1014" cy="900" r="18" fill="#ffe29a" /><circle cx="1014" cy="900" r="46" fill="#ffe29a" opacity=".25" />
      <Vapor x={x1} y={1160} s={1.35} name="MARQUÊS DE OLINDA" />
      {t > 3.5 && <g><Vapor x={x2} y={1290} s={0.95} flip pennant={P.red} name="" /></g>}
      {t > 5.0 && <g transform={`translate(${x2 - 40} ${1235})`}><circle r={16 + 6 * Math.sin(t * 9)} fill={P.red} opacity=".0" /></g>}
    </svg></Sc>);
};

// ------------------------------------------------------------ cena 2 e 3: mapa
const NAME_PT: Record<string, string> = { Paraguay: "PARAGUAI", Brazil: "BRASIL", Argentina: "ARGENTINA", Uruguay: "URUGUAI" };
const Draw: React.FC<{ d: string; p: number; c: string; w?: number; arrow?: boolean; dash?: string }> = ({ d, p, c, w = 12, dash }) => (
  <path d={d} pathLength={1} fill="none" stroke={c} strokeWidth={w} strokeLinecap="round" strokeDasharray={dash ?? "1"} strokeDashoffset={dash ? 0 : 1 - clamp(p)} opacity={clamp(p * 6)} />);
const Seta: React.FC<{ a: [number, number]; b: [number, number]; p: number; c: string; bend?: number }> = ({ a, b, p, c, bend = 0.18 }) => {
  const mx = (a[0] + b[0]) / 2 + (b[1] - a[1]) * bend, my = (a[1] + b[1]) / 2 - (b[0] - a[0]) * bend;
  const ang = Math.atan2(b[1] - my, b[0] - mx), L = 40;
  return (<g><Draw d={`M${a[0]} ${a[1]} Q${mx} ${my} ${b[0]} ${b[1]}`} p={p} c={c} />
    {p > 0.92 && <path d={`M${b[0]} ${b[1]} L${b[0] - L * Math.cos(ang - 0.45)} ${b[1] - L * Math.sin(ang - 0.45)} M${b[0]} ${b[1]} L${b[0] - L * Math.cos(ang + 0.45)} ${b[1] - L * Math.sin(ang + 0.45)}`} stroke={c} strokeWidth="12" strokeLinecap="round" fill="none" />}</g>);
};
const Mapa: React.FC = () => {
  const { t } = useT();
  const w2 = ease((t - 14.6) / 1.4), AVG: [number, number] = [(RIO[0] + BUE[0] + MON[0] + ASU[0]) / 4, (RIO[1] + BUE[1] + MON[1] + ASU[1]) / 4];
  const z = (2.2 - 1.2 * ease((t - 7.0) / 7.2)) * (1 - w2) + 1.3 * w2, cx = PAR[0] * (1 - w2) + AVG[0] * w2, cy = PAR[1] * (1 - w2) + AVG[1] * w2;
  const tx = 540 - cx * z, ty = 800 - cy * z;
  const aliad = ease((t - M.brasil + 0.4) / 1.2);                      // Tríplice Aliança entra
  const pPar = ease((t - 7.2) / 0.8) , pMT = ease((t - 11.6) / 2.0);
  const colorOf = (n: string) => {
    if (n === "Paraguay") return t > 7.2 ? (t > 14.6 ? P.terra : `hsl(${16 + 0}, 56%, ${46 + 6 * Math.sin(t * 4)}%)`) : "#d8c9a5";
    if (aliad > 0) { if (n === "Brazil") return P.olive; if (n === "Argentina") return P.slate; if (n === "Uruguay") return P.ochre; }
    return "#d8c9a5";
  };
  const labels = t > 14.6 ? ["Paraguay", "Brazil", "Argentina", "Uruguay"] : t > 7.4 ? ["Paraguay"] : [];
  return (<Sc a={6.8} b={22.4} zoom={0} ov={<>
    <Cartela at={M.maior - 0.2} to={11.5} date="A MAIOR GUERRA DA AMÉRICA DO SUL" fs={44} y={130} />
    <Cartela at={11.9} to={M.maio - 0.4} date="DEZEMBRO DE 1864" sub="INVASÃO DE MATO GROSSO" />
    <Cartela at={M.maio} to={22.0} date="1º DE MAIO DE 1865" sub="TRÍPLICE ALIANÇA" />
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 285, textAlign: "center", font: "italic 400 26px PFI", color: "rgba(40,30,18,.75)" }}>mapa com as fronteiras de hoje</div></>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920">
      <rect width="1080" height="1920" fill="#e9dcbc" />
      <g stroke="rgba(120,95,55,.18)" strokeWidth="2">{Array.from({ length: 14 }, (_, i) => <line key={i} x1="0" y1={i * 140} x2="1080" y2={i * 140} />)}{Array.from({ length: 9 }, (_, i) => <line key={i} x1={i * 140} y1="0" x2={i * 140} y2="1920" />)}</g>
      <g transform={`translate(${tx} ${ty}) scale(${z})`}>
        {MAP.map((m: any) => <path key={m.name} d={m.d} fill={colorOf(m.name)} stroke="#8a7650" strokeWidth={1.4 / z * 1.2} strokeLinejoin="round" />)}
        {t > 11.5 && t < 16.2 && <Seta a={ASU} b={COR} p={pMT} c={P.red} bend={-0.2} />}
        {t > 11.5 && t < 16.2 && <circle cx={COR[0]} cy={COR[1]} r={(10 + 8 * Math.sin(t * 6)) / z * 1.4} fill="none" stroke={P.red} strokeWidth={4 / z} opacity={pMT} />}
        {aliad > 0 && <g>
          <Seta a={RIO} b={ASU} p={ease((t - M.brasil) / 1.0)} c="#14202b" bend={0.15} />
          <Seta a={BUE} b={ASU} p={ease((t - M.brasil - 0.5) / 1.0)} c="#14202b" bend={-0.15} />
          <Seta a={MON} b={ASU} p={ease((t - M.brasil - 1.0) / 1.0)} c="#14202b" bend={0.28} /></g>}
        {[RIO, BUE, MON, ASU].map((q, i) => (i < 3 ? aliad > 0 : t > 7.4) && <circle key={i} cx={q[0]} cy={q[1]} r={9 / z * 1.4} fill={i === 3 ? P.red : P.ink} />)}
        {labels.map((n) => { const m = MAP.find((x: any) => x.name === n)!; const off: Record<string, [number, number]> = { Paraguay: [-70, -75], Argentina: [-190, 40], Uruguay: [150, 60], Brazil: [0, 0] }; const o = off[n] ?? [0, 0]; return <text key={n} x={m.c[0] + o[0] / z * (n === "Paraguay" && t < 14.6 ? 0.2 : 1)} y={m.c[1] + o[1] / z * (n === "Paraguay" && t < 14.6 ? 0.2 : 1)} textAnchor="middle" fontFamily="MS" fontSize={34 / z * 1.1} fill={n === "Paraguay" ? "#fff6e0" : P.ink} stroke={n === "Paraguay" ? "rgba(60,20,8,.8)" : "none"} strokeWidth={5 / z} paintOrder="stroke" letterSpacing="3">{NAME_PT[n]}</text>; })}
      </g>
      {t > M.segredo - 0.1 && t < 22.2 && (() => { const u = ease((t - M.segredo) / 0.25); return <g transform={`translate(780 1560) rotate(-9) scale(${1.9 - 0.9 * u})`} opacity={u}>
        <rect x="-170" y="-48" width="340" height="96" rx="8" fill="rgba(179,54,43,.08)" stroke={P.red} strokeWidth="8" /><text x="0" y="18" textAnchor="middle" fontFamily="AN" fontSize="64" fill={P.red} letterSpacing="6">EM SEGREDO</text></g>; })()}
    </svg></Sc>);
};

// ------------------------------------------------------------ cena 4: Riachuelo
const Riachuelo: React.FC = () => {
  const { t } = useT(); const a = 22.4, drift = (t - a) * 18;
  const shoot = [23.1, 23.55, 24.1, 24.45, 24.95, 25.4, 25.8];
  const sink = ease((t - M.destroi) / 1.4);
  return (<Sc a={a} b={26.7} zoom={0.08} ov={<Cartela at={M.junho} to={26.3} date="11 DE JUNHO DE 1865" sub="BATALHA NAVAL DE RIACHUELO" />}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="bat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#2a2430" /><stop offset=".6" stopColor="#8a5b4a" /><stop offset="1" stopColor="#d9954f" /></linearGradient></defs>
      <rect width="1080" height="1250" fill="url(#bat)" />
      <ellipse cx="300" cy="360" rx="420" ry="90" fill="#3b3438" opacity=".7" transform={`translate(${-drift} 0)`} /><ellipse cx="860" cy="260" rx="360" ry="70" fill="#4a4146" opacity=".6" transform={`translate(${drift * 0.6} 0)`} />
      <Hills y={1060} c="#2e2a2f" amp={50} seed={9} />
      <Water y={1090} h={900} c="#1e3a48" />
      {/* frota brasileira (esq) */}
      <Vapor x={250 + drift * 0.3} y={1190} s={0.95} pennant={P.olive} smoke />
      <Vapor x={520 + drift * 0.2} y={1330} s={1.05} pennant={P.olive} smoke />
      {/* frota paraguaia (dir) */}
      <Vapor x={860} y={1200 + 220 * sink} s={0.85} flip pennant={P.red} tilt={-14 * sink} />
      <Vapor x={1040} y={1340} s={0.9} flip pennant={P.red} />
      {shoot.map((s, i) => <Flash key={i} x={i % 2 ? 640 : 380} y={i % 2 ? 1120 : 1090} at={s} big={1} />)}
      {shoot.map((s, i) => <Flash key={"r" + i} x={i % 2 ? 760 : 900} y={i % 2 ? 1180 : 1230} at={s + 0.25} big={0.9} />)}
      {sink > 0 && <g opacity={0.8 * (1 - sink * 0.5)}><Puffs x={840} y={1190 + 220 * sink} n={9} sp={20} sz={40} c="#3a3a40" /></g>}
    </svg></Sc>);
};

// ------------------------------------------------------------ cena 5: Humaitá
const Humaita: React.FC = () => {
  const { t } = useT(); const a = 26.5, p = t - a;
  const chain = Array.from({ length: 22 }, (_, i) => i);
  return (<Sc a={a} b={32.5} zoom={0.08} ov={<><Cartela at={M.humaita - 0.5} to={32.1} date="25 DE JULHO DE 1868" sub="QUEDA DE HUMAITÁ" />
    {t > M.cerco - 0.2 && <div style={{ position: "absolute", left: 56, top: 336, font: "italic 400 38px PFI", color: P.cream, textShadow: "0 3px 10px rgba(0,0,0,.6)" }}>depois de um longo cerco</div>}</>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="hum" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#3a4a5e" /><stop offset=".7" stopColor="#b8a07a" /><stop offset="1" stopColor="#e3c98f" /></linearGradient></defs>
      <rect width="1080" height="1250" fill="url(#hum)" />
      <g transform={`translate(${-p * 6} 0)`}><ellipse cx="220" cy="300" rx="260" ry="56" fill="#fff" opacity=".35" /><ellipse cx="800" cy="220" rx="300" ry="50" fill="#fff" opacity=".28" /></g>
      <Hills y={1020} c="#6b6a5a" amp={60} seed={4} dx={-p * 4} />
      <Water y={1100} h={900} c="#27505e" />
      {/* margem direita e fortaleza */}
      <path d="M560 1090 L1200 1060 L1200 1330 L520 1330 Z" fill="#7a6a4e" />
      <g>{[0, 1, 2, 3, 4, 5, 6].map((i) => <rect key={i} x={620 + i * 62} y={940} width="38" height="52" fill="#9a8a68" />)}
        <rect x="610" y="990" width="450" height="130" fill="#a8977a" /><rect x="610" y="1118" width="450" height="14" fill="#6a5a42" />
        <rect x="700" y="830" width="120" height="170" fill="#b2a184" /><rect x="690" y="815" width="140" height="22" fill="#8b7a5c" />
        {[0, 1, 2].map((i) => <rect key={i} x={716 + i * 36} y={850} width="20" height="40" rx="10" fill="#3b3226" />)}
        {[0, 1, 2, 3].map((i) => <g key={i}><rect x={640 + i * 100} y={1030} width="46" height="34" rx="4" fill="#2e271e" /><rect x={560 + i * 100} y={1040} width={90} height={14} rx="7" fill="#2a2a30" /></g>)}
        <line x1="900" y1="830" x2="900" y2="760" stroke="#2a2018" strokeWidth="5" /><path d="M900 760 L960 778 L900 796 Z" fill={P.red} /></g>
      <Flash x={610} y={1048} at={M.humaita + 0.1} big={0.9} /><Flash x={710} y={1048} at={M.humaita + 1.0} big={0.9} /><Flash x={810} y={1048} at={M.cai + 0.4} big={0.9} />
      {/* corrente atravessando o rio */}
      <g>{chain.map((i) => { const u = i / 21, x = 40 + u * 540, y = 1180 + 46 * Math.sin(u * Math.PI); return <ellipse key={i} cx={x} cy={y} rx="14" ry="8" fill="none" stroke="#2b2b30" strokeWidth="5" transform={`rotate(${i % 2 ? 70 : 0} ${x} ${y})`} />; })}
        <rect x="22" y="1150" width="26" height="90" fill="#2a2018" /></g>
      {/* navios aliados chegando */}
      <Vapor x={-120 + 330 * ease((t - 27.6) / 3.0)} y={1380} s={0.9} pennant={P.olive} />
    </svg></Sc>);
};

// ------------------------------------------------------------ soldados e palmeiras
const Soldado: React.FC<{ x: number; y: number; s?: number; ph?: number; c?: string }> = ({ x, y, s = 1, ph = 0, c = "#15181f" }) => {
  const { t } = useT(); const bob = 4 * Math.sin(t * 7 + ph);
  return (<g transform={`translate(${x} ${y + bob}) scale(${s})`} fill={c}><circle cx="0" cy="-92" r="13" /><rect x="-4" y="-80" width="8" height="8" /><path d="M-15 -76 L15 -76 L18 -20 L-18 -20 Z" /><rect x="-16" y="-20" width="12" height="58" /><rect x="4" y="-20" width="12" height="58" />
    <rect x="-18" y="-108" width="36" height="10" rx="3" /><line x1="22" y1="-120" x2="22" y2="30" stroke={c} strokeWidth="5" /></g>);
};
const Palma: React.FC<{ x: number; y: number; s?: number }> = ({ x, y, s = 1 }) => {
  const { t } = useT();
  return (<g transform={`translate(${x} ${y}) scale(${s})`}><path d="M-6 0 Q-10 -90 0 -180 L8 -180 Q0 -90 6 0 Z" fill="#2a2018" />
    {Array.from({ length: 7 }, (_, i) => <path key={i} d={`M0 -180 Q${60 * Math.cos(i * 0.9)} ${-230 + 30 * Math.sin(t * 2 + i)} ${130 * Math.cos(i * 0.9 - 0.2)} ${-150 + 60 * Math.sin(i)}`} stroke="#1f3a2a" strokeWidth="12" fill="none" strokeLinecap="round" />)}</g>);
};

// ------------------------------------------------------------ cena 6: Assunção ocupada
const Assuncao: React.FC = () => {
  const { t } = useT(); const a = 32.3, p = t - a;
  return (<Sc a={a} b={36.7} zoom={0.07} ov={<Cartela at={M.jan - 0.2} to={36.3} date="1º DE JANEIRO DE 1869" sub="ASSUNÇÃO OCUPADA" />}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="asu" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#6d7fa0" /><stop offset=".8" stopColor="#f0cf9a" /><stop offset="1" stopColor="#f6dcaa" /></linearGradient></defs>
      <rect width="1080" height="1250" fill="url(#asu)" />
      <circle cx="260" cy="620" r="90" fill="#fff3cf" opacity=".9" />
      <Hills y={1000} c="#8b8a7c" amp={50} seed={6} dx={-p * 3} />
      {/* casario */}
      <g>{Array.from({ length: 9 }, (_, i) => { const x = -20 + i * 130, h = 120 + 50 * rnd(i + 2); return <g key={i}><rect x={x} y={1080 - h} width="116" height={h} fill={i % 2 ? "#d8b98a" : "#c9a171"} /><path d={`M${x - 8} ${1080 - h} L${x + 58} ${1080 - h - 42} L${x + 124} ${1080 - h} Z`} fill={P.terra} />
        {[0, 1].map((k) => <rect key={k} x={x + 20 + k * 48} y={1080 - h + 28} width="28" height="42" fill="#3a2a22" />)}</g>; })}
        <rect x="470" y="880" width="200" height="200" fill="#e6cfa0" /><path d="M450 880 L570 800 L690 880 Z" fill="#b5593a" /><circle cx="570" cy="780" r="42" fill="#e0b86a" /><rect x="566" y="700" width="8" height="46" fill="#3a2a22" /><rect x="552" y="716" width="36" height="8" fill="#3a2a22" /></g>
      <rect x="0" y="1080" width="1080" height="900" fill="#6f5a3e" /><rect x="0" y="1340" width="1080" height="600" fill="#5a4630" />
      <Puffs x={300} y={880} n={6} sp={20} sz={30} c="#4a4448" /><Puffs x={800} y={870} n={6} sp={20} sz={32} c="#4a4448" />
      <Palma x={90} y={1330} s={1.35} /><Palma x={990} y={1320} s={1.5} />
      {/* soldados em primeiro plano */}
      <g transform={`translate(${-60 + p * 130} 0)`}>{[0, 1, 2, 3, 4].map((i) => <Soldado key={i} x={i * 110} y={1480 + 8 * (i % 2)} s={1.4} ph={i} />)}</g>
    </svg></Sc>);
};

// ------------------------------------------------------------ cena 7: Cerro Corá
const Cerro: React.FC = () => {
  const { t } = useT(); const a = 36.5, p = t - a;
  return (<Sc a={a} b={45.4} zoom={0.1} ov={<>
    <Cartela at={M.marco - 0.5} to={44.6} date="1º DE MARÇO DE 1870" sub="CERRO CORÁ · FIM DA GUERRA" />
    {t > M.solano - 0.3 && <div style={{ position: "absolute", left: 56, top: 336, opacity: ease((t - M.solano + 0.3) / 0.5), padding: "12px 24px", background: "rgba(16,20,28,.82)", borderLeft: `6px solid ${P.terra}` }}>
      <div style={{ font: "400 34px DMS", color: P.cream }}>FRANCISCO SOLANO LÓPEZ</div><div style={{ font: "700 20px MB", color: P.sand, letterSpacing: 3, marginTop: 4 }}>PRESIDENTE DO PARAGUAI</div></div>}</>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="cc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#3a4468" /><stop offset=".45" stopColor="#c0707a" /><stop offset=".75" stopColor="#f3b46c" /><stop offset="1" stopColor="#f6d493" /></linearGradient></defs>
      <rect width="1080" height="1300" fill="url(#cc)" /><Star n={28} />
      <circle cx={540} cy={880 - 20 * clamp(p / 8)} r="130" fill="#ffe0a0" opacity=".9" />
      <Hills y={900} c="#6b5a6a" amp={110} seed={3} dx={-p * 5} /><Hills y={1000} c="#4d4560" amp={90} seed={8} dx={-p * 9} /><Hills y={1100} c="#2f2a40" amp={70} seed={12} dx={-p * 14} />
      <rect x="0" y="1180" width="1080" height="800" fill="#241f2e" />
      {/* acampamento */}
      {[170, 380, 640, 880].map((x, i) => <g key={i}><path d={`M${x - 90} 1240 L${x} ${1130 - 12 * (i % 2)} L${x + 90} 1240 Z`} fill={i % 2 ? "#5d4a3a" : "#74604a"} /><path d={`M${x - 14} 1240 L${x} 1190 L${x + 14} 1240 Z`} fill="#150f0b" /></g>)}
      <g><circle cx="520" cy="1260" r="26" fill="#ffb347" opacity={0.85 + 0.1 * Math.sin(t * 12)} /><circle cx="520" cy="1260" r="70" fill="#ffb347" opacity=".18" /><Puffs x={520} y={1240} n={6} sp={28} sz={22} c="#555058" /></g>
      <Palma x={70} y={1300} s={1.1} /><Palma x={1010} y={1290} s={1.25} />
      <g>{[0, 1, 2, 3].map((i) => <Soldado key={i} x={250 + i * 190 + 10 * Math.sin(p + i)} y={1500 + 10 * (i % 2)} s={1.5} ph={i * 1.7} c="#0f1118" />)}</g>
    </svg></Sc>);
};

// ------------------------------------------------------------ cena 8: números
const Contagem: React.FC<{ to: number; at: number; dur?: number; suf?: string }> = ({ to, at, dur = 1.4, suf = " mil" }) => {
  const { t } = useT(); const k = ease((t - at) / dur); if (t < at) return <span style={{ opacity: 0 }}>{to}{suf}</span>; return <>{Math.round(to * k)}{suf}</>;
};
const Numeros: React.FC = () => {
  const { t } = useT(); const a = 45.2, W = 3.2;
  const bB = ease((t - M.n150) / 1.2) * 150 * W, bN = ease((t - M.n50) / 1.0) * 50 * W, bP = ease((t - M.n300) / 1.6) * 300 * W;
  return (<Sc a={a} b={58.8} zoom={0.02} ov={null}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><rect width="1080" height="1920" fill="#14181f" />
      <g stroke="rgba(240,228,201,.06)" strokeWidth="2">{Array.from({ length: 14 }, (_, i) => <line key={i} x1="0" y1={i * 140} x2="1080" y2={i * 140} />)}</g></svg>
    <div style={{ position: "absolute", left: 60, right: 60, top: 190, font: "400 66px DMS", color: P.cream, letterSpacing: 1, opacity: ease((t - a - 0.3) / 0.5) }}>O CUSTO DA GUERRA</div>
    <div style={{ position: "absolute", left: 60, width: 960, top: 330, opacity: ease((t - M.brasilN) / 0.5) }}>
      <div style={{ font: "800 34px MS", color: P.olive, letterSpacing: 5 }}>BRASIL</div>
      <div style={{ font: "400 52px DMS", color: P.cream, marginTop: 6 }}>enviou cerca de <Contagem to={150} at={M.n150} /> homens</div>
      <div style={{ position: "relative", marginTop: 20, height: 70, background: "rgba(255,255,255,.06)", borderRadius: 8 }}>
        <div style={{ position: "absolute", left: 0, top: 0, height: 70, width: bB, background: P.olive, borderRadius: 8 }} />
        <div style={{ position: "absolute", left: 0, top: 0, height: 70, width: bN, background: P.red, borderRadius: 8 }} /></div>
      {t > M.n50 - 0.2 && <div style={{ font: "700 34px MB", color: "#ff8a7a", marginTop: 16, opacity: ease((t - M.n50) / 0.4) }}>cerca de <Contagem to={50} at={M.n50} /> não voltaram</div>}
    </div>
    <div style={{ position: "absolute", left: 60, width: 960, top: 820, opacity: ease((t - M.parN) / 0.5) }}>
      <div style={{ font: "800 34px MS", color: P.terra, letterSpacing: 5 }}>PARAGUAI</div>
      <div style={{ font: "400 52px DMS", color: P.cream, marginTop: 6 }}>até <Contagem to={300} at={M.n300} dur={1.8} /> mortos</div>
      <div style={{ position: "relative", marginTop: 20, height: 70, background: "rgba(255,255,255,.06)", borderRadius: 8 }}>
        <div style={{ position: "absolute", left: 0, top: 0, height: 70, width: bP, background: P.terra, borderRadius: 8 }} /></div>
      <div style={{ font: "italic 400 32px PFI", color: P.sand, marginTop: 16, opacity: ease((t - M.n300 - 0.6) / 0.5) }}>estimativa · combates, doenças e fome</div>
    </div>
    <div style={{ position: "absolute", left: 60, right: 60, top: 1210, font: "400 150px DMS", color: P.cream, textAlign: "center", opacity: ease((t - 55.0) / 0.8), letterSpacing: 4 }}>1864–1870</div>
    <div style={{ position: "absolute", left: 80, right: 80, top: 1420, textAlign: "center", font: "italic 400 28px PFI", color: "rgba(240,228,201,.7)", opacity: ease((t - 55.4) / 0.8) }}>Fonte: Wikipédia (Guerra do Paraguai). Os números são estimativas e variam entre historiadores.</div>
  </Sc>);
};

// ------------------------------------------------------------ legenda e montagem
const Legenda: React.FC = () => {
  const { t } = useT(); const c = (TM.caps as any[]).find((x) => t >= x.t - 0.02 && t < x.e + 0.18); if (!c) return null;
  const u = clamp((t - c.t) / 0.15);
  return (<div style={{ position: "absolute", left: 70, right: 70, bottom: 150, textAlign: "center", font: "400 56px PF", color: P.cream, textShadow: "0 4px 14px rgba(0,0,0,.85), 0 0 4px rgba(0,0,0,.9)", opacity: u, transform: `translateY(${(1 - u) * 14}px)`, lineHeight: 1.15 }}>{c.text}</div>);
};
export const GuerraParaguai: React.FC = () => {
  const { t } = useT();
  return (<AbsoluteFill style={{ background: "#0d1017" }}>
    <style>{FONT}</style>
    <Porto /><Mapa /><Riachuelo /><Humaita /><Assuncao /><Cerro /><Numeros />
    <Vig /><Grain />
    {t < 56.5 && <Legenda />}
  </AbsoluteFill>);
};
export const GuerraParaguaiCapa: React.FC = () => (
  <AbsoluteFill style={{ background: "#e9dcbc" }}>
    <style>{FONT}</style>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><rect width="1080" height="1920" fill="#e9dcbc" />
      <g stroke="rgba(120,95,55,.18)" strokeWidth="2">{Array.from({ length: 14 }, (_, i) => <line key={i} x1="0" y1={i * 140} x2="1080" y2={i * 140} />)}{Array.from({ length: 9 }, (_, i) => <line key={i} x1={i * 140} y1="0" x2={i * 140} y2="1920" />)}</g>
      <g transform="translate(54 285) scale(0.9)">{MAP.map((m: any) => <path key={m.name} d={m.d} fill={m.name === "Paraguay" ? P.terra : m.name === "Brazil" ? P.olive : m.name === "Argentina" ? P.slate : m.name === "Uruguay" ? P.ochre : "#d8c9a5"} stroke="#8a7650" strokeWidth="1.4" />)}</g>
      <rect x="0" y="0" width="1080" height="640" fill="#161b24" /><rect x="0" y="1560" width="1080" height="360" fill="#161b24" /><rect x="0" y="636" width="1080" height="5" fill="#d9a441" /><rect x="0" y="1559" width="1080" height="5" fill="#d9a441" />
      <text x="540" y="205" textAnchor="middle" fontFamily="MB" fontSize="34" fill={P.ochre} letterSpacing="10">1864 – 1870</text>
      <text x="540" y="360" textAnchor="middle" fontFamily="DMS" fontSize="150" fill={P.cream}>Guerra do</text>
      <text x="540" y="520" textAnchor="middle" fontFamily="DMS" fontSize="170" fill={P.cream}>Paraguai</text>
      <rect x="440" y="560" width="200" height="6" fill={P.ochre} />
      <text x="540" y="1690" textAnchor="middle" fontFamily="DMS" fontSize="62" fill={P.cream}>A maior guerra da</text>
      <text x="540" y="1770" textAnchor="middle" fontFamily="DMS" fontSize="62" fill={P.ochre}>América do Sul</text>
    </svg><Vig />
  </AbsoluteFill>
);
