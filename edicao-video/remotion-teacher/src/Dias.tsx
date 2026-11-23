// Aula "Dias e meses" (s8-a1, 23/11/2026). Tempos: timings/dias.json (scripts/prep_aula.py + aulas/aula_dias.py).
// Melhoria desta aula: marcas desenhadas à mão (círculo que se traça sozinho em volta da letra maiúscula) e linha acesa no dia/mês que a voz está falando.
import React from "react";
import TM from "./timings/dias.json";
import { useT, Chip, Box, Outline, Emoji, Center, Pop, Cena, Card, Quiz, Chamada, Licao, CapaBase, QuizItem, clamp,
  INK, YEL, MUTED, C_A, C_AN, C_THE, GREY, RED, PT } from "./kit";
const T = TM.t as Record<string, number>;
const W = { font: "400 112px Anton", color: "#fff", ...Outline } as any;
const eo = (x: number) => 1 - Math.pow(1 - clamp(x), 3);

/** círculo desenhado à mão: o traço aparece aos poucos em volta do que estiver dentro do contêiner relativo */
const Circulo: React.FC<{ at: number; w: number; h: number; c?: string; sw?: number }> = ({ at, w, h, c = RED, sw = 9 }) => {
  const { t } = useT(); const k = eo((t - at) / 0.55); if (k <= 0) return null;
  const d = `M ${w * 0.52} ${h * 0.05} C ${w * 0.92} ${h * 0.0}, ${w * 1.02} ${h * 0.72}, ${w * 0.56} ${h * 0.97} C ${w * 0.1} ${h * 1.06}, ${-w * 0.04} ${h * 0.3}, ${w * 0.44} ${h * 0.09} C ${w * 0.62} ${h * 0.03}, ${w * 0.78} ${h * 0.1}, ${w * 0.84} ${h * 0.22}`;
  return <svg width={w} height={h} style={{ position: "absolute", left: 0, top: 0, overflow: "visible", pointerEvents: "none", filter: "drop-shadow(0 4px 6px rgba(0,0,0,.4))" }}>
    <path d={d} pathLength={1} fill="none" stroke={c} strokeWidth={sw} strokeLinecap="round" strokeDasharray={1} strokeDashoffset={1 - k} /></svg>;
};
/** a letra inicial grande e destacada, com o círculo traçado em volta */
const Inicial: React.FC<{ word: string; at: number; size?: number; cap?: boolean }> = ({ word, at, size = 96, cap = true }) => (
  <span style={{ display: "inline-flex", font: `400 ${size}px Anton`, color: "#fff", ...Outline } as any}>
    <span style={{ position: "relative", display: "inline-block", color: cap ? YEL : "#fff" }}>{word[0]}{cap && <span style={{ position: "absolute", left: -size * 0.2, top: -size * 0.06 }}><Circulo at={at} w={size * 0.95} h={size * 1.2} /></span>}</span>
    <span>{word.slice(1)}</span></span>
);

// ------------------------------------------------------------ gancho
const Gancho: React.FC = () => {
  const { t } = useT();
  const wob = t > T.care ? 5 * Math.sin((t - T.care) * 18) * Math.exp(-(t - T.care) * 2) : 0;
  return (<Cena a={0} b={T.dia - 0.1}>
    <Pop at={0.05} y={265}><Chip bg={C_AN} size={38}>BÁSICO · A1</Chip></Pop>
    <Pop at={T.tit} y={500} from={0.3}><div style={{ font: "400 170px Anton", color: YEL, ...Outline, textAlign: "center", lineHeight: 0.95 } as any}>DAYS<br /><span style={{ fontSize: 110, color: "#fff" }}>& MONTHS</span></div></Pop>
    <Pop at={T.car1} y={800}><Card w={780}><span style={{ font: "400 100px Anton", color: "#fff" }}>monday?</span></Card></Pop>
    <Pop at={T.car2} y={990}><div style={{ transform: `rotate(${wob}deg)` }}><Card w={780} border={t > T.care ? C_THE : undefined}><Inicial word="Monday?" at={T.care + 0.1} size={100} /></Card></div></Pop>
    <Pop at={T.care} y={1140}><Chip bg={RED} size={50}><Emoji e="⚠️" size={48} style={{ marginRight: 14, verticalAlign: -6 }} />CUIDADO!</Chip></Pop>
  </Cena>);
};

