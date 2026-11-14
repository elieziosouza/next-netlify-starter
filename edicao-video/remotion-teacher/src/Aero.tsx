// Série "Como se fala em inglês" · episódio 1: no aeroporto (14/11/2026). Tempos: timings/aero.json (scripts/prep_aula.py + aulas/aula_aero.py).
// Formato: frase em português na tela, ícone 3D, frase em inglês dita 2x (a 2ª é "repita comigo"). Sem quiz.
import React from "react";
import TM from "./timings/aero.json";
import { useT, usePop, Chip, Outline, Emoji, Center, Pop, Cena, Card, Chamada, Licao, CapaBase,
  INK, YEL, MUTED, RED, clamp } from "./kit";
import { Img, staticFile } from "remotion";
const T = TM.t as Record<string, number>;

/** ícone 3D flutuando devagar, com entrada em mola */
const Icone: React.FC<{ at: number; y: number; src: string; size?: number; over?: string }> = ({ at, y, src, size = 250, over }) => {
  const { t } = useT(); const p = usePop(at, { from: 0.3 }); if (!p.visible) return null;
  return (<div style={{ position: "absolute", left: 540, top: y, transform: "translate(-50%, -50%)" }}><div style={p.style}>
    <div style={{ position: "relative", transform: `translateY(${8 * Math.sin(t * 3)}px) rotate(${3 * Math.sin(t * 2)}deg)` }}>
      <Img src={staticFile(src)} style={{ width: size, height: size, objectFit: "contain", filter: "drop-shadow(0 14px 20px rgba(0,0,0,.45))" }} />
      {over && <div style={{ position: "absolute", right: -30, top: -26 }}><Emoji e={over} size={96} /></div>}
    </div></div></div>);
};

type FraseP = { n: number; a: number; b: number; p: number; r: number; pt: string; en: React.ReactNode; ic: string; over?: string; fs?: number };
const Frase: React.FC<FraseP> = ({ n, a, b, p, r, pt, en, ic, over, fs = 104 }) => {
  const { t } = useT(); const second = t >= r;
  return (
    <Cena a={a} b={b}>
      <Pop at={a + 0.1} y={290}><Chip bg={YEL} color={INK} size={40}>AEROPORTO · {n} de 4</Chip></Pop>
      <Pop at={a + 0.2} y={450}><Card w={920}><span style={{ font: "800 58px Montserrat", color: "#fff", textAlign: "center", display: "block" }}>{pt}</span></Card></Pop>
      <Icone at={a + 0.5} y={745} src={ic} over={over} />
      <Pop at={p} y={985} from={0.4}>
        <div style={{ font: `400 ${fs}px Anton`, color: second ? YEL : "#fff", textAlign: "center", width: 980, lineHeight: 1.08, transform: `scale(${second ? 1 + 0.03 * Math.sin((t - r) * 10) : 1})`, ...Outline } as any}>{en}</div>
      </Pop>
      <Pop at={r} y={1135}><Chip bg="rgba(8,20,48,.92)" size={42} style={{ border: `4px solid ${YEL}` }}>🔁 REPITA COMIGO</Chip></Pop>
    </Cena>
  );
};

const Abertura: React.FC = () => (
  <Cena a={0} b={T.p1 - 0.1}>
    <Pop at={0.1} y={300}><Chip bg={YEL} color={INK} size={40}>SÉRIE · EPISÓDIO 1</Chip></Pop>
    <Pop at={0.2} y={520} from={0.3}><div style={{ font: "400 150px Anton", color: "#fff", ...Outline } as any}>COMO SE FALA</div></Pop>
    <Pop at={0.81} y={700} from={0.3}><div style={{ font: "400 150px Anton", color: YEL, ...Outline } as any}>EM INGLÊS?</div></Pop>
    <Pop at={T.air} y={900}><Chip bg={RED} size={52}>NO AEROPORTO</Chip></Pop>
    <Icone at={T.air + 0.15} y={1050} src="ic/plane.png" size={300} />
  </Cena>
);

const FRASES: FraseP[] = [
  { n: 1, a: T.p1 - 0.1, b: T.p2 - 0.1, p: T.p1, r: T.r1, pt: "Onde fica o portão?", en: <>WHERE IS <span style={{ color: "#7fd0ff" }}>THE GATE</span>?</>, ic: "ic/ticket.png" },
  { n: 2, a: T.p2 - 0.1, b: T.p3 - 0.1, p: T.p2, r: T.r2, pt: "Meu voo foi cancelado", en: <>MY FLIGHT WAS <span style={{ color: "#7fd0ff" }}>CANCELED</span>.</>, ic: "ic/plane.png", over: "❌", fs: 88 },
  { n: 3, a: T.p3 - 0.1, b: T.p4 - 0.1, p: T.p3, r: T.r3, pt: "Posso despachar esta mala?", en: <>CAN I <span style={{ color: "#7fd0ff" }}>CHECK</span> THIS BAG?</>, ic: "ic/bag.png" },
  { n: 4, a: T.p4 - 0.1, b: T.cta, p: T.p4, r: T.r4, pt: "Perdi minha bagagem", en: <>I <span style={{ color: "#7fd0ff" }}>LOST</span> MY LUGGAGE.</>, ic: "ic/bag.png", over: "❓" },
];
export const Aero: React.FC = () => (
  <Licao tm={TM} hl={{}}>
    <Abertura />{FRASES.map((f) => <Frase key={f.n} {...f} />)}<Chamada titulo="SALVA!" pedido="MANDA PRA QUEM VAI VIAJAR" />
  </Licao>
);
export const AeroCapa: React.FC = () => (
  <CapaBase tm={TM} tt={4.5}>
    <Center y={270}><Chip bg={YEL} color={INK} size={40}>SÉRIE · EPISÓDIO 1</Chip></Center>
    <Center y={500}><div style={{ font: "400 150px Anton", color: "#fff", ...Outline } as any}>COMO SE FALA</div></Center>
    <Center y={690}><div style={{ font: "400 150px Anton", color: YEL, ...Outline } as any}>EM INGLÊS?</div></Center>
    <Center y={990}><Img src={staticFile("ic/plane.png")} style={{ width: 400, height: 400, objectFit: "contain", filter: "drop-shadow(0 16px 24px rgba(0,0,0,.45))" }} /></Center>
    <Center y={1270}><Chip bg={RED} size={52}>NO AEROPORTO</Chip></Center>
  </CapaBase>
);
