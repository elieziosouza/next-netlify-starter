// Reel de 7 s do Teacher Eliezio: "7 palavras em inglês que todo mundo precisa saber" → "as 7 estão na legenda".
// Design: cartão azul-marinho com borda dourada na parte de baixo (longe do rosto e da zona do Instagram); os dois textos ficam juntos até o fim,
// com 7 bolinhas que acendem uma a uma (mesmo placar dos quizzes). O vídeo dele fica por baixo (public/v7.mp4, só na pasta de trabalho) com zoom bem leve.
import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile, Easing } from "remotion";
import { useT, useFonts, Emoji, Outline, YEL, INK, clamp } from "./kit";

const ease = (x: number) => Easing.out(Easing.cubic)(clamp(x));
const NAVY = "#0a1a38";

const Cartao: React.FC<{ t: number; fixo?: boolean }> = ({ t, fixo }) => {
  const k1 = fixo ? 1 : ease((t - 0.25) / 0.55);               // entrada do cartão e do bloco 1
  const kc = fixo ? 1 : ease((t - 3.45) / 0.4);                // o cartão cresce primeiro
  const k2 = fixo ? 1 : ease((t - 3.85) / 0.45);               // depois entram o aviso e as bolinhas
  const pulse = 1 + 0.025 * Math.sin((t - 3.85) * 6);
  const dots = Array.from({ length: 7 }, (_, i) => (fixo ? 1 : ease((t - (4.35 + i * 0.36)) / 0.2)));
  return (
    <div style={{ position: "absolute", left: 60, top: 1170, width: 960, height: 250 + 190 * kc, opacity: k1, transform: `translateY(${(1 - k1) * 60}px)` }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: 48, background: "linear-gradient(160deg, rgba(25,66,140,.94) 0%, rgba(10,26,56,.96) 70%)", border: "3px solid rgba(255,214,64,.7)", boxShadow: "0 24px 60px rgba(0,0,0,.45), 0 0 50px rgba(255,214,64,.18)" }} />
      {/* bloco 1: 7 + PALAVRAS EM INGLÊS */}
      <div style={{ position: "absolute", left: 36, top: 34, display: "flex", alignItems: "center", gap: 30 }}>
        <div style={{ width: 176, height: 176, borderRadius: 40, background: YEL, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 8px 0 rgba(0,0,0,.28)" }}>
          <span style={{ font: "400 190px Anton", color: INK, lineHeight: 1, marginTop: 6 }}>7</span></div>
        <div style={{ display: "grid", gap: 4 }}>
          <span style={{ font: "400 84px Anton", color: "#fff", lineHeight: 1.0, letterSpacing: 1.5, whiteSpace: "nowrap" }}>PALAVRAS EM INGLÊS</span>
          <span style={{ font: "800 34px Montserrat", color: YEL, lineHeight: 1.15, letterSpacing: 0.6, whiteSpace: "nowrap" }}>QUE TODO MUNDO PRECISA SABER</span>
        </div>
      </div>
      {/* bloco 2: divisor, aviso e bolinhas */}
      <div style={{ position: "absolute", left: 36, right: 36, top: 238, height: 3, background: "rgba(255,214,64,.4)", transform: `scaleX(${k2})`, transformOrigin: "left" }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 268, display: "flex", justifyContent: "center", opacity: k2, transform: `translateY(${(1 - k2) * 26}px) scale(${pulse})` }}>
        <div style={{ background: YEL, color: INK, borderRadius: 999, padding: "10px 46px 10px 52px", display: "flex", alignItems: "center", gap: 18, boxShadow: "0 8px 0 rgba(0,0,0,.28), 0 0 40px rgba(255,214,64,.35)" }}>
          <span style={{ font: "900 50px Montserrat", letterSpacing: 0.8 }}>AS 7 ESTÃO NA LEGENDA</span>
          <Emoji e="👇" size={62} style={{ transform: `translateY(${10 * Math.sin((t - 3.85) * 7)}px)` }} />
        </div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 388, display: "flex", justifyContent: "center", gap: 16, opacity: k2 }}>
        {dots.map((d, i) => <div key={i} style={{ width: 26, height: 26, borderRadius: "50%", background: d > 0.5 ? YEL : "rgba(255,255,255,.16)", border: `3px solid ${d > 0.5 ? YEL : "rgba(255,255,255,.3)"}`, transform: `scale(${0.9 + 0.3 * d})` }} />)}
      </div>
    </div>
  );
};
const Base: React.FC<{ from: number; zoom?: boolean; children: (t: number) => React.ReactNode }> = ({ from, zoom = true, children }) => {
  useFonts(); const { t } = useT();
  return (<AbsoluteFill style={{ background: NAVY }}>
    <AbsoluteFill style={{ transform: `scale(${zoom ? 1 + 0.045 * clamp(t / 7) : 1})`, transformOrigin: "50% 14%" }}>
      <OffthreadVideo src={staticFile("v7.mp4")} startFrom={from} muted style={{ width: 1080, height: 1920, objectFit: "cover" }} />
    </AbsoluteFill>
    <div style={{ position: "absolute", left: 0, right: 0, top: 960, bottom: 0, background: "linear-gradient(180deg, rgba(8,20,48,0) 0%, rgba(8,20,48,.5) 60%, rgba(8,20,48,.7) 100%)" }} />
    {children(t)}
  </AbsoluteFill>);
};
export const Palavras7: React.FC = () => <Base from={18}>{(t) => <Cartao t={t} />}</Base>;
export const Palavras7Capa: React.FC = () => <Base from={75} zoom={false}>{(t) => <Cartao t={t} fixo />}</Base>;
