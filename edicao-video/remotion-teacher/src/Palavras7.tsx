// Reel de 7 s do Teacher Eliezio: "7 palavras em inglês que todo mundo precisa saber" → "as 7 estão na legenda".
// O vídeo dele (public/v7.mp4, fica só na pasta de trabalho) vai por baixo; o texto fica na parte de baixo, longe do rosto e da zona do Instagram.
import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";
import { useT, useFonts, Pop, Emoji, Outline, YEL, clamp } from "./kit";

const Fade: React.FC<{ a: number; b: number; children: React.ReactNode }> = ({ a, b, children }) => {
  const { t } = useT(); const k = clamp((t - a) / 0.2) * clamp((b - t) / 0.25); if (k <= 0) return null;
  return <AbsoluteFill style={{ opacity: k }}>{children}</AbsoluteFill>;
};
const Base: React.FC<{ from: number; children: React.ReactNode }> = ({ from, children }) => {
  useFonts();
  return (<AbsoluteFill style={{ background: "#0a1a38" }}>
    <OffthreadVideo src={staticFile("v7.mp4")} startFrom={from} muted style={{ width: 1080, height: 1920, objectFit: "cover" }} />
    <div style={{ position: "absolute", left: 0, right: 0, top: 1020, bottom: 0, background: "linear-gradient(180deg, rgba(8,20,48,0) 0%, rgba(8,20,48,.78) 40%, rgba(8,20,48,.86) 100%)" }} />
    {children}
  </AbsoluteFill>);
};
const Bloco1: React.FC<{ at: number }> = ({ at }) => (<>
  <Pop at={at} y={1190} from={0.3}><div style={{ font: "400 150px Anton", color: YEL, ...Outline } as any}>7 PALAVRAS</div></Pop>
  <Pop at={at + 0.35} y={1300}><div style={{ font: "800 40px Montserrat", color: "#fff", textAlign: "center", width: 940, lineHeight: 1.2, ...Outline, WebkitTextStroke: "8px #0a1a38" } as any}>EM INGLÊS QUE TODO MUNDO PRECISA SABER</div></Pop>
</>);
const Bloco2: React.FC<{ at: number }> = ({ at }) => { const { t } = useT(); return (<>
  <Pop at={at} y={1440}><div style={{ font: "800 46px Montserrat", color: "#fff", ...Outline, WebkitTextStroke: "9px #0a1a38" } as any}>AS 7 ESTÃO NA</div></Pop>
  <Pop at={at + 0.15} y={1545} from={0.3}><div style={{ display: "flex", alignItems: "center", gap: 18 }}>
    <div style={{ font: "400 150px Anton", color: YEL, ...Outline } as any}>LEGENDA</div>
    <Emoji e="👇" size={84} style={{ transform: `translateY(${12 * Math.sin((t - at) * 7)}px)` }} /></div></Pop>
</>); };
export const Palavras7: React.FC = () => (
  <Base from={18}>
    <Fade a={0.2} b={99}><Bloco1 at={0.3} /></Fade>
    <Fade a={3.6} b={99}><Bloco2 at={3.7} /></Fade>
  </Base>
);
export const Palavras7Capa: React.FC = () => (
  <Base from={75}>
    <Bloco1 at={-3} /><Bloco2 at={-3} />
  </Base>
);
