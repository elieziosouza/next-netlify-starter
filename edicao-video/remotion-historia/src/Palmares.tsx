// Quilombo dos Palmares (22/11/2026): documentário animado 2D plano, vertical 1080x1920, 55 s. Tempos: ./pal.json (scripts/historia/pal_timings.py).
// Novidade desta vez: linha do tempo animada no pé da tela (1590 a 2024).
import React from "react";
import { AbsoluteFill } from "remotion";
import { feature } from "topojson-client";
import { geoMercator, geoPath } from "d3-geo";
import topo from "world-atlas/countries-50m.json";
import TM from "./pal.json";
import { P, clamp, ease, rnd, useT, FONT, Grain, Vig, Sc, Puffs, Star, Hills, Cartela, Flash } from "./GuerraParaguai";

const M = TM.M as Record<string, number>;
const SAN = ["Brazil", "Argentina", "Paraguay", "Uruguay", "Bolivia", "Peru", "Colombia", "Venezuela", "Guyana", "Suriname"];
const fc: any = feature(topo as any, (topo as any).objects.countries);
const BR = fc.features.find((f: any) => f.properties.name === "Brazil");
const projB = geoMercator().fitExtent([[70, 340], [1010, 1470]], BR);
const gB = geoPath(projB);
const NEIGH = fc.features.filter((f: any) => SAN.includes(f.properties.name)).map((f: any) => ({ n: f.properties.name as string, d: gB(f) as string })).filter((x: any) => x.d);
const PAL = projB([-36.02, -9.16]) as [number, number];

