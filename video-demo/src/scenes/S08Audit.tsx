import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme, verdictColor } from "../theme";
import { CHAIN, CHAIN_TAMPERED_SEQ } from "../data";
import { Entrance, useProgress } from "../components/Motion";
import { Body, Headline, Kicker, PAD, Pill } from "../components/UI";

const TAMPER_AT = 190;
const BREAK_AT = 225;
const BW = 252;
const BGAP = 32;

export const S08Audit: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const brk = useProgress(BREAK_AT, 18);
  const ti = CHAIN.findIndex((c) => c.seq === CHAIN_TAMPERED_SEQ);
  return (
    <AbsoluteFill style={{ padding: `86px ${PAD}px`, justifyContent: "center" }}>
      <Kicker text="Audit tahan manipulasi" />
      <div style={{ height: 22 }} />
      <Headline text="Setiap vonis dirantai. Ubah satu entri, rantainya putus." size={64} width={1680} delay={6} />
      <div style={{ display: "flex", gap: BGAP, marginTop: 70, position: "relative" }}>
        {CHAIN.map((c, i) => {
          const tampered = c.seq === CHAIN_TAMPERED_SEQ && frame >= TAMPER_AT;
          const broken = i >= ti && frame >= BREAK_AT;
          const shake = c.seq === CHAIN_TAMPERED_SEQ && frame >= TAMPER_AT && frame < TAMPER_AT + 12
            ? Math.sin((frame - TAMPER_AT) * 2.4) * 8 * (1 - (frame - TAMPER_AT) / 12) : 0;
          const v = tampered ? "ACCEPT" : c.verdict;
          const pop = spring({ frame: frame - TAMPER_AT, fps, config: theme.spring.bouncy });
          const border = broken ? theme.colors.reject : theme.colors.line;
          return (
            <Entrance key={c.seq} delay={50 + i * 8} y={40}>
              <div style={{ position: "relative", transform: `translateX(${shake}px)` }}>
                {i > 0 && (
                  <div style={{
                    position: "absolute", left: -BGAP, top: 80, width: BGAP, height: 4,
                    background: i === ti && frame >= BREAK_AT ? "transparent" : (broken ? theme.colors.reject : theme.colors.textFaint),
                  }}>
                    {i === ti && frame >= BREAK_AT && (
                      <>
                        <div style={{ position: "absolute", left: 0, width: BGAP / 2 - 6, height: 4, background: theme.colors.reject, transform: `rotate(${brk * 18}deg)`, transformOrigin: "left" }} />
                        <div style={{ position: "absolute", right: 0, width: BGAP / 2 - 6, height: 4, background: theme.colors.reject, transform: `rotate(${-brk * 18}deg)`, transformOrigin: "right" }} />
                      </>
                    )}
                  </div>
                )}
                <div style={{
                  width: BW, padding: "22px 22px", borderRadius: 20, background: theme.colors.card,
                  border: `1.5px solid ${border}`, boxShadow: broken ? `0 0 30px ${theme.colors.reject}33` : "0 24px 48px -24px rgba(0,0,0,0.7)",
                }}>
                  <div style={{ fontFamily: theme.fonts.mono, fontSize: 20, color: theme.colors.textDim }}>seq {c.seq}</div>
                  <div style={{ margin: "14px 0", transform: tampered ? `scale(${interpolate(pop, [0, 1], [0.6, 1])})` : undefined, transformOrigin: "left center" }}>
                    <Pill text={v} color={verdictColor(v)} size={20} />
                  </div>
                  <div style={{ fontFamily: theme.fonts.mono, fontSize: 19, color: theme.colors.textFaint, whiteSpace: "nowrap" }}>token {c.token}…</div>
                </div>
              </div>
            </Entrance>
          );
        })}
      </div>
      <Entrance delay={110} y={12}>
        <div style={{ fontFamily: theme.fonts.mono, fontSize: 21, color: theme.colors.textDim, marginTop: 22 }}>
          token[n] = HMAC(K_tok, 0x02 ‖ vonis ‖ alasan ‖ seq ‖ tag[0:24] ‖ token[n−1])
        </div>
      </Entrance>
      <div style={{ marginTop: 44, display: "flex", flexDirection: "column", gap: 20 }}>
        <Entrance delay={TAMPER_AT - 6} y={20}>
          <div style={{ fontFamily: theme.fonts.body, fontSize: 30, color: theme.colors.text }}>
            Host mengubah entri <b>seq {CHAIN_TAMPERED_SEQ}</b> dari <span style={{ color: theme.colors.flag }}>FLAG</span> menjadi{" "}
            <span style={{ color: theme.colors.accept }}>ACCEPT</span> untuk menghapus jejak…
          </div>
        </Entrance>
        <Entrance delay={BREAK_AT + 20} y={20}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 22, padding: "18px 28px", borderRadius: 16,
            border: `1.5px solid ${theme.colors.reject}`, background: `${theme.colors.reject}14`,
          }}>
            <span style={{ fontFamily: theme.fonts.mono, fontSize: 24, color: theme.colors.textDim }}>verify_chain(K_tok) →</span>
            <span style={{ fontFamily: theme.fonts.mono, fontWeight: 700, fontSize: 26, color: theme.colors.reject }}>
              TERDETEKSI: rantai putus pada seq {CHAIN_TAMPERED_SEQ}
            </span>
          </div>
        </Entrance>
        <Body delay={BREAK_AT + 70} size={26}>
          Penghapusan entri dan penukaran urutan juga terdeteksi (diuji di simulasi RTL). Backend cukup memegang K_tok, bukan kunci master.
        </Body>
      </div>
    </AbsoluteFill>
  );
};
