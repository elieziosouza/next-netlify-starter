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
    <div style={{ position: "absolute", left: 0, right: 0, top: 1130, bottom: 0, background: "linear-gradient(180deg, rgba(8,20,48,0) 0%, rgba(8,20,48,.78) 55%, rgba(8,20,48,.86) 100%)" }} />
    {children}
  </AbsoluteFill>);
};
export const Palavras7: React.FC = () => {
  const { t } = useT();
  return (
    <Base from={18}>
      <Fade a={0.2} b={3.5}>
        <Pop at={0.3} y={1370} from={0.3}><div style={{ font: "400 190px Anton", color: YEL, ...Outline } as any}>7 PALAVRAS</div></Pop>
        <Pop at={0.65} y={1545}><div style={{ font: "800 48px Montserrat", color: "#fff", textAlign: "center", width: 940, lineHeight: 1.2, ...Outline, WebkitTextStroke: "9px #0a1a38" } as any}>EM INGLÊS QUE TODO MUNDO PRECISA SABER</div></Pop>
      </Fade>
      <Fade a={3.6} b={7.2}>
        <Pop at={3.7} y={1345}><div style={{ font: "800 58px Montserrat", color: "#fff", ...Outline, WebkitTextStroke: "10px #0a1a38" } as any}>AS 7 ESTÃO NA</div></Pop>
        <Pop at={3.85} y={1475} from={0.3}><div style={{ font: "400 190px Anton", color: YEL, ...Outline } as any}>LEGENDA</div></Pop>
        <Pop at={4.2} y={1650}><Emoji e="👇" size={110} style={{ transform: `translateY(${14 * Math.sin((t - 4.2) * 7)}px)` }} /></Pop>
      </Fade>
    </Base>
  );
};
export const Palavras7Capa: React.FC = () => (
  <Base from={75}>
    <Pop at={0} y={1370}><div style={{ font: "400 190px Anton", color: YEL, ...Outline } as any}>7 PALAVRAS</div></Pop>
    <Pop at={0} y={1545}><div style={{ font: "800 48px Montserrat", color: "#fff", textAlign: "center", width: 940, lineHeight: 1.2, ...Outline, WebkitTextStroke: "9px #0a1a38" } as any}>EM INGLÊS QUE TODO MUNDO PRECISA SABER</div></Pop>
  </Base>
);
