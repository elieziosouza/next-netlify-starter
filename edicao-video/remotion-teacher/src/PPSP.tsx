// Aula "Present Perfect × Simple Past" (14/11/2026, B1). Tempos: timings/ppsp.json (scripts/prep_aula.py + aulas/aula_ppsp.py).
// Novo: linha do tempo animada (tempo fechado × tempo aberto até o agora) para explicar a diferença.
import React from "react";
import TM from "./timings/ppsp.json";
import { useT, usePop, Chip, Box, Outline, Emoji, Center, Pop, Cena, Card, Quiz, Chamada, Licao, CapaBase, QuizItem,
  INK, YEL, MUTED, C_A, C_AN, C_THE, GREY, GREEN, RED, clamp } from "./kit";
const T = TM.t as Record<string, number>;
const C_B1 = "#e0a612";
const W = { font: "400 84px Anton", color: "#fff", ...Outline } as any;
const TLY = 770, XA = 90, XB = 990, XNOW = 880;      // linha do tempo: y, início, fim e posição do "agora"

/** coloca um elemento no centro (x, y) com a entrada em mola */
const At: React.FC<{ at: number; x: number; y: number; dx?: number; from?: number; children: React.ReactNode }> = ({ at, x, y, dx, from, children }) => {
  const p = usePop(at, { dx, from }); if (!p.visible) return null;
  return <div style={{ position: "absolute", left: x, top: y, transform: "translate(-50%, -50%)" }}><div style={p.style}>{children}</div></div>;
};
const Barra: React.FC<{ x0: number; x1: number; at: number; c: string; h?: number; dur?: number; glow?: boolean }> = ({ x0, x1, at, c, h = 22, dur = 0.5, glow }) => {
  const { t } = useT(); const k = clamp((t - at) / dur); if (k <= 0) return null;
  const e = 1 - Math.pow(1 - k, 3);
  return <div style={{ position: "absolute", left: x0, top: TLY - h / 2, width: (x1 - x0) * e, height: h, borderRadius: h / 2, background: c, boxShadow: glow ? `0 0 46px ${c}` : "0 6px 0 rgba(0,0,0,.25)" }} />;
};
/** a linha do tempo base: passado → agora → futuro */
const Trilho: React.FC<{ at: number }> = ({ at }) => {
  const { t } = useT(); const k = clamp((t - at) / 0.4); const pulse = 1 + 0.08 * Math.sin(t * 5);
  return (<div style={{ opacity: k }}>
    <div style={{ position: "absolute", left: XA, top: TLY - 9, width: XB - XA, height: 18, borderRadius: 9, background: "#3c5480" }} />
    <div style={{ position: "absolute", left: XA, top: TLY + 34, font: "800 32px Montserrat", color: MUTED }}>PASSADO</div>
    <div style={{ position: "absolute", left: XNOW, top: TLY, width: 62, height: 62, marginLeft: -31, marginTop: -31, borderRadius: "50%", background: YEL, border: `6px solid ${INK}`, boxShadow: "0 0 40px #ffd640aa", transform: `scale(${pulse})` }} />
    <div style={{ position: "absolute", left: XNOW, top: TLY + 54, transform: "translateX(-50%)", font: "800 34px Montserrat", color: YEL, ...Outline, WebkitTextStroke: "6px " + INK } as any}>AGORA</div>
  </div>);
};
const Pin: React.FC<{ at: number; x: number; label: string; up: boolean; c: string }> = ({ at, x, label, up, c }) => {
  const p = usePop(at, { dy: up ? -20 : 20 }); if (!p.visible) return null;
  return (<>
    <div style={{ position: "absolute", left: x - 3, top: up ? TLY - 110 : TLY, width: 6, height: 110, background: c, opacity: p.style.opacity as number, borderRadius: 3 }} />
    <div style={{ position: "absolute", left: x, top: TLY, width: 40, height: 40, marginLeft: -20, marginTop: -20, borderRadius: "50%", background: c, border: `5px solid ${INK}`, opacity: p.style.opacity as number }} />
    <div style={{ position: "absolute", left: x, top: up ? TLY - 150 : TLY + 150, transform: "translate(-50%, -50%)" }}>
      <div style={p.style}><div style={{ background: "#fff", color: INK, font: "800 40px Montserrat", padding: "10px 24px", borderRadius: 22, boxShadow: "0 12px 26px rgba(0,0,0,.4)", whiteSpace: "nowrap" }}>{label}</div></div></div>
  </>);
};

