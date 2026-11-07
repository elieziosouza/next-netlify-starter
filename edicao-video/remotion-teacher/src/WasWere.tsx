// Aula "Was e were" (s3-a2, 07/11/2026). Tempos: timings/waswere.json (scripts/prep_aula.py + aulas/aula_waswere.py).
import React from "react";
import TM from "./timings/waswere.json";
import { useT, Chip, Box, Outline, Emoji, Center, Pop, Cena, Card, Quiz, Chamada, Licao, CapaBase, QuizItem,
  INK, YEL, MUTED, C_A, C_AN, C_THE, GREY, RED, GREEN } from "./kit";
const T = TM.t as Record<string, number>;
const W = { font: "400 100px Anton", color: "#fff", ...Outline } as any;

/** linha "I → WAS": o pronome entra em `at` já com o verbo em caixa colorida */
const Pron: React.FC<{ p: string; v: string; c: string; at: number; y: number; dx?: number }> = ({ p, v, c, at, y, dx = 0 }) => (
  <Pop at={at} y={y}><div style={{ transform: `translateX(${dx}px)`, display: "flex", alignItems: "center", gap: 20, ...W, fontSize: 88 } as any}>
    <span style={{ minWidth: 150, textAlign: "right" }}>{p}</span><Box c={c} size={88} tight>{v}</Box></div></Pop>
);

const Gancho: React.FC = () => (
  <Cena a={0} b={T.conj}>
    <Pop at={0.05} y={300}><Chip bg={C_AN} size={38}>BÁSICO-INTERMEDIÁRIO · A2</Chip></Pop>
    <Pop at={0.2} y={500}><Card w={900}><div style={{ font: "400 84px Anton", color: "#fff", textAlign: "center", lineHeight: 1.1 }}>WHERE <span style={{ color: YEL }}>WERE</span> YOU<br />LAST NIGHT? <Emoji e="🌙" size={72} /></div></Card></Pop>
    <Pop at={2.68} y={850} from={0.3}><div style={{ display: "flex", gap: 30, font: "400 190px Anton" }}><Box c={C_A} size={190}>WAS</Box><Box c={C_THE} size={190}>WERE</Box></div></Pop>
    <Pop at={4.06} y={1070}><Chip bg="rgba(8,20,48,.92)" size={42} style={{ border: `4px solid ${YEL}` }}>o passado do verbo TO BE</Chip></Pop>
  </Cena>
);
const Conj: React.FC = () => (
  <Cena a={T.conj} b={T.rule}>
    <Pop at={T.conj + 0.05} y={290}><Chip bg={YEL} color={INK} size={46}>QUEM USA O QUÊ</Chip></Pop>
    {[["I", T.w1], ["he", T.w2], ["she", T.w3], ["it", T.w4]].map(([p, at], i) => <Pron key={p as string} p={p as string} v="was" c={C_A} at={at as number} y={460 + i * 150} dx={-230} />)}
    {[["you", T.r1], ["we", T.r2], ["they", T.r3]].map(([p, at], i) => <Pron key={p as string} p={p as string} v="were" c={C_THE} at={at as number} y={460 + i * 150} dx={230} />)}
  </Cena>
);
const Regra: React.FC = () => (
  <Cena a={T.rule} b={T.neg}>
    <Pop at={T.rule + 0.05} y={300}><Chip bg={C_AN} size={46}>PRESENTE → PASSADO</Chip></Pop>
    <Pop at={T.rWas} y={540}><Card w={860}><div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 24, ...W } as any}>
      <span>am · is</span><span style={{ color: YEL }}>→</span><Box c={C_A} size={100} tight>was</Box></div></Card></Pop>
    <Pop at={T.rWere} y={780}><Card w={860}><div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 24, ...W } as any}>
      <span>are</span><span style={{ color: YEL }}>→</span><Box c={C_THE} size={100} tight>were</Box></div></Card></Pop>
  </Cena>
);
const Neg: React.FC = () => (
  <Cena a={T.neg} b={T.q}>
    <Pop at={T.neg + 0.05} y={290}><Chip bg={RED} size={46}>NEGATIVA</Chip></Pop>
    <Pop at={T.n1} y={450}><div style={{ display: "flex", gap: 30, font: "400 120px Anton" }}><Box c={C_A} size={120}>wasn't</Box>{/* */}</div></Pop>
    <Pop at={T.n2} y={600}><div style={{ font: "400 120px Anton" }}><Box c={C_THE} size={120}>weren't</Box></div></Pop>
    <Pop at={T.n3} y={790}><Card w={860}><span style={{ ...W, fontSize: 80 } as any}><Emoji e="🏠" size={70} /> I <span style={{ color: YEL }}>wasn't</span> at home.</span></Card></Pop>
    <Pop at={T.n4} y={970}><Card w={860}><span style={{ ...W, fontSize: 80 } as any}><Emoji e="🏫" size={70} /> They <span style={{ color: YEL }}>weren't</span> at school.</span></Card></Pop>
  </Cena>
);
const Perg: React.FC = () => (
  <Cena a={T.q} b={T.quiz}>
    <Pop at={T.q + 0.05} y={300}><Chip bg={GREEN} size={46}>PERGUNTA: O VERBO VAI NA FRENTE</Chip></Pop>
    <Pop at={T.q1a} y={560}><Card w={860}><span style={{ ...W, fontSize: 92 } as any}><Box c={C_A} size={92} tight>Was</Box> she happy? <Emoji e="😊" size={80} /></span></Card></Pop>
    <Pop at={T.q2a} y={800}><Card w={860}><span style={{ ...W, fontSize: 92 } as any}><Box c={C_THE} size={92} tight>Were</Box> you tired? <Emoji e="😴" size={80} /></span></Card></Pop>
  </Cena>
);
const QUIZ: QuizItem[] = [
  { e: "🏖️", before: "I", answer: "was", opts: [["I were", false], ["I was", true]], tip: <>I → <b style={{ color: C_A }}>WAS</b> (Yesterday, I was at the beach)</> },
  { e: "🎉", before: "They", answer: "were", opts: [["They was", false], ["They were", true]], tip: <>they → <b style={{ color: C_THE }}>WERE</b></> },
];
export const WasWere: React.FC = () => (
  <Licao tm={TM} hl={{ WAS: C_A, WERE: C_THE, "WASN'T": C_A, "WEREN'T": C_THE }}>
    <Gancho /><Conj /><Regra /><Neg /><Perg /><Quiz items={QUIZ} /><Chamada />
  </Licao>
);

export const WasWereCapa: React.FC = () => (
  <CapaBase tm={TM} tt={4.5}>
    <Center y={260}><Chip bg={C_AN} size={40}>BÁSICO-INTERMEDIÁRIO · A2</Chip></Center>
    <Center y={450}><div style={{ display: "flex", gap: 26, font: "400 170px Anton" }}><Box c={C_A} size={170}>WAS</Box><Box c={C_THE} size={170}>WERE</Box></div></Center>
    <Center y={700}><Card w={820}><span style={{ font: "400 120px Anton", color: "#fff" }}>I WERE?</span></Card></Center>
    <Center y={850}><span style={{ font: "800 56px Montserrat", color: MUTED }}>ou</span></Center>
    <Center y={1000}><Card w={820}><span style={{ font: "400 120px Anton", color: "#fff" }}>I WAS?</span></Card></Center>
    <Center y={1210}><Chip bg={RED} size={46}>VOCÊ ERRA ESSA? · QUIZ</Chip></Center>
  </CapaBase>
);
