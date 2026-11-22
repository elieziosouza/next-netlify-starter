// Lampião: herói ou bandido? (22/11/2026): Short vertical 1080x1920, ~58 s, para Instagram e TikTok. Tempos: ./lampcur.json (scripts/historia/lampcur_timings.py).
// Novidade: áreas seguras de Instagram/TikTok (nada importante nos ~450 px de baixo nem nos ~130 px da direita) e chamada para o vídeo completo.
import React from "react";
import { AbsoluteFill } from "remotion";
import { geoMercator, geoPath } from "d3-geo";
import TM from "./lampcur.json";
import { P, clamp, ease, rnd, useT, FONT, Grain, Vig, Sc, Star, Hills, Cartela, Flash } from "./GuerraParaguai";
import { Cang, Mandacaru, Arbusto, Cavalo, Casa, Barraca, Cerca, sunset, NE, FS, SEVEN } from "./Lampiao";

const M = TM.M as Record<string, number>;
const S = TM.spans as number[][];

// ------------------------------------------------------------ mapa vertical
const projV = geoMercator().fitExtent([[120, 700], [1000, 1400]], { type: "FeatureCollection", features: FS.filter((f: any) => NE.includes(f.properties.name)) } as any);
const gV = geoPath(projV);
const STV = FS.map((f: any) => ({ n: f.properties.name as string, d: gV(f) as string })).filter((x: any) => x.d);
const ptV = (lon: number, lat: number) => projV([lon, lat]) as [number, number];
const SERRA = ptV(-38.29, -7.99);

const MapV: React.FC<{ fill?: Record<string, string>; zoomTo?: [number, number]; z?: number; at?: number; children?: (z: number) => React.ReactNode }> = ({ fill = {}, zoomTo, z = 1.8, at = 0, children }) => {
  const { t } = useT(); const k = zoomTo ? ease((t - at) / 1.8) : 0, zz = 1 + (z - 1) * k, tx = zoomTo ? 540 - zoomTo[0] * zz : 0, ty = zoomTo ? 960 - zoomTo[1] * zz : 0;
  return (<svg width="1080" height="1920" viewBox="0 0 1080 1920"><rect width="1080" height="1920" fill="#e9dcbc" />
    <g stroke="rgba(120,95,55,.18)" strokeWidth="2">{Array.from({ length: 14 }, (_, i) => <line key={i} x1="0" y1={i * 140} x2="1080" y2={i * 140} />)}{Array.from({ length: 9 }, (_, i) => <line key={i} x1={i * 140} y1="0" x2={i * 140} y2="1920" />)}</g>
    <g transform={zoomTo ? `translate(${tx} ${ty}) scale(${zz})` : undefined}>
      {STV.map((s: any) => <path key={s.n} d={s.d} fill={fill[s.n] || (NE.includes(s.n) ? "#d8c9a5" : "#e0d3b0")} stroke="#8a7650" strokeWidth={1.5 / zz} strokeLinejoin="round" />)}
      {children && children(zz)}</g></svg>);
};
const Rain: React.FC<{ o?: number }> = ({ o = 0.35 }) => {
  const { t } = useT();
  return (<g stroke="#cfe3f5" strokeWidth="2" opacity={o}>{Array.from({ length: 150 }, (_, i) => { const x = rnd(i) * 1180 - 50, y = ((rnd(i + 3) * 1920 + t * 900 * (0.8 + 0.4 * rnd(i + 8))) % 2000) - 40; return <line key={i} x1={x} y1={y} x2={x - 14} y2={y + 36} />; })}</g>);
};
const Pill: React.FC<{ at: number; to?: number; y: number; children: React.ReactNode }> = ({ at, to = 999, y, children }) => {
  const { t } = useT(); const k = ease((t - at) / 0.4) * clamp((to - t) / 0.35); if (k <= 0) return null;
  return <div style={{ position: "absolute", left: 56, top: y, opacity: k, transform: `translateX(${(1 - k) * -80}px)`, padding: "10px 22px", borderRadius: 40, background: "rgba(240,228,201,.95)", color: P.ink, font: "700 26px MB", letterSpacing: 2 }}>{children}</div>;
};
const Big: React.FC<{ at: number; to?: number; y: number; size?: number; color?: string; sub?: string; children: React.ReactNode }> = ({ at, to = 999, y, size = 150, color = P.cream, sub, children }) => {
  const { t } = useT(); const k = ease((t - at) / 0.5) * clamp((to - t) / 0.4); if (k <= 0) return null;
  return (<div style={{ position: "absolute", left: 56, top: y, opacity: k, textShadow: "0 6px 22px rgba(0,0,0,.65)" }}><div style={{ font: `400 ${size}px DMS`, color, lineHeight: 1 }}>{children}</div>{sub && <div style={{ font: "700 24px MB", letterSpacing: 5, color: P.sand, marginTop: 8 }}>{sub}</div>}</div>);
};