// ------------------------------------------------------------ os dias
const DIAS = [["Monday", "segunda", "MON"], ["Tuesday", "terça", "TUE"], ["Wednesday", "quarta", "WED"], ["Thursday", "quinta", "THU"], ["Friday", "sexta", "FRI"], ["Saturday", "sábado", "SAT"], ["Sunday", "domingo", "SUN"]];
const Dias: React.FC = () => {
  const { t } = useT();
  return (<Cena a={T.dia} b={T.mes - 0.1}>
    <Pop at={T.dia + 0.05} y={300}><Chip bg={YEL} color={INK} size={46}>OS DIAS · DAYS</Chip></Pop>
    {DIAS.map(([en, pt, ab], i) => { const at = T["d" + i], ap = T["pd" + i], on = t >= at && t < at + 0.95, c = i >= 5 ? C_AN : C_A;
      return (<Pop key={en} at={at} y={470 + i * 104} dx={-260}><div style={{ width: 860, height: 92, borderRadius: 24, background: "rgba(8,20,48,.86)", border: `4px solid ${on ? YEL : "rgba(255,255,255,.18)"}`, display: "flex", alignItems: "center", gap: 24, padding: "0 18px",
        transform: `scale(${on ? 1.04 : 1})`, boxShadow: on ? `0 0 34px ${YEL}88` : "0 10px 22px rgba(0,0,0,.35)" }}>
        <div style={{ width: 120, height: 62, borderRadius: 16, background: c, color: "#fff", font: "800 34px Montserrat", display: "grid", placeItems: "center", letterSpacing: 1 }}>{ab}</div>
        <span style={{ font: "400 58px Anton", color: "#fff", flex: 1 }}>{en}</span>
        <span style={{ font: "800 36px Montserrat", color: PT, opacity: clamp((t - ap) / 0.2) }}>{pt}</span>
      </div></Pop>); })}
  </Cena>);
};

// ------------------------------------------------------------ os meses
const MESES = [["January", "janeiro"], ["February", "fevereiro"], ["March", "março"], ["April", "abril"], ["May", "maio"], ["June", "junho"], ["July", "julho"], ["August", "agosto"], ["September", "setembro"], ["October", "outubro"], ["November", "novembro"], ["December", "dezembro"]];
const Meses: React.FC = () => {
  const { t } = useT();
  return (<Cena a={T.mes} b={T.r1 - 0.1}>
    <Pop at={T.mes + 0.05} y={300}><Chip bg={YEL} color={INK} size={46}>OS MESES · MONTHS</Chip></Pop>
    {MESES.map(([en, pt], i) => { const at = T["m" + i], ap = T["pm" + i], on = t >= at && t < at + 0.9, x = ((i % 3) - 1) * 330, y = 462 + Math.floor(i / 3) * 184;
      return (<Pop key={en} at={at} y={y} dx={0}><div style={{ transform: `translateX(${x}px) scale(${on ? 1.06 : 1})`, width: 304, height: 176, borderRadius: 22, background: "#f6f8fc", overflow: "hidden", position: "relative",
        border: `4px solid ${on ? YEL : "rgba(255,255,255,.5)"}`, boxShadow: on ? `0 0 34px ${YEL}99` : "0 12px 26px rgba(0,0,0,.4)" }}>
        <div style={{ height: 34, background: C_THE, display: "flex", justifyContent: "space-around", alignItems: "center" }}>{[0, 1, 2].map((k) => <div key={k} style={{ width: 14, height: 14, borderRadius: "50%", background: "rgba(255,255,255,.85)" }} />)}</div>
        <div style={{ textAlign: "center", font: "400 54px Anton", color: INK, marginTop: 6, lineHeight: 1.1 }}>{en}</div>
        <div style={{ textAlign: "center", font: "800 32px Montserrat", color: "#4b5f86", lineHeight: 1.25, opacity: clamp((t - ap) / 0.2) }}>{pt}</div>
      </div></Pop>); })}
  </Cena>);
};