const Gancho: React.FC = () => (
  <Cena a={0} b={4.2}>
    <Pop at={0.05} y={300}><Chip bg={C_B1} color={INK} size={38}>INTERMEDIÁRIO · B1</Chip></Pop>
    <Pop at={1.66} y={520} from={0.3}><div style={{ font: "400 132px Anton", color: YEL, ...Outline } as any}>PRESENT PERFECT</div></Pop>
    <Pop at={2.95} y={680}><Chip bg="#fff" color={INK} size={46}>VERSUS</Chip></Pop>
    <Pop at={3.25} y={840} from={0.3}><div style={{ font: "400 132px Anton", color: "#fff", ...Outline } as any}>SIMPLE PAST</div></Pop>
  </Cena>
);
const Erro: React.FC = () => (
  <Cena a={4.2} b={T.sp}>
    <Pop at={4.25} y={300}><Chip bg={RED} size={46}>ERRO COMUM</Chip></Pop>
    <Pop at={T.wrong} y={640}><Card w={940}><span style={{ font: "400 86px Anton", color: "#fff" }}>I <span style={{ color: GREY, textDecoration: "line-through", textDecorationColor: RED, textDecorationThickness: 9 }}>HAVE</span> SEEN HIM <span style={{ color: YEL }}>YESTERDAY</span></span></Card></Pop>
    <Pop at={7.7} y={900} from={0.3}><Emoji e="❌" size={190} /></Pop>
    <Pop at={T.wrongPt} y={1090}><Chip bg="rgba(8,20,48,.92)" size={40} style={{ border: `4px solid ${YEL}` }}>muita gente erra isso</Chip></Pop>
  </Cena>
);
const SimplePast: React.FC = () => (
  <Cena a={T.sp} b={T.pp}>
    <Pop at={T.sp + 0.05} y={290}><Chip bg={C_THE} size={46}>SIMPLE PAST</Chip></Pop>
    <Pop at={T.sp + 0.5} y={410} from={0.3}><div style={{ ...W, fontSize: 104 } as any}>TEMPO <Box c={C_THE} size={104} tight>FECHADO</Box></div></Pop>
    <Trilho at={T.sp + 0.3} />
    <Barra x0={150} x1={800} at={T.sp + 1.2} c={C_THE} h={26} />
    <Pin at={T.sp1} x={800} label="yesterday" up c={C_THE} />
    <Pin at={T.sp2} x={200} label="last year" up c={C_THE} />
    <Pin at={T.sp3} x={510} label="two days ago" up c={C_THE} />
    <Pop at={T.spPt} y={980}><Chip bg="rgba(8,20,48,.92)" size={42} style={{ border: `4px solid ${YEL}` }}>acabou antes de agora = <b style={{ color: C_THE }}>SIMPLE PAST</b></Chip></Pop>
    <Pop at={T.spEx} y={1120}><Card w={820} border={GREEN}><span style={{ font: "400 76px Anton", color: "#fff" }}>I <Box c={C_THE} size={76} tight>SAW</Box> HIM YESTERDAY <Emoji e="✅" size={64} /></span></Card></Pop>
  </Cena>
);
const PresentPerfect: React.FC = () => { const { t } = useT(); return (
  <Cena a={T.pp} b={T.quiz}>
    <Pop at={T.pp + 0.05} y={290}><Chip bg={C_A} size={46}>PRESENT PERFECT</Chip></Pop>
    <Pop at={T.pp + 0.5} y={410} from={0.3}><div style={{ ...W, fontSize: 80 } as any}><Box c={C_A} size={80} tight>HAVE / HAS</Box> + <Box c={C_AN} size={80} tight>PARTICIPLE</Box></div></Pop>
    <Trilho at={T.pp + 0.3} />
    <Barra x0={150} x1={XNOW} at={T.pp + 1.2} c={C_A} h={30} dur={0.9} glow />
    <At at={T.pp + 1.6} x={600} y={TLY - 95} from={0.4}><div style={{ font: "800 40px Montserrat", color: C_A, ...Outline, WebkitTextStroke: "6px " + INK } as any}>ligado ao agora →</div></At>
    <At at={T.ppE} x={190} y={940}><Chip bg="#fff" color={INK} size={42}>ever</Chip></At>
    <At at={T.ppE + 0.55} x={385} y={940}><Chip bg="#fff" color={INK} size={42}>never</Chip></At>
    <At at={T.ppA} x={620} y={940}><Chip bg="#fff" color={INK} size={42}>already</Chip></At>
    <At at={T.ppA + 0.6} x={860} y={940}><Chip bg={YEL} color={INK} size={42}>since</Chip></At>
    <At at={T.ppEx1} x={540} y={1050}><Card w={800} border={GREEN}><span style={{ font: "400 62px Anton", color: "#fff" }}>I <Box c={C_A} size={62} tight>HAVE SEEN</Box> THAT MOVIE <Emoji e="✅" size={54} /></span></Card></At>
    {t >= T.ppEx2 && <>
      <At at={T.ppEx2} x={300} y={TLY - 95}><Chip bg={YEL} color={INK} size={38}>2020</Chip></At>
      <Barra x0={300} x1={XNOW} at={T.ppEx2 + 0.1} c={YEL} h={36} dur={0.8} glow />
    </>}
    <At at={T.ppEx2} x={540} y={1160}><Card w={900} border={GREEN}><span style={{ font: "400 56px Anton", color: "#fff" }}>I <Box c={C_A} size={56} tight>HAVE LIVED</Box> HERE <span style={{ color: YEL }}>SINCE 2020</span></span></Card></At>
  </Cena>
); };
const QUIZ: QuizItem[] = [
  { e: "🥐", before: "I", answer: "visited", after: "Paris last year", fs: 76, opts: [["I have visited Paris last year", false], ["I visited Paris last year", true]], tip: <>LAST YEAR = tempo fechado → <b style={{ color: C_THE }}>SIMPLE PAST</b></> },
  { e: "🏠", before: "I", answer: "have lived", after: "here since 2020", fs: 76, opts: [["I have lived here since 2020", true], ["I lived here since 2020", false]], tip: <>SINCE = vale até agora → <b style={{ color: C_A }}>PRESENT PERFECT</b></> },
];
export const PPSP: React.FC = () => (
  <Licao tm={TM} hl={{}}>
    <Gancho /><Erro /><SimplePast /><PresentPerfect /><Quiz items={QUIZ} /><Chamada />
  </Licao>
);
export const PPSPCapa: React.FC = () => (
  <CapaBase tm={TM} tt={4.5}>
    <Center y={260}><Chip bg={C_B1} color={INK} size={40}>INTERMEDIÁRIO · B1</Chip></Center>
    <Center y={440}><div style={{ font: "400 132px Anton", color: YEL, ...Outline } as any}>PRESENT PERFECT</div></Center>
    <Center y={590}><span style={{ font: "800 54px Montserrat", color: MUTED }}>ou</span></Center>
    <Center y={740}><div style={{ font: "400 132px Anton", color: "#fff", ...Outline } as any}>SIMPLE PAST</div></Center>
    <Center y={990}><Card w={900}><span style={{ font: "400 84px Anton", color: "#fff" }}>I HAVE SEEN HIM YESTERDAY</span></Card></Center>
    <Center y={1190}><Chip bg={RED} size={46}>ESTÁ CERTO? · QUIZ</Chip></Center>
  </CapaBase>
);