// ------------------------------------------------------------ cenas
const A: React.FC = () => {
  const { t } = useT();
  return (<Sc a={0} b={3.0} zoom={0.09} ov={<>
    {t > 0 && <div style={{ position: "absolute", left: 0, right: 0, top: 230, textAlign: "center", opacity: ease(t / 0.25) * clamp((2.9 - t) / 0.3) }}><div style={{ font: "400 210px DMS", color: P.cream, textShadow: "0 10px 40px rgba(0,0,0,.7)", letterSpacing: 4 }}>LAMPIÃO</div></div>}
    {t > S[1][0] - 0.1 && <div style={{ position: "absolute", left: 0, right: 0, top: 500, textAlign: "center", opacity: ease((t - S[1][0] + 0.1) / 0.4) * clamp((2.9 - t) / 0.3) }}><div style={{ display: "inline-block", padding: "12px 34px", background: P.ochre, color: P.ink, font: "400 70px DMS", letterSpacing: 2 }}>HERÓI OU BANDIDO?</div></div>}</>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>{sunset("va", "#2b2f5a", "#c0586e", "#f09a62", "#f8cd8a")}</defs>
      <rect width="1080" height="1500" fill="url(#va)" /><Star n={30} /><circle cx="560" cy="1010" r="210" fill="#ffe3a8" opacity=".95" />
      <Hills y={1130} c="#8a5a6a" amp={130} seed={4} dx={-t * 4} /><Hills y={1230} c="#5a3f50" amp={110} seed={9} dx={-t * 8} />
      <rect y="1330" width="1080" height="700" fill="#4a3228" />
      <Arbusto x={140} y={1420} s={1.8} c="#241810" /><Arbusto x={930} y={1430} s={1.6} c="#241810" /><Mandacaru x={80} y={1480} s={2.0} c="#10150f" />
      <Cang x={540} y={1400} s={4.2} walk={false} c="#0a0a0f" /></svg></Sc>);
};
const B1: React.FC = () => {
  const { t } = useT();
  return (<Sc a={S[2][0] - 0.2} b={S[3][0] + 0.2} zoom={0} ov={<>
    <Cartela at={S[2][0]} to={S[3][0] - 0.2} date="ENTRE 1897 E 1900" sub="NASCE VIRGULINO" y={210} fs={56} />
    <Pill at={M.pern - 0.2} to={S[3][0]} y={420}>PERNAMBUCO</Pill>
    <div style={{ position: "absolute", left: 56, top: 1400, font: "italic 400 24px PFI", color: "rgba(40,30,18,.75)" }}>mapa com as fronteiras de hoje</div></>}>
    <MapV fill={{ Pernambuco: "#c9a25c" }} zoomTo={SERRA} at={S[2][0]} z={1.9}>{(z) => <g opacity={ease((t - M.a1897) / 0.4)}><circle cx={SERRA[0]} cy={SERRA[1]} r={(22 + 9 * Math.sin(t * 6)) / z} fill="none" stroke={P.red} strokeWidth={4 / z} /><circle cx={SERRA[0]} cy={SERRA[1]} r={9 / z} fill={P.red} /></g>}</MapV>
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(16,20,28,.55) 0%, rgba(16,20,28,0) 28%)" }} /></Sc>);
};
const B2: React.FC = () => {
  const { t } = useT(); const a = S[3][0] - 0.2, p = t - a, carr = clamp((t - M.briga) / 2.9);
  return (<Sc a={a} b={S[4][0] + 0.3} zoom={0.06} ov={<Cartela at={S[3][0]} to={S[4][0]} date="A FAMÍLIA DEIXA O SÍTIO" sub="DEPOIS DE UMA BRIGA COM O VIZINHO" y={210} fs={46} />}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>{sunset("vb", "#4a5c7a", "#c99a78", "#e6bf8a", "#f1d9a6")}</defs>
      <rect width="1080" height="1300" fill="url(#vb)" /><Hills y={1000} c="#8a6a5a" amp={110} seed={5} dx={-p * 4} /><Hills y={1080} c="#6a5448" amp={80} seed={13} dx={-p * 8} />
      <rect y="1100" width="1080" height="900" fill="#a3763e" />
      <Casa x={230} y={1230} s={1.6} wall="#d6b583" roof="#8a5a38" /><Cerca x={20} y={1280} w={400} h={80} />
      <g transform={`translate(${-250 + 1500 * carr} 1330)`}><rect x="-110" y="-70" width="220" height="60" fill="#6b4a28" /><rect x="-90" y="-130" width="180" height="60" fill="#b88a50" /><path d="M-100 -130 Q0 -190 100 -130" fill="#e4d4b0" /><circle cx="-70" cy="-6" r="34" fill="none" stroke="#2a1e14" strokeWidth="9" /><circle cx="70" cy="-6" r="34" fill="none" stroke="#2a1e14" strokeWidth="9" /></g>
      <Mandacaru x={960} y={1260} s={1.5} c="#3a5a38" /></svg></Sc>);
};
const B3: React.FC = () => {
  const { t } = useT(); const a = S[4][0] - 0.2, p = t - a;
  return (<Sc a={a} b={S[5][0] + 0.2} zoom={0.07} ov={<Cartela at={S[4][0]} to={S[5][0]} date="ENTRA NO CANGAÇO" sub="UM SERTÃO DE GUERRAS ENTRE FAMÍLIAS" y={210} fs={52} />}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>{sunset("vc", "#241d2e", "#7a3a48", "#d27a5a", "#efa868")}</defs>
      <rect width="1080" height="1300" fill="url(#vc)" /><Star n={24} /><circle cx="300" cy="1030" r="150" fill="#ffd9a0" opacity=".8" />
      <Hills y={1080} c="#4a2c3a" amp={110} seed={8} dx={-p * 4} /><Hills y={1160} c="#2c1c28" amp={90} seed={14} dx={-p * 7} />
      <rect y="1220" width="1080" height="800" fill="#1d1a2a" />
      <Mandacaru x={160} y={1290} s={1.8} c="#0a0c12" /><Mandacaru x={980} y={1300} s={1.6} c="#0a0c12" />
      {Array.from({ length: 5 }, (_, i) => { const u = (p * 0.35 + i * 0.22) % 1.3 - 0.15; return <Cang key={i} x={-100 + 1300 * u} y={1480 + 26 * (i % 3)} s={1.6 - 0.1 * (i % 3)} ph={i * 1.1} c="#07080d" />; })}
    </svg></Sc>);
};
const C1: React.FC = () => {
  const { t } = useT(); const a = S[5][0] - 0.2, p = t - a;
  return (<Sc a={a} b={S[6][0] + 0.2} zoom={0.06} ov={<>
    <Cartela at={S[5][0]} to={S[6][0] - 0.1} date="1922" sub="ASSUME O COMANDO DO BANDO" y={210} fs={90} />
    <Pill at={M.rei - 0.3} to={S[6][0]} y={460}>O REI DO CANGAÇO</Pill></>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>{sunset("vd", "#5a7aa0", "#d29a78", "#f0b878", "#f6d89a")}</defs>
      <rect width="1080" height="1250" fill="url(#vd)" /><Hills y={1000} c="#a4695a" amp={100} seed={5} dx={-p * 5} /><Hills y={1080} c="#7a4e4c" amp={80} seed={9} dx={-p * 9} />
      <rect y="1150" width="1080" height="800" fill="#b98a4e" />
      {[100, 520, 960].map((x, i) => <Arbusto key={i} x={x} y={1250 + 14 * (i % 3)} s={1.6} c="#4a3524" />)}
      {[0, 1, 2].map((i) => <Cavalo key={i} x={((p * 190 + i * 480) % 1500) - 250} y={1480 + 26 * (i % 2)} s={1.5 - 0.1 * (i % 2)} ph={i * 1.3} speed={9} />)}
    </svg></Sc>);
};
const C2: React.FC = () => {
  const { t } = useT(); const a = S[6][0] - 0.2, t0 = M.sete - 0.3;
  const fill: Record<string, string> = {}; SEVEN.forEach(([n]: [string, string], i: number) => { if (t >= t0 + i * 0.42) fill[n] = "#c9a25c"; });
  const n7 = Math.min(7, Math.max(0, Math.floor((t - t0) / 0.42) + 1));
  return (<Sc a={a} b={S[7][0] + 0.2} zoom={0} ov={<>
    <Cartela at={S[6][0]} to={S[7][0] - 0.1} date="16 ANOS DE CANGAÇO" sub="7 ESTADOS DO NORDESTE" y={210} fs={56} />
    <Big at={t0} to={S[7][0] - 0.2} y={380} size={140} color={P.ochre}>{n7}<span style={{ fontSize: 66, color: P.cream }}> / 7</span></Big>
    <Pill at={M.duzentos - 0.3} to={S[7][0]} y={560}>+ DE 200 CONFRONTOS COM AS VOLANTES</Pill>
    <Pill at={M.mil - 0.7} to={S[7][0]} y={630}>+ DE MIL MORTES · ESTIMATIVA</Pill>
    <div style={{ position: "absolute", left: 56, top: 1400, font: "italic 24px PFI", color: "rgba(40,30,18,.75)" }}>mapa com as fronteiras de hoje</div></>}>
    <MapV fill={fill}>{() => <g>{SEVEN.map(([n, sg]: [string, string]) => { const f = FS.find((x: any) => x.properties.name === n); const c = gV.centroid(f) as [number, number]; return t >= t0 ? <text key={n} x={c[0]} y={c[1]} textAnchor="middle" fontFamily="MS" fontSize="30" fill="#3a2a14" opacity=".85">{sg}</text> : null; })}</g>}</MapV>
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(16,20,28,.6) 0%, rgba(16,20,28,.25) 36%, rgba(16,20,28,0) 48%)" }} /></Sc>);
};
const D: React.FC = () => {
  const { t } = useT(); const a = S[7][0] - 0.2, p = t - a;
  return (<Sc a={a} b={S[8][0] + 0.2} zoom={0.07} ov={<>
    <Cartela at={S[7][0]} to={S[8][0] - 0.1} date="1930" sub="BAHIA · MARIA BONITA" y={210} fs={90} />
    <Pill at={M.primeira - 0.3} to={S[8][0]} y={460}>PRIMEIRA MULHER NO BANDO</Pill></>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>{sunset("ve", "#3b4a78", "#d27a8a", "#f4b070", "#f8d89a")}</defs>
      <rect width="1080" height="1400" fill="url(#ve)" /><Star n={20} /><circle cx="780" cy="1040" r="170" fill="#ffe7b0" opacity=".95" />
      <Hills y={1080} c="#a4695a" amp={100} seed={5} dx={-p * 3} /><Hills y={1160} c="#7a4e4c" amp={80} seed={9} dx={-p * 6} />
      <rect y="1250" width="1080" height="800" fill="#b98a4e" />
      <Arbusto x={140} y={1330} s={1.6} c="#4a3524" /><Mandacaru x={990} y={1380} s={1.7} c="#2f4a2e" />
      <Cang x={400} y={1470} s={2.7} walk={false} rifle={false} c="#0a0a0f" />
      <g transform="translate(620 1470) scale(2.6)" fill="#0a0a0f"><rect x="-12" y="-22" width="10" height="58" /><rect x="4" y="-22" width="10" height="58" /><path d="M-14 -78 L14 -78 L34 -22 L-34 -22 Z" /><circle cx="0" cy="-92" r="12" /><path d="M-22 -102 Q-22 -136 0 -140 Q22 -136 22 -102 Z" /><path d="M-44 -100 Q0 -90 44 -100 Q38 -116 30 -120 L-30 -120 Q-38 -116 -44 -100 Z" /><circle cx="0" cy="-120" r="4" fill={P.ochre} /></g>
    </svg></Sc>);
};
const E: React.FC = () => {
  const { t } = useT(); const a = S[8][0] - 0.2;
  const shots = [40.3, 40.7, 41.1, 41.6, 42.0, 42.4, 42.9, 43.3];
  return (<Sc a={a} b={S[9][0] + 0.3} zoom={0.07} ov={<>
    <Cartela at={S[8][0]} to={S[9][0] - 0.2} date="28 DE JULHO DE 1938" sub="GROTA DO ANGICO · SERGIPE" y={210} fs={54} />
    <Pill at={M.surp - 0.2} to={S[9][0]} y={440}>A VOLANTE SURPREENDE O BANDO</Pill></>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs><linearGradient id="vf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#10162a" /><stop offset=".6" stopColor="#1c2438" /><stop offset="1" stopColor="#2a3240" /></linearGradient></defs>
      <rect width="1080" height="1400" fill="url(#vf)" /><Hills y={1050} c="#1c2630" amp={110} seed={11} /><Hills y={1130} c="#121a22" amp={90} seed={16} />
      <rect y="1200" width="1080" height="800" fill="#141a1e" />
      {[180, 540, 900].map((x, i) => <Barraca key={i} x={x} y={1330 + 20 * (i % 2)} s={1.5} c={i % 2 ? "#2c3038" : "#242830"} />)}
      {[80, 1000].map((x, i) => <Mandacaru key={i} x={x} y={1450} s={1.5} c="#070a0c" />)}
      {shots.map((s, i) => <Flash key={i} x={100 + (i % 3) * 120} y={1200 + (i % 4) * 50} at={s} big={1.0} />)}{shots.map((s, i) => <Flash key={"b" + i} x={960 - (i % 3) * 110} y={1210 + (i % 3) * 60} at={s + 0.2} big={0.9} />)}
      <Rain o={0.4} /></svg></Sc>);
};
const F: React.FC = () => {
  const { t } = useT(); const a = S[9][0] - 0.2;
  return (<Sc a={a} b={S[12][0] - 0.1} zoom={0.06} ov={<>
    <Cartela at={S[9][0]} to={S[12][0] - 0.3} date="EM CERCA DE 20 MINUTOS" y={210} fs={50} />
    <Big at={M.onze - 0.2} to={S[12][0] - 0.3} y={400} size={190} color={P.cream} sub="CANGACEIROS MORTOS">{<>11</>}</Big>
    <Pill at={M.eles - 0.1} to={S[12][0] - 0.2} y={740}>ENTRE ELES: LAMPIÃO E MARIA BONITA</Pill></>}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs><linearGradient id="vg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#1a1a36" /><stop offset=".55" stopColor="#4a4a6a" /><stop offset="1" stopColor="#a8665a" /></linearGradient></defs>
      <rect width="1080" height="1400" fill="url(#vg)" /><Star n={30} /><Hills y={1050} c="#2a3038" amp={110} seed={11} /><Hills y={1130} c="#161c24" amp={90} seed={16} />
      <rect y="1200" width="1080" height="800" fill="#141a1e" />
      {[180, 540, 900].map((x, i) => <Barraca key={i} x={x} y={1330 + 20 * (i % 2)} s={1.5} c={i % 2 ? "#2c3038" : "#242830"} />)}
      {[80, 1000].map((x, i) => <Mandacaru key={i} x={x} y={1450} s={1.5} c="#070a0c" />)}
      <Rain o={0.15} /></svg></Sc>);
};
const G: React.FC = () => {
  const { t } = useT();
  const blk = (at: number, y: number, c: string, lab: string, word: string) => (<div style={{ position: "absolute", left: 56, right: 140, top: y, opacity: ease((t - at) / 0.5), transform: `translateX(${(1 - ease((t - at) / 0.5)) * -80}px)`, borderLeft: `10px solid ${c}`, paddingLeft: 30 }}>
    <div style={{ font: "700 24px MB", letterSpacing: 5, color: P.sand }}>{lab}</div><div style={{ font: "400 120px DMS", color: P.cream, lineHeight: 1.05 }}>{word}</div></div>);
  return (<Sc a={S[12][0] - 0.2} b={58.5} zoom={0.02}>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><rect width="1080" height="1920" fill="#14181f" /><g stroke="rgba(240,228,201,.06)" strokeWidth="2">{Array.from({ length: 14 }, (_, i) => <line key={i} x1="0" y1={i * 140} x2="1080" y2={i * 140} />)}</g></svg>
    <div style={{ position: "absolute", left: 56, right: 140, top: 230, font: "400 92px DMS", color: P.cream, opacity: ease((t - S[12][0] + 0.2) / 0.5), lineHeight: 1.05 }}>HERÓI OU BANDIDO?</div>
    {blk(M.auto - 0.2, 520, P.red, "PARA AS AUTORIDADES", "brutalidade")}{blk(M.sert - 0.2, 800, P.ochre, "PARA PARTE DOS SERTANEJOS", "bravura")}
    {t > M.voce - 0.2 && <div style={{ position: "absolute", left: 56, right: 140, top: 1090, font: "400 76px DMS", color: P.cream, opacity: ease((t - M.voce + 0.2) / 0.5), lineHeight: 1.1 }}>E você, o que acha?</div>}
    {t > 56.4 && <div style={{ position: "absolute", left: 56, top: 1260, opacity: ease((t - 56.4) / 0.5) }}><span style={{ display: "inline-block", padding: "12px 28px", background: P.ochre, color: P.ink, font: "400 40px DMS", letterSpacing: 2 }}>HISTÓRIA COMPLETA NO YOUTUBE</span><div style={{ font: "700 26px MB", letterSpacing: 4, color: P.sand, marginTop: 10 }}>@EZVIDEOS2979</div></div>}
    <div style={{ position: "absolute", left: 56, right: 140, top: 1385, font: "italic 400 22px PFI", color: "rgba(240,228,201,.6)", opacity: ease((t - 52) / 0.8) }}>Fonte: Wikipédia (Virgulino Ferreira da Silva). Números são estimativas.</div>
  </Sc>);
};
// legenda acima da área coberta por Instagram/TikTok (base a ~470 px do fundo; margem direita maior)
const Legenda: React.FC = () => {
  const { t } = useT(); const c = (TM.caps as any[]).find((x) => t >= x.t - 0.02 && t < x.e + 0.18); if (!c) return null;
  const u = clamp((t - c.t) / 0.15);
  return (<><div style={{ position: "absolute", left: 0, right: 0, top: 1280, height: 640, background: "linear-gradient(to bottom, rgba(8,6,4,0), rgba(8,6,4,.66) 45%, rgba(8,6,4,.7))" }} />
    <div style={{ position: "absolute", left: 60, right: 140, top: 1440, textAlign: "center", font: "400 58px PF", color: P.cream, textShadow: "0 4px 14px rgba(0,0,0,.85), 0 0 4px rgba(0,0,0,.9)", opacity: u, transform: `translateY(${(1 - u) * 14}px)`, lineHeight: 1.15 }}>
      {c.words.map((w: any, i: number) => { const on = t >= w.s && t < w.e + 0.04; return <span key={i} style={{ color: on ? P.ochre : P.cream, display: "inline-block", transform: on ? "scale(1.07)" : "none", marginRight: 14 }}>{w.w}</span>; })}</div></>);
};
export const LampiaoCurto: React.FC = () => {
  const { t } = useT();
  return (<AbsoluteFill style={{ background: "#0d1017" }}><style>{FONT}</style>
    <A /><B1 /><B2 /><B3 /><C1 /><C2 /><D /><E /><F /><G /><Vig /><Grain />{t < 57.6 && <Legenda />}
  </AbsoluteFill>);
};
export const LampiaoCurtoCapa: React.FC = () => (
  <AbsoluteFill style={{ background: "#12151c" }}><style>{FONT}</style>
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>{sunset("vcp", "#2b2f5a", "#c0586e", "#f09a62", "#f8cd8a")}</defs>
      <rect width="1080" height="1920" fill="#12151c" /><rect y="560" width="1080" height="940" fill="url(#vcp)" /><circle cx="600" cy="1070" r="210" fill="#ffe3a8" opacity=".96" />
      <Hills y={1190} c="#8a5a6a" amp={130} seed={4} /><Hills y={1290} c="#5a3f50" amp={110} seed={9} /><rect y="1370" width="1080" height="140" fill="#2a1c18" />
      <Mandacaru x={90} y={1450} s={2.2} c="#0a0c10" /><Arbusto x={960} y={1430} s={1.8} c="#1a100c" /><Cang x={560} y={1420} s={4.4} walk={false} c="#07070b" />
      <rect y="1500" width="1080" height="420" fill="#12151c" /><rect y="556" width="1080" height="6" fill="#d9a441" /><rect y="1496" width="1080" height="6" fill="#d9a441" />
      <text x="540" y="210" textAnchor="middle" fontFamily="MB" fontSize="28" fill="#d9a441" letterSpacing="8">O REI DO CANGAÇO</text>
      <text x="540" y="410" textAnchor="middle" fontFamily="DMS" fontSize="200" fill="#f0e4c9">Lampião</text><rect x="440" y="470" width="200" height="6" fill="#d9a441" />
      <text x="540" y="1610" textAnchor="middle" fontFamily="DMS" fontSize="92" fill="#d9a441">Herói ou bandido?</text></svg><Vig />
  </AbsoluteFill>
);