// ------------------------------------------------------------ regra 1: letra maiúscula
const Par: React.FC<{ at: number; y: number; good: string; bad: string; badAt?: number }> = ({ at, y, good, bad }) => (
  <Pop at={at} y={y}><div style={{ display: "flex", alignItems: "center", gap: 36 }}>
    <div style={{ display: "flex", alignItems: "center", gap: 14 }}><Emoji e="✅" size={74} /><Inicial word={good} at={at + 0.6} size={96} /></div>
    <div style={{ display: "flex", alignItems: "center", gap: 14, opacity: 0.8 }}><Emoji e="❌" size={64} /><span style={{ font: "400 84px Anton", color: GREY, ...Outline, textDecoration: "line-through", textDecorationColor: C_THE, textDecorationThickness: 9 } as any}>{bad}</span></div>
  </div></Pop>
);
const Regra1: React.FC = () => (
  <Cena a={T.r1} b={T.r2 - 0.1}>
    <Pop at={T.r1 + 0.05} y={300}><Chip bg={C_A} size={46}>REGRA 1</Chip></Pop>
    <Pop at={T.r1h} y={480} from={0.3}><div style={{ display: "flex", alignItems: "center", gap: 22, font: "400 100px Anton", color: "#fff", ...Outline } as any}>
      <Box c={C_THE} size={100} tight>CAPITAL</Box><span>LETTER</span></div></Pop>
    <Par at={T.r1a} y={720} good="Monday" bad="monday" />
    <Par at={T.r1b} y={900} good="March" bad="march" />
    <Pop at={T.r1p} y={1075}><Chip bg="rgba(8,20,48,.9)" size={34} style={{ border: `3px solid ${YEL}` }}>Em português é minúscula: segunda, março</Chip></Pop>
  </Cena>
);

// ------------------------------------------------------------ regra 2: pronúncia
const Regra2: React.FC = () => (
  <Cena a={T.r2} b={T.r3 - 0.1}>
    <Pop at={T.r2 + 0.05} y={300}><Chip bg={C_THE} size={46}>REGRA 2 · PRONÚNCIA</Chip></Pop>
    <Pop at={T.r2a} y={510}><div style={{ ...W, fontSize: 118 } as any}>We<span style={{ color: GREY, textDecoration: "line-through", textDecorationColor: C_THE, textDecorationThickness: 12 }}>d</span>nesday</div></Pop>
    <Pop at={T.r2a + 0.35} y={660}><div style={{ font: "400 66px Anton", color: "#fff" }}><Box c={C_A} size={66}>WENZ-day</Box></div></Pop>
    <Pop at={T.r2d} y={770}><Chip bg="rgba(8,20,48,.9)" size={36} style={{ border: `3px solid ${YEL}` }}>o D é mudo</Chip></Pop>
    <Pop at={T.r2b} y={920}><div style={{ ...W, fontSize: 118 } as any}>February</div></Pop>
    <Pop at={T.r2b + 0.35} y={1055}><div style={{ font: "400 62px Anton", color: "#fff" }}><Box c={C_AN} size={62}>FEB-yoo-air-ee</Box></div></Pop>
  </Cena>
);