// ------------------------------------------------------------ peças
const Arvore: React.FC<{ x: number; y: number; s?: number; c: string }> = ({ x, y, s = 1, c }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`} fill={c}><rect x="-8" y="-20" width="16" height="74" /><circle cx="0" cy="-64" r="54" /><circle cx="-40" cy="-32" r="40" /><circle cx="40" cy="-34" r="42" /></g>);
const Fig: React.FC<{ x: number; y: number; s?: number; ph?: number; c?: string; bundle?: boolean; spear?: boolean; walk?: boolean }> = ({ x, y, s = 1, ph = 0, c = "#12151c", bundle, spear, walk = true }) => {
  const { t } = useT(); const bob = walk ? 4 * Math.sin(t * 6 + ph) : 0, sw = walk ? 7 * Math.sin(t * 6 + ph) : 0;
  return (<g transform={`translate(${x} ${y + bob}) scale(${s})`} fill={c}><circle cx="0" cy="-92" r="13" /><path d="M-15 -76 L15 -76 L18 -22 L-18 -22 Z" />
    <rect x={-16 + sw} y="-22" width="12" height="58" /><rect x={4 - sw} y="-22" width="12" height="58" />
    {bundle && <circle cx="-6" cy="-112" r="16" />}{spear && <g><line x1="26" y1="-150" x2="26" y2="36" stroke={c} strokeWidth="5" /><path d="M26 -168 L36 -146 L16 -146 Z" /></g>}</g>);
};
const Cabana: React.FC<{ x: number; y: number; s?: number; fire?: boolean; wall?: string; roof?: string }> = ({ x, y, s = 1, fire, wall = "#c9a171", roof = "#8a6a38" }) => {
  const { t } = useT();
  return (<g transform={`translate(${x} ${y}) scale(${s})`}><rect x="-60" y="-70" width="120" height="70" fill={wall} /><path d="M-82 -66 L0 -150 L82 -66 Z" fill={roof} />
    {[-70, -40, -10, 20, 50].map((lx) => <line key={lx} x1={lx} y1={-66 + Math.abs(lx) * 0.1} x2={lx * 0.45} y2={-130 + Math.abs(lx) * 0.2} stroke="rgba(40,25,10,.35)" strokeWidth="3" />)}
    <path d="M-16 0 L-16 -44 Q0 -58 16 -44 L16 0 Z" fill="#2a1e14" />
    {fire && <g>{[-50, -20, 20, 50].map((fx, i) => <path key={i} d={`M${fx - 18} -70 Q${fx - 6} ${-120 - 16 * Math.sin(t * 9 + i)} ${fx} ${-150 - 24 * Math.sin(t * 7 + i * 2)} Q${fx + 8} ${-110} ${fx + 18} -70 Z`} fill={i % 2 ? "#ffb23c" : "#ff6a2a"} opacity=".92" />)}</g>}</g>);
};
const Cerca: React.FC<{ x: number; y: number; w: number; h?: number; c?: string }> = ({ x, y, w, h = 130, c = "#6b4a28" }) => (
  <g>{Array.from({ length: Math.floor(w / 26) }, (_, i) => <path key={i} d={`M${x + i * 26} ${y} L${x + i * 26} ${y - h} L${x + i * 26 + 11} ${y - h - 24} L${x + i * 26 + 22} ${y - h} L${x + i * 26 + 22} ${y} Z`} fill={c} stroke="#3d2a14" strokeWidth="2" />)}
    <rect x={x} y={y - h * 0.6} width={w} height="10" fill="#3d2a14" opacity=".7" /></g>);
const Bruma: React.FC<{ y: number; o?: number }> = ({ y, o = 0.25 }) => { const { t } = useT(); return <ellipse cx={540 + 50 * Math.sin(t * 0.3 + y)} cy={y} rx="640" ry="60" fill="#fff" opacity={o} />; };

// ------------------------------------------------------------ cena A: Serra da Barriga ao amanhecer
const CenaA: React.FC = () => {
  const { t } = useT();
  return (<Sc a={0} b={7.0} zoom={0.08} ov={<Cartela at={0.3} to={6.5} date="FINAL DO SÉCULO XVI" sub="SERRA DA BARRIGA · PERNAMBUCO" />}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="pa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#2b3558" /><stop offset=".45" stopColor="#c4687a" /><stop offset=".75" stopColor="#f0a468" /><stop offset="1" stopColor="#f6cf8f" /></linearGradient></defs>
      <rect width="1080" height="1500" fill="url(#pa)" /><Star n={26} /><circle cx="760" cy="880" r="120" fill="#ffe3a8" opacity=".92" />
      <g transform={`translate(${-t * 3} 0)`}><Hills y={900} c="#7a5a6c" amp={110} seed={3} /></g><Bruma y={960} o={0.22} />
      <Hills y={1000} c="#4f4259" amp={100} seed={7} dx={-t * 6} /><Bruma y={1050} o={0.18} />
      {/* engenho ao fundo */}
      <g transform="translate(150 1070)"><rect x="-70" y="-60" width="140" height="60" fill="#2a2030" /><path d="M-86 -58 L0 -112 L86 -58 Z" fill="#1c1624" /><rect x="40" y="-150" width="22" height="96" fill="#1c1624" /><Puffs x={51} y={-150} n={6} sp={20} sz={22} c="#5a5260" /></g>
      <Hills y={1130} c="#2c2a3c" amp={80} seed={11} dx={-t * 10} />
      {[60, 170, 290, 420, 560, 690, 830, 960, 1060].map((x, i) => <Arvore key={i} x={x + 12 * Math.sin(t * 0.4 + i)} y={1160 + 20 * (i % 3)} s={1.2 + 0.4 * rnd(i)} c={i % 2 ? "#1b2a2c" : "#223630"} />)}
      <rect x="0" y="1190" width="1080" height="800" fill="#3a2f2c" />
      {[40, 1040].map((x, i) => <Arvore key={"f" + i} x={x} y={1400} s={2.3} c="#0f161a" />)}
      {/* caminho e pessoas subindo a serra */}
      <path d="M-40 1560 Q380 1480 1100 1250" stroke="#d9a272" strokeWidth="64" fill="none" strokeLinecap="round" opacity=".55" />
      {Array.from({ length: 7 }, (_, i) => { const u = ((t * 0.075 + i / 7) % 1), x = -30 + 1160 * u, y = 1555 - 300 * Math.pow(u, 0.9) + 60 * Math.sin(u * 3.14 * 1) * 0; return <Fig key={i} x={x} y={y - 6 * Math.sin(u * 6)} s={0.95 - 0.3 * u} ph={i * 1.3} bundle={i % 2 === 0} />; })}
    </svg></Sc>);
};

// ------------------------------------------------------------ cena B: mapa do Brasil
const CenaB: React.FC = () => {
  const { t } = useT(); const a = 6.6, z = 1 + 1.25 * ease((t - 6.8) / 1.8), tx = 540 - PAL[0] * z, ty = 820 - PAL[1] * z;
  return (<Sc a={a} b={9.6} zoom={0} ov={<>
    <Cartela at={M.quilombo - 0.3} to={9.2} date="QUILOMBO DOS PALMARES" fs={46} />
    <div style={{ position: "absolute", left: 60, top: 212, font: "italic 400 26px PFI", color: "rgba(40,30,18,.8)" }}>mapa com as fronteiras de hoje</div></>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><rect width="1080" height="1920" fill="#e9dcbc" />
      <g stroke="rgba(120,95,55,.18)" strokeWidth="2">{Array.from({ length: 14 }, (_, i) => <line key={i} x1="0" y1={i * 140} x2="1080" y2={i * 140} />)}{Array.from({ length: 9 }, (_, i) => <line key={i} x1={i * 140} y1="0" x2={i * 140} y2="1920" />)}</g>
      <g transform={`translate(${tx} ${ty}) scale(${z})`}>
        {NEIGH.map((m: any) => <path key={m.n} d={m.d} fill={m.n === "Brazil" ? "#7b9a62" : "#d8c9a5"} stroke="#8a7650" strokeWidth={1.4 / z} strokeLinejoin="round" />)}
        <circle cx={PAL[0]} cy={PAL[1]} r={(26 + 12 * Math.sin(t * 6)) / z * 1.2} fill="none" stroke={P.red} strokeWidth={5 / z} opacity={ease((t - 7.6) / 0.4)} />
        <circle cx={PAL[0]} cy={PAL[1]} r={11 / z * 1.2} fill={P.red} opacity={ease((t - 7.4) / 0.3)} />
        {t > 8.0 && <text x={PAL[0] + 32 / z} y={PAL[1] - 24 / z} fontFamily="MS" fontSize={30 / z} fill={P.ink} stroke="#e9dcbc" strokeWidth={5 / z} paintOrder="stroke" letterSpacing="2">PALMARES</text>}
        {t > 8.2 && <text x={PAL[0] + 32 / z} y={PAL[1] + 14 / z} fontFamily="PFI" fontSize={24 / z} fill="#3a2a14" stroke="#e9dcbc" strokeWidth={4 / z} paintOrder="stroke">hoje União dos Palmares (AL)</text>}
      </g></svg></Sc>);
};

// ------------------------------------------------------------ cena C: o mocambo no auge
const Pill: React.FC<{ at: number; y: number; children: React.ReactNode }> = ({ at, y, children }) => {
  const { t } = useT(); const k = ease((t - at) / 0.4); if (k <= 0) return null;
  return <div style={{ position: "absolute", left: 56, top: y, opacity: k, transform: `translateX(${(1 - k) * -80}px)`, padding: "10px 22px", borderRadius: 40, background: "rgba(240,228,201,.94)", color: P.ink, font: "700 26px MB", letterSpacing: 2 }}>{children}</div>;
};
const CenaC: React.FC = () => {
  const { t } = useT(); const a = 9.3, p = t - a;
  const num = Math.round(20 * ease((t - M.n11) / 1.8));
  return (<Sc a={a} b={20.6} zoom={0.07} ov={<>
    <Cartela at={M.auge - 0.2} to={20.2} date="PALMARES NO AUGE" sub="ESTIMATIVA · 11 A 20 MIL PESSOAS" fs={52} />
    {t > M.n11 - 0.2 && <div style={{ position: "absolute", right: 56, top: 140, textAlign: "right", opacity: ease((t - M.n11 + 0.2) / 0.5), font: "400 120px DMS", color: P.cream, textShadow: "0 6px 20px rgba(0,0,0,.6)" }}>{num}<span style={{ fontSize: 56 }}> mil</span></div>}
    <Pill at={M.afric - 0.1} y={330}>AFRICANOS</Pill><Pill at={M.indig - 0.1} y={400}>INDÍGENAS</Pill><Pill at={M.colonos - 0.1} y={470}>COLONOS MARGINALIZADOS</Pill>
    {t > M.maior - 0.1 && <div style={{ position: "absolute", left: 0, right: 0, top: 1240, textAlign: "center", opacity: ease((t - M.maior) / 0.5) }}>
      <span style={{ display: "inline-block", padding: "14px 36px", background: "rgba(16,20,28,.9)", borderTop: `4px solid ${P.ochre}`, borderBottom: `4px solid ${P.ochre}`, font: "400 52px DMS", color: P.cream, letterSpacing: 2 }}>O MAIOR QUILOMBO DO BRASIL</span></div>}</>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="pc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#6f9bbd" /><stop offset=".7" stopColor="#f0d9a8" /><stop offset="1" stopColor="#f6e4b8" /></linearGradient></defs>
      <rect width="1080" height="1300" fill="url(#pc)" />
      <g transform={`translate(${-p * 5} 0)`}><ellipse cx="260" cy="300" rx="280" ry="46" fill="#fff" opacity=".5" /><ellipse cx="860" cy="220" rx="300" ry="40" fill="#fff" opacity=".4" /></g>
      <Hills y={900} c="#6c8f66" amp={120} seed={2} dx={-p * 3} /><Hills y={980} c="#58805a" amp={90} seed={9} dx={-p * 6} />
      {[100, 330, 700, 960].map((x, i) => <Arvore key={i} x={x} y={1010} s={1.1 + 0.3 * rnd(i)} c="#3b6a48" />)}
      <rect x="0" y="1000" width="1080" height="900" fill="#8a6a3e" />
      {/* roças em fileiras */}
      <g stroke="#4f7a3a" strokeWidth="9" strokeLinecap="round">{Array.from({ length: 9 }, (_, r) => <line key={r} x1={-200 + r * 190} y1="1760" x2={400 + r * 40} y2="1180" />)}</g>
      <rect x="0" y="1150" width="1080" height="14" fill="#5b3f22" opacity=".5" />
      <Cerca x={-10} y={1130} w={1100} h={120} />
      {/* cabanas */}
      <Cabana x={170} y={1190} s={1.15} /><Cabana x={420} y={1170} s={0.95} wall="#d6b583" /><Cabana x={650} y={1195} s={1.2} wall="#bf9565" /><Cabana x={900} y={1170} s={1.0} wall="#d6b583" />
      <Puffs x={210} y={1050} n={5} sp={18} sz={22} c="#9a9aa0" /><Puffs x={690} y={1040} n={5} sp={18} sz={24} c="#9a9aa0" />
      <rect x="0" y="1210" width="1080" height="800" fill="#7a5a32" />
      {[0, 1, 2, 3, 4, 5].map((i) => <Fig key={i} x={((p * 40 + i * 190) % 1300) - 100} y={1470 + 26 * (i % 3)} s={1.05} ph={i * 1.4} bundle={i % 3 === 0} c="#241a12" />)}
    </svg></Sc>);
};

// ------------------------------------------------------------ cena D: defesa, 6 expedições
const CenaD: React.FC = () => {
  const { t } = useT(); const a = 20.4, p = t - a;
  const wave = (i: number) => { const u = (p * 0.55 + i * 0.5) % 3; return u < 1.4 ? 1100 - 480 * ease(u / 1.4) : 620 + 480 * ease((u - 1.4) / 1.4) * (u < 2.8 ? 1 : 0) * 0.0 + 480 * ease((u - 1.4) / 1.6) * 0.9; };
  return (<Sc a={a} b={31.9} zoom={0.07} ov={<>
    <Cartela at={M.a1680 - 0.3} to={31.4} date="1680 A 1686" sub="6 EXPEDIÇÕES · TODAS FRACASSARAM" fs={56} />
    <div style={{ position: "absolute", right: 56, top: 140, display: "flex", gap: 10 }}>{[0, 1, 2, 3, 4, 5].map((i) => { const on = t >= M.seis + i * 0.35, x = t >= M.fracas + i * 0.12;
      return <div key={i} style={{ width: 54, height: 54, borderRadius: "50%", border: `5px solid ${on ? P.cream : "rgba(240,228,201,.25)"}`, background: x ? P.red : "rgba(0,0,0,.3)", display: "grid", placeItems: "center", color: P.cream, font: "800 30px MS", transition: "none" }}>{x ? "✕" : on ? i + 1 : ""}</div>; })}</div>
    {t > M.zumbi1 - 0.2 && <div style={{ position: "absolute", left: 56, top: 340, opacity: ease((t - M.zumbi1 + 0.2) / 0.5), padding: "12px 24px", background: "rgba(16,20,28,.86)", borderLeft: `6px solid ${P.terra}` }}>
      <div style={{ font: "400 40px DMS", color: P.cream }}>ZUMBI</div><div style={{ font: "700 20px MB", color: P.sand, letterSpacing: 3, marginTop: 4 }}>PRINCIPAL LIDERANÇA DA RESISTÊNCIA</div></div>}</>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="pd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#4a5c7a" /><stop offset=".6" stopColor="#c99a78" /><stop offset="1" stopColor="#e6bf8a" /></linearGradient></defs>
      <rect width="1080" height="1300" fill="url(#pd)" />
      <Hills y={920} c="#5b6a63" amp={100} seed={4} dx={-p * 4} /><Hills y={1010} c="#3f5547" amp={80} seed={13} dx={-p * 8} />
      <rect x="0" y="1050" width="1080" height="900" fill="#7a5a34" />
      {/* inimigos avançando e recuando (silhuetas) */}
      {[0, 1, 2, 3, 4].map((i) => <Fig key={i} x={wave(i) + i * 40} y={1330 + 26 * (i % 3)} s={1.05} ph={i * 1.1} spear c="#1c1822" walk />)}
      {/* armadilha: fosso com estacas */}
      <rect x="470" y="1420" width="200" height="40" fill="#1e140c" />{Array.from({ length: 8 }, (_, i) => <path key={i} d={`M${482 + i * 24} 1420 L${494 + i * 24} 1388 L${506 + i * 24} 1420 Z`} fill="#8a6a40" />)}
      {/* cerca em primeiro plano */}
      <Cerca x={-20} y={1560} w={520} h={260} c="#6b4a28" /><Cerca x={560} y={1560} w={560} h={260} c="#6b4a28" />
      {/* Zumbi (silhueta no alto) */}
      {t > M.zumbi1 - 0.3 && <g opacity={ease((t - M.zumbi1 + 0.3) / 0.6)}><Fig x={150} y={1040} s={1.4} spear walk={false} c="#0f1217" /></g>}
      <Flash x={900} y={1400} at={22.6} big={0.6} /><Flash x={760} y={1380} at={24.9} big={0.6} />
    </svg></Sc>);
};

// ------------------------------------------------------------ cena E: 1694, grande ofensiva
const CenaE: React.FC = () => {
  const { t } = useT(); const a = 31.7, p = t - a;
  const shots = [32.6, 33.3, 34.0, 34.8, 35.5, 36.2];
  return (<Sc a={a} b={37.7} zoom={0.09} ov={<Cartela at={M.a1694 - 0.3} to={37.2} date="1694" sub="GRANDE OFENSIVA · COM ARTILHARIA" fs={64} />}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="pe" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#1a1626" /><stop offset=".55" stopColor="#7c3a3a" /><stop offset="1" stopColor="#e8803c" /></linearGradient></defs>
      <rect width="1080" height="1400" fill="url(#pe)" />
      <circle cx="540" cy="1050" r="520" fill="#ff9a3c" opacity=".16" />
      <Hills y={980} c="#2a1c26" amp={90} seed={5} dx={-p * 4} />
      <rect x="0" y="1060" width="1080" height="900" fill="#2a1d16" />
      <Puffs x={150} y={1040} n={9} sp={24} sz={40} c="#26222a" /><Puffs x={560} y={1060} n={9} sp={24} sz={44} c="#26222a" /><Puffs x={900} y={1040} n={9} sp={24} sz={40} c="#26222a" />
      <Cabana x={170} y={1260} s={1.3} fire wall="#7a5a3a" roof="#3a2a1a" /><Cabana x={470} y={1240} s={1.1} fire wall="#7a5a3a" roof="#3a2a1a" /><Cabana x={760} y={1270} s={1.35} fire wall="#7a5a3a" roof="#3a2a1a" />
      {[0, 1, 2, 3].map((i) => <Fig key={i} x={940 - ((p * 90 + i * 90) % 1100) * 0.0 + 0 - i * 70 - 40 * Math.sin(p * 2 + i)} y={1560 + 22 * (i % 2)} s={1.25} ph={i * 1.2} spear c="#0e0c10" />)}
      <g>{/* canhão na direita */}<rect x="900" y="1480" width="190" height="34" rx="12" fill="#14121a" transform="rotate(-8 900 1490)" /><circle cx="990" cy="1530" r="42" fill="#14121a" /><circle cx="990" cy="1530" r="20" fill="#2a2630" /></g>
      {shots.map((s, i) => <Flash key={i} x={880} y={1470} at={s} big={1.1} />)}{shots.map((s, i) => <Flash key={"b" + i} x={170 + (i % 3) * 300} y={1240} at={s + 0.4} big={0.8} />)}
    </svg></Sc>);
};

// ------------------------------------------------------------ cena F: 20 de novembro de 1695
const CenaF: React.FC = () => {
  const { t } = useT(); const a = 37.5, p = t - a, wind = 5 * Math.sin(t * 3);
  return (<Sc a={a} b={43.8} zoom={0.1} ov={<Cartela at={M.zumbi2 - 0.2} to={43.3} date="20 DE NOVEMBRO DE 1695" sub="MORTE DE ZUMBI" fs={54} />}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
      <linearGradient id="pf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#141b36" /><stop offset=".5" stopColor="#4a4a7a" /><stop offset=".8" stopColor="#d98b78" /><stop offset="1" stopColor="#f3c58a" /></linearGradient></defs>
      <rect width="1080" height="1500" fill="url(#pf)" /><Star n={60} />
      <circle cx="540" cy={1000 - 40 * clamp(p / 6)} r="150" fill="#ffd9a0" opacity=".85" />
      <Hills y={960} c="#5a4c6a" amp={120} seed={8} dx={-p * 4} /><Bruma y={1040} o={0.2} /><Hills y={1060} c="#3a3250" amp={90} seed={14} dx={-p * 8} />
      <rect x="0" y="1180" width="1080" height="800" fill="#1d1a2a" />
      <path d="M200 1240 Q540 1130 880 1240 L880 1400 L200 1400 Z" fill="#12121c" />
      <g transform={`translate(540 1190)`}><Fig x={0} y={0} s={2.1} spear walk={false} c="#07080d" /><path d={`M-22 -190 Q${-60 + wind} -170 ${-90 + wind * 2} -140`} stroke="#07080d" strokeWidth="9" fill="none" strokeLinecap="round" /></g>
      {[60, 210, 880, 1010].map((x, i) => <Arvore key={i} x={x} y={1260 + 20 * (i % 2)} s={1.9} c="#0b0d14" />)}
    </svg></Sc>);
};

// ------------------------------------------------------------ cena G: o que ficou
const CenaG: React.FC = () => {
  const { t } = useT(); const a = 43.6;
  const card = (at: number, y: number, ano: string, txt: string, c: string) => (
    <div style={{ position: "absolute", left: 60, right: 60, top: y, opacity: ease((t - at) / 0.5), transform: `translateX(${(1 - ease((t - at) / 0.5)) * -120}px)`, display: "flex", gap: 28, alignItems: "center" }}>
      <div style={{ font: "400 130px DMS", color: c, minWidth: 340 }}>{ano}</div><div style={{ font: "400 44px PF", color: P.cream, lineHeight: 1.15 }}>{txt}</div></div>);
  const cal = ease((t - M.a2024 + 1.2) / 0.6);
  return (<Sc a={a} b={55.2} zoom={0.02}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><rect width="1080" height="1920" fill="#14181f" /><g stroke="rgba(240,228,201,.06)" strokeWidth="2">{Array.from({ length: 14 }, (_, i) => <line key={i} x1="0" y1={i * 140} x2="1080" y2={i * 140} />)}</g></svg>
    {card(M.a1995 - 0.2, 220, "1995", "Zumbi é reconhecido como herói nacional", P.ochre)}
    {card(M.a2024 - 0.2, 470, "2024", "O 20 de novembro vira feriado em todo o país", P.terra)}
    {t > M.feriado - 0.8 && <div style={{ position: "absolute", left: 270, top: 760, width: 540, height: 470, opacity: cal, transform: `scale(${0.8 + 0.2 * cal}) rotate(-2deg)`, background: "#f3ead3", borderRadius: 26, boxShadow: "0 20px 50px rgba(0,0,0,.55)", overflow: "hidden" }}>
      <div style={{ height: 120, background: P.red, color: "#fff", font: "800 46px MS", letterSpacing: 8, display: "grid", placeItems: "center" }}>NOVEMBRO</div>
      <div style={{ font: "400 270px DMS", color: P.ink, textAlign: "center", lineHeight: 1.05 }}>20</div></div>}
    {t > M.consc - 0.1 && <div style={{ position: "absolute", left: 0, right: 0, top: 1300, textAlign: "center", opacity: ease((t - M.consc) / 0.5) }}>
      <span style={{ display: "inline-block", padding: "16px 40px", background: P.ochre, color: P.ink, font: "400 56px DMS", letterSpacing: 2 }}>DIA DA CONSCIÊNCIA NEGRA</span></div>}
    <div style={{ position: "absolute", left: 80, right: 80, top: 1450, textAlign: "center", font: "italic 400 27px PFI", color: "rgba(240,228,201,.65)", opacity: ease((t - 50.5) / 0.8) }}>Fonte: Wikipédia (Quilombo dos Palmares e Zumbi dos Palmares). Dados de população são estimativas.</div>
  </Sc>);
};

// ------------------------------------------------------------ linha do tempo, legenda, montagem
const MARCOS: { y: string; t: number }[] = [{ y: "1590", t: 0 }, { y: "1680", t: 20.5 }, { y: "1694", t: 31.8 }, { y: "1695", t: 37.55 }, { y: "1995", t: 43.64 }, { y: "2024", t: 48.1 }];
const Linha: React.FC = () => {
  const { t } = useT(); if (t < 1.2 || t > 54) return null;
  const k = clamp((t - 1.2) / 0.5) * clamp((54 - t) / 0.4), X0 = 110, X1 = 970, step = (X1 - X0) / (MARCOS.length - 1);
  let pos = 0; for (let i = 0; i < MARCOS.length - 1; i++) { if (t >= MARCOS[i].t) pos = i + clamp((t - MARCOS[i].t) / (MARCOS[i + 1].t - MARCOS[i].t)); }
  if (t >= MARCOS[MARCOS.length - 1].t) pos = MARCOS.length - 1;
  const mx = X0 + pos * step, cur = MARCOS[Math.round(pos)].y;
  return (<div style={{ position: "absolute", left: 0, top: 1540, width: 1080, height: 110, opacity: k }}>
    <svg width="1080" height="110"><line x1={X0} y1="40" x2={X1} y2="40" stroke="rgba(240,228,201,.35)" strokeWidth="4" /><line x1={X0} y1="40" x2={mx} y2="40" stroke={P.ochre} strokeWidth="6" />
      {MARCOS.map((m, i) => <g key={m.y}><circle cx={X0 + i * step} cy="40" r={pos >= i ? 11 : 8} fill={pos >= i ? P.ochre : "#2a2f3a"} stroke="rgba(240,228,201,.7)" strokeWidth="3" /><text x={X0 + i * step} y="86" textAnchor="middle" fontFamily="MB" fontSize="24" fill={cur === m.y ? P.cream : "rgba(240,228,201,.6)"}>{m.y}</text></g>)}
      <circle cx={mx} cy="40" r="16" fill={P.terra} stroke={P.cream} strokeWidth="4" /></svg></div>);
};
const Legenda: React.FC = () => {
  const { t } = useT(); const c = (TM.caps as any[]).find((x) => t >= x.t - 0.02 && t < x.e + 0.18); if (!c) return null;
  const u = clamp((t - c.t) / 0.15);
  return (<div style={{ position: "absolute", left: 70, right: 70, bottom: 150, textAlign: "center", font: "400 56px PF", color: P.cream, textShadow: "0 4px 14px rgba(0,0,0,.85), 0 0 4px rgba(0,0,0,.9)", opacity: u, transform: `translateY(${(1 - u) * 14}px)`, lineHeight: 1.15 }}>{c.text}</div>);
};
export const Palmares: React.FC = () => {
  const { t } = useT();
  return (<AbsoluteFill style={{ background: "#0d1017" }}><style>{FONT}</style>
    <CenaA /><CenaB /><CenaC /><CenaD /><CenaE /><CenaF /><CenaG /><Vig /><Grain /><Linha />{t < 54.2 && <Legenda />}
  </AbsoluteFill>);
};
export const PalmaresCapa: React.FC = () => (
  <AbsoluteFill style={{ background: "#161b24" }}><style>{FONT}</style>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs><linearGradient id="cp" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#2b3558" /><stop offset=".5" stopColor="#c4687a" /><stop offset=".8" stopColor="#f0a468" /><stop offset="1" stopColor="#f6cf8f" /></linearGradient></defs>
      <rect width="1080" height="1920" fill="#161b24" /><rect y="640" width="1080" height="920" fill="url(#cp)" /><circle cx="760" cy="1180" r="150" fill="#ffe3a8" opacity=".95" />
      <Hills y={1190} c="#7a5a6c" amp={120} seed={3} /><Hills y={1290} c="#4f4259" amp={100} seed={7} /><Hills y={1390} c="#2c2a3c" amp={80} seed={11} />
      {[80, 260, 430, 620, 820, 990].map((x, i) => <Arvore key={i} x={x} y={1470 + 20 * (i % 2)} s={1.6 + 0.4 * rnd(i)} c="#10171b" />)}
      <g transform="translate(340 1475)"><Fig x={0} y={0} s={2.4} spear walk={false} c="#07080d" /></g>
      <rect y="1556" width="1080" height="364" fill="#161b24" /><rect y="636" width="1080" height="6" fill="#d9a441" /><rect y="1552" width="1080" height="6" fill="#d9a441" />
      <text x="540" y="195" textAnchor="middle" fontFamily="MB" fontSize="27" fill="#d9a441" letterSpacing="7">20 DE NOVEMBRO · CONSCIÊNCIA NEGRA</text>
      <text x="540" y="360" textAnchor="middle" fontFamily="DMS" fontSize="150" fill="#f0e4c9">Quilombo</text>
      <text x="540" y="520" textAnchor="middle" fontFamily="DMS" fontSize="150" fill="#f0e4c9">dos Palmares</text><rect x="440" y="570" width="200" height="6" fill="#d9a441" />
      <text x="540" y="1690" textAnchor="middle" fontFamily="DMS" fontSize="60" fill="#f0e4c9">O maior quilombo da</text><text x="540" y="1768" textAnchor="middle" fontFamily="DMS" fontSize="60" fill="#d9a441">história do Brasil</text></svg><Vig />
  </AbsoluteFill>
);