// ------------------------------------------------------------ regra 3: fim de semana
const Regra3: React.FC = () => {
  const { t } = useT(); const LET = ["M", "T", "W", "T", "F", "S", "S"];
  return (<Cena a={T.r3} b={T.quiz - 0.1}>
    <Pop at={T.r3 + 0.05} y={300}><Chip bg={C_AN} size={46}>REGRA 3 · FIM DE SEMANA</Chip></Pop>
    <Pop at={T.r3h} y={500} from={0.3}><div style={{ font: "400 130px Anton", color: "#fff", ...Outline } as any}><Box c={C_AN} size={130} tight>WEEKEND</Box></div></Pop>
    <Pop at={T.r3h + 0.2} y={760}><div style={{ display: "flex", gap: 18 }}>{LET.map((l, i) => { const at = i === 5 ? T.r3a : i === 6 ? T.r3b : 9999, on = t >= at, k = on ? 1 + 0.12 * Math.exp(-(t - at) * 7) : 1;
      return <div key={i} style={{ width: 112, height: 112, borderRadius: 26, background: on ? C_AN : "rgba(255,255,255,.16)", color: "#fff", font: "400 66px Anton", display: "grid", placeItems: "center", transform: `scale(${k})`, border: `4px solid ${on ? "#fff" : "rgba(255,255,255,.25)"}`, boxShadow: on ? `0 0 30px ${C_AN}aa` : "none" }}>{l}</div>; })}</div></Pop>
    {t >= T.r3a && <Pop at={T.r3a} y={920}><div style={{ display: "flex", gap: 120, font: "400 56px Anton", color: "#fff", ...Outline } as any}><span style={{ opacity: 1 }}>SATURDAY</span>{t >= T.r3b && <span>SUNDAY</span>}</div></Pop>}
    <Pop at={T.r3p} y={1075}><Chip bg="rgba(8,20,48,.9)" size={40} style={{ border: `3px solid ${YEL}` }}>weekend = fim de semana</Chip></Pop>
  </Cena>);
};

// ------------------------------------------------------------ quiz
const QUIZ: QuizItem[] = [
  { e: "📅", before: "after Friday:", answer: "Saturday", fs: 92, opts: [["Saturday", true], ["Sunday", false]], tip: <>Friday → <b style={{ color: C_AN }}>Saturday</b> → Sunday</> },
  { e: "🗓️", before: "after April:", answer: "May", fs: 100, opts: [["May", true], ["June", false]], tip: <>April → <b style={{ color: C_AN }}>May</b> → June</> },
];
export const Dias_: React.FC = () => (
  <Licao tm={TM} hl={{}}>
    <Gancho /><Dias /><Meses /><Regra1 /><Regra2 /><Regra3 /><Quiz items={QUIZ} /><Chamada />
  </Licao>
);
export { Dias_ as DiasAula };

export const DiasCapa: React.FC = () => (
  <CapaBase tm={TM} tt={4.5}>
    <Center y={245}><Chip bg={C_AN} size={40}>BÁSICO · A1</Chip></Center>
    <Center y={530}><div style={{ font: "400 170px Anton", color: YEL, ...Outline, textAlign: "center", lineHeight: 0.95 } as any}>DAYS<br /><span style={{ fontSize: 110, color: "#fff" }}>& MONTHS</span></div></Center>
    <Center y={800}><div style={{ display: "flex", gap: 14 }}>{["M", "T", "W", "T", "F", "S", "S"].map((l, i) => <div key={i} style={{ width: 96, height: 96, borderRadius: 22, background: i > 4 ? C_AN : "rgba(255,255,255,.18)", color: "#fff", font: "400 56px Anton", display: "grid", placeItems: "center", border: "4px solid rgba(255,255,255,.7)" }}>{l}</div>)}</div></Center>
    <Center y={975}><Card w={820}><span style={{ font: "400 110px Anton", color: "#fff" }}>monday</span></Card></Center>
    <Center y={1105}><span style={{ font: "800 56px Montserrat", color: MUTED }}>ou</span></Center>
    <Center y={1235}><Card w={820}><span style={{ font: "400 110px Anton", color: "#fff" }}>Monday</span></Card></Center>
    <Center y={1405}><Chip bg={C_THE} size={46}>VOCÊ ESCREVE CERTO? · QUIZ</Chip></Center>
  </CapaBase>
);
