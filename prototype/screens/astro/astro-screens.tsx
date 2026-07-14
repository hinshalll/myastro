// astro-screens.tsx — Chat with the Moon, Diyas wallet, Decode (Readings) hub, tab
// placeholders, the detail sheets (eclipse / ritual / journal / full timing), and the
// AstroApp container that wires navigation + shared balance. ASTROLO-clean language throughout.
;(function () {
const U = (window as any).__astroUI;
const T = (window as any).__astroToday;
const P = (window as any).__astroPlan;
const { useState, useRef, useEffect, aA, PAPER, WASH, INK, INK2, GRAY, HAIR, ORANGE, SANS, SERIF, MONO,
  pill, card, Label, Icon, Flame, GlossIcon, Press, MoodEmblem, MoonGloss, Ganesha, Sheet, MOOD, CYCLE, ECL, MIR, NAME, DATE, DAY_LINE, rise } = U;
const { TopCluster, LivingSkyHeader, MoonFAB, SubTabs, EclipseCard, ReadingCard, LifeAreas, CheckInSheet, CheckInChip, RitualPill, JournalCard, BottomNav } = T;
const { PlanTab, MonthScreen, MuhuratSheet, CalendarDoctorSheet, AskMomentSheet, TimeCapsuleSheet, WhySheet } = P;

// a plain back-button header used by the sub-screens (Chat, Wallet)
function BackBar({ onBack, chip, bal, mood, onWallet }: any) {
  const { accent, accentDeep, glow } = mood;
  return (
    <div style={{ position: "absolute", top: 52, left: 18, right: 18, zIndex: 10, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
      <Press scale={0.9} onClick={onBack}><div style={{ ...pill(999), width: 42, height: 42, display: "flex", alignItems: "center", justifyContent: "center" }}><Icon n="arrowL" s={19} c={INK} /></div></Press>
      {chip && <Press scale={0.94} onClick={onWallet}><div style={{ ...pill(999), padding: "9px 14px", display: "flex", alignItems: "center", gap: 6 }}><Flame s={15} c={glow} /><span style={{ fontFamily: SANS, fontWeight: 800, fontSize: 15, color: INK }}>{bal}</span></div></Press>}
    </div>
  );
}

// ===================== CHAT WITH THE MOON =====================
// A living, proactive conversation. The Moon opens with one of three warm, specific
// openers (a pattern it noticed · a look-back · a gentle nudge), the input really works
// (contextual warm replies + a typing beat), and hard moments get a gentle, safe reply.
const MOON_OPENERS = [
  { kind: "a pattern I noticed", lines: [`Hey ${NAME}. I've been noticing something — you tend to feel lighter on the days you write to me in the morning. Today's a soft one, so maybe start there?`], chips: ["Tell me more", "Maybe later"] },
  { kind: "looking back", lines: [`Hi ${NAME}. A week ago you were dreading that conversation at work. I've been wondering — how did it land?`], chips: ["It went okay", "Still on my mind"] },
  { kind: "just checking in", lines: [`Hey ${NAME}. It's been a couple of quiet days. No agenda, I just wanted you to know I'm here. How are you, really?`], chips: ["I'm alright", "Not my best"] },
];
const REPLY = {
  low: ["That sounds heavy, and I'm glad you told me. You don't have to carry today all at once — just the next hour.", "I hear you. With your Moon where it is right now, these days ask more of you than usual. Go slow, it's allowed.", "Thank you for being honest with me. Let's keep today small and kind. What would feel like a little relief?"],
  high: ["I love hearing that. Hold onto this one — days like this are worth remembering.", "That makes me happy. The sky's with you today, so let it carry you a little further.", "Beautiful. Let yourself enjoy it fully, no guilt attached."],
  ask: ["With the day this tender, I'd wait until late morning — things land softer then.", "It's a mixed moment. You can move ahead, just gently and without forcing it.", "The timing's a little rushed right now. Give it an hour and it eases."],
  warm: ["I'm here. Tell me more whenever you're ready.", "That tracks with how the day's moving. What's underneath it, do you think?", "Mm. Sit with that for a second — I'm not going anywhere.", "I understand. Want to just talk it through, no fixing?"],
};
const DISTRESS = ["kill myself", "end it", "suicide", "don't want to be here", "dont want to be here", "hurt myself", "no reason to live", "can't go on", "cant go on", "want to die", "worthless"];
function pickReply(text: string, i: number) {
  const t = text.toLowerCase();
  if (DISTRESS.some((w) => t.includes(w))) return { safe: true, t: "I'm really glad you told me, and I don't want you to be alone with this. Please reach out to someone who can sit with you right now — in India you can call KIRAN at 1800-599-0019, any time, free. I'm here too, and I'm not going anywhere." };
  if (/\b(low|tired|heavy|sad|down|anxious|stressed|awful|exhausted|lonely|hurt)\b/.test(t)) return { t: REPLY.low[i % REPLY.low.length] };
  if (/\b(good|great|happy|excited|wonderful|amazing|better|grateful|calm)\b/.test(t)) return { t: REPLY.high[i % REPLY.high.length] };
  if (t.includes("?") || /^should i|^is it|^can i|^will /.test(t)) return { t: REPLY.ask[i % REPLY.ask.length] };
  return { t: REPLY.warm[i % REPLY.warm.length] };
}
function ChatScreen({ mood, seed, opener = 0, onBack }: any) {
  const { accent, accentDeep, glow } = mood;
  const op = MOON_OPENERS[opener % MOON_OPENERS.length];
  const seedMsgs = seed ? [{ me: true, t: seed }, { me: false, t: "Good question to bring me. With the day this tender, I'd wait until late morning — the words will land softer then." }] : [];
  const [msgs, setMsgs] = useState<any[]>([
    { me: false, t: op.lines[0], kind: op.kind },
    ...seedMsgs,
  ]);
  const [chips, setChips] = useState<string[]>(seed ? [] : op.chips);
  const [draft, setDraft] = useState("");
  const [typing, setTyping] = useState(false);
  const [listening, setListening] = useState(false);
  const scrollRef = useRef<any>(null);
  const cnt = useRef(0);
  const userSpoke = msgs.some((m: any) => m.me);
  // three-state companion: idle before you speak, thinking while replying, delivered after
  const sageImg = typing ? "chatsage2.png" : (userSpoke ? "chatsage3.png" : "chatsage1.png");
  useEffect(() => { const el = scrollRef.current; if (el) el.scrollTop = el.scrollHeight; }, [msgs, typing]);

  const send = (raw: string) => {
    const text = raw.trim(); if (!text || typing) return;
    setChips([]); setDraft(""); setListening(false);
    setMsgs((m: any[]) => [...m, { me: true, t: text }]);
    setTyping(true);
    const r = pickReply(text, cnt.current++);
    setTimeout(() => { setTyping(false); setMsgs((m: any[]) => [...m, { me: false, t: r.t, safe: r.safe }]); }, 950 + Math.min(text.length * 12, 700));
  };

  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER, display: "flex", flexDirection: "column" }}>
      {/* glowing phase-moon header */}
      <div style={{ paddingTop: 40, paddingBottom: 11, display: "flex", flexDirection: "column", alignItems: "center", borderBottom: `1px solid ${HAIR}`, background: `radial-gradient(120% 90% at 50% -10%, ${aA(glow, 0.16)}, ${aA(glow, 0)} 70%)` }}>
        <Press scale={0.9} onClick={onBack} style={{ position: "absolute", left: 18, top: 48 }}><div style={{ ...pill(999), width: 42, height: 42, display: "flex", alignItems: "center", justifyContent: "center" }}><Icon n="arrowL" s={19} c={INK} /></div></Press>
        <div style={{ position: "relative", width: 92, height: 92, display: "flex", alignItems: "center", justifyContent: "center" }}>
          {/* soft aura */}
          <div style={{ position: "absolute", inset: 8, borderRadius: 999, background: `radial-gradient(circle at 50% 46%, ${aA(glow, 0.4)}, ${aA(glow, 0)} 66%)`, animation: "haloBreathe 5s ease-in-out infinite" }} />
          {/* the sage with the crystal ball */}
          <div style={{ position: "relative", width: 86, height: 87, animation: "floatY 6s ease-in-out infinite" }}>
            {["chatsage1.png", "chatsage2.png", "chatsage3.png"].map((src) => (
              <img key={src} src={src} alt="" draggable={false} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "contain", filter: `drop-shadow(0 6px 12px ${aA("#1A1408", 0.22)})`, opacity: src === sageImg ? 1 : 0, transition: "opacity .18s ease" }} />
            ))}
          </div>
        </div>
        <div style={{ fontFamily: SERIF, fontSize: 18, fontWeight: 500, color: INK, marginTop: 3 }}>Sage</div>
        <div style={{ fontFamily: SANS, fontSize: 12, color: GRAY, marginTop: 1 }}>your guide · always private</div>
      </div>
      {/* conversation */}
      <div ref={scrollRef} style={{ flex: 1, overflowY: "auto", padding: "18px 18px 8px", display: "flex", flexDirection: "column", gap: 11, scrollBehavior: "smooth" }}>
        {msgs.map((m: any, i: number) => (
          <div key={i} style={{ alignSelf: m.me ? "flex-end" : "flex-start", maxWidth: "83%", animation: `riseIn .45s ease both` }}>
            {m.kind && <div style={{ fontFamily: MONO, fontSize: 9.5, letterSpacing: 1, textTransform: "uppercase", color: aA(accentDeep, 0.85), marginBottom: 5, marginLeft: 4, display: "flex", alignItems: "center", gap: 5 }}><span style={{ width: 4, height: 4, borderRadius: 999, background: glow, boxShadow: `0 0 5px ${glow}` }} />{m.kind}</div>}
            <div style={m.me
              ? { background: INK, color: "#FFF", borderRadius: "20px 20px 6px 20px", padding: "11px 15px", fontFamily: SANS, fontSize: 14.5, lineHeight: 1.45, fontWeight: 500 }
              : m.safe
                ? { background: aA(accent, 0.08), border: `1px solid ${aA(accent, 0.3)}`, borderRadius: "20px 20px 20px 6px", padding: "13px 16px", color: INK, fontFamily: SERIF, fontSize: 15.5, lineHeight: 1.5 }
                : { ...pill(20), borderRadius: "20px 20px 20px 6px", padding: "12px 16px", color: INK, fontFamily: SERIF, fontSize: 15.5, lineHeight: 1.45 }}>{m.t}</div>
          </div>
        ))}
        {typing && (<div style={{ alignSelf: "flex-start", ...pill(20), borderRadius: "20px 20px 20px 6px", padding: "13px 17px", display: "flex", gap: 5, animation: "riseIn .3s ease both" }}>
          {[0, 1, 2].map((d) => (<div key={d} style={{ width: 6, height: 6, borderRadius: 999, background: aA(INK, 0.4), animation: `blink 1.2s ease-in-out ${d * 0.18}s infinite` }} />))}
        </div>)}
        {chips.length > 0 && !typing && (<div style={{ alignSelf: "flex-start", display: "flex", gap: 8, marginTop: 2, flexWrap: "wrap", animation: "riseIn .5s ease .2s both" }}>
          {chips.map((c) => (<Press key={c} scale={0.95} onClick={() => send(c)}><div style={{ padding: "8px 14px", borderRadius: 999, background: "#FFF", border: `1px solid ${aA(accentDeep, 0.3)}`, fontFamily: SANS, fontSize: 13, fontWeight: 700, color: accentDeep }}>{c}</div></Press>))}
        </div>)}
      </div>
      {/* input */}
      <div style={{ padding: "6px 16px 26px" }}>
        {listening && (<div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, marginBottom: 9, animation: "fadeIn .3s ease both" }}>
          {[0, 1, 2, 3, 4].map((b) => (<div key={b} style={{ width: 3, borderRadius: 999, background: accentDeep, height: 8 + (b % 3) * 7, animation: `sound 0.9s ease-in-out ${b * 0.12}s infinite` }} />))}
          <span style={{ fontFamily: SANS, fontSize: 12, color: accentDeep, fontStyle: "italic", marginLeft: 4 }}>listening…</span>
        </div>)}
        <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "5px 6px 5px 16px", ...pill(999) }}>
          <input value={draft} onChange={(e: any) => setDraft(e.target.value)} onKeyDown={(e: any) => { if (e.key === "Enter") send(draft); }} placeholder="Tell Sage…" style={{ flex: 1, border: "none", outline: "none", background: "transparent", fontFamily: SANS, fontSize: 14.5, color: INK, padding: "9px 0" }} />
          <Press scale={0.9} onClick={() => setListening((v) => !v)}><div style={{ width: 38, height: 38, borderRadius: 999, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", background: listening ? accentDeep : aA(accent, 0.12) }}><Icon n="mic" s={18} c={listening ? "#FFF" : accentDeep} sw={1.8} /></div></Press>
          <Press scale={0.9} onClick={() => send(draft)}><div style={{ width: 38, height: 38, borderRadius: 999, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", background: draft.trim() ? INK : aA(INK, 0.35) }}><Icon n="send" s={17} c="#FFF" sw={1.8} /></div></Press>
        </div>
      </div>
    </div>
  );
}

// ===================== DIYAS WALLET =====================
function WalletScreen({ mood, bal, onBack }: any) {
  const { accent, accentDeep, glow } = mood;
  const bright = Math.min(1, 0.4 + bal / 500);
  const earn = [["Daily check-in", "+1", true], ["Today's ritual", "+2", false], ["A journal note", "+1", false], ["7-day streak", "+10", false], ["Invite a friend", "+25", false]];
  const buy = [["Glow", "₹99", "110", false], ["Blaze", "₹299", "380", true], ["Festival", "₹799", "1,150", false]];
  const hist = [["Today's ritual", "+2"], ["Daily check-in", "+1"], ["Full Life Reading", "−60"], ["7-day streak", "+10"], ["Compatibility unlock", "−30"]];
  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER, overflowY: "auto" }}>
      <BackBar onBack={onBack} mood={mood} />
      <div style={{ padding: "104px 18px 40px" }}>
        {/* hero */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginBottom: 24, ...rise(0) }}>
          <div style={{ position: "relative", width: 92, height: 92, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ position: "absolute", inset: -14, borderRadius: 999, "--gc": aA(glow, 0.3 + bright * 0.4), animation: "glowPulse 4s ease-in-out infinite" } as any} />
            <div style={{ animation: "floatY 5s ease-in-out infinite" }}><Flame s={64} c={glow} /></div>
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 8 }}><span style={{ fontFamily: SERIF, fontSize: 52, fontWeight: 600, color: INK, letterSpacing: -1.5 }}>{bal}</span><span style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 22, color: accentDeep }}>🪔 lit</span></div>
        </div>
        {/* earn */}
        <div style={{ ...card({ padding: "16px 18px", marginBottom: 14 }), ...rise(80) }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}><Label c={aA(accentDeep, 0.9)}>Light a diya by doing good</Label><span style={{ fontFamily: SANS, fontSize: 11, fontWeight: 700, color: GRAY }}>3 of 5 today</span></div>
          {earn.map(([l, amt, done]: any, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: "11px 0", borderTop: i ? `1px solid ${HAIR}` : "none" }}>
              <div style={{ width: 26, height: 26, borderRadius: 999, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", background: done ? aA(accent, 0.14) : WASH, border: `1px solid ${done ? aA(accent, 0.3) : HAIR}` }}>{done ? <Icon n="check" s={13} c={accentDeep} sw={2.4} /> : <Flame s={12} c={glow} />}</div>
              <span style={{ flex: 1, fontFamily: SANS, fontSize: 14, fontWeight: 600, color: done ? GRAY : INK, textDecoration: done ? "line-through" : "none" }}>{l}</span>
              <span style={{ fontFamily: MONO, fontSize: 12.5, fontWeight: 600, color: done ? GRAY : accentDeep }}>{amt}</span>
            </div>
          ))}
        </div>
        {/* buy */}
        <div style={{ marginBottom: 14, ...rise(140) }}>
          <div style={{ paddingLeft: 4, marginBottom: 9 }}><Label>Buy diyas</Label></div>
          <div style={{ display: "flex", gap: 10 }}>
            {buy.map(([n, p, coins, best]: any) => (
              <div key={n} style={{ flex: 1, position: "relative", ...pill(18), padding: "16px 8px", display: "flex", flexDirection: "column", alignItems: "center", gap: 6, border: `1px solid ${best ? aA(accent, 0.5) : aA("#000", 0.05)}` }}>
                {best && <div style={{ position: "absolute", top: -8, left: "50%", transform: "translateX(-50%)", whiteSpace: "nowrap", padding: "2px 8px", borderRadius: 999, background: accentDeep }}><span style={{ fontFamily: MONO, fontSize: 8, fontWeight: 600, letterSpacing: 0.5, textTransform: "uppercase", color: "#FFF" }}>best value</span></div>}
                <Flame s={20} c={glow} /><span style={{ fontFamily: SANS, fontSize: 14, fontWeight: 800, color: INK }}>{n}</span>
                <span style={{ fontFamily: SERIF, fontSize: 17, fontWeight: 600, color: INK }}>{coins}🪔</span>
                <div style={{ marginTop: 2, padding: "6px 0", width: "100%", borderRadius: 10, background: INK, textAlign: "center" }}><span style={{ fontFamily: SANS, fontSize: 12, fontWeight: 700, color: "#FFF" }}>{p}</span></div>
              </div>
            ))}
          </div>
        </div>
        {/* go plus — dark glossy */}
        <div style={{ borderRadius: 22, overflow: "hidden", position: "relative", background: `linear-gradient(155deg, #211B12, #0C0B0A)`, padding: "20px 20px 18px", marginBottom: 14, boxShadow: `0 18px 40px -20px ${aA("#000", 0.6)}`, ...rise(200) }}>
          <div style={{ position: "absolute", top: -40, right: -30, width: 160, height: 160, borderRadius: 999, background: `radial-gradient(circle, ${aA(glow, 0.4)}, ${aA(glow, 0)} 70%)` }} />
          <Label c={glow}>ASTROLO Plus</Label>
          <div style={{ fontFamily: SERIF, fontSize: 21, fontWeight: 500, color: "#FBF4E8", marginTop: 9, lineHeight: 1.3 }}>Unlimited chat, every Pattern, 25% off everything.</div>
          <div style={{ fontFamily: SANS, fontSize: 12.5, color: aA("#FBF4E8", 0.6), marginTop: 8 }}>couple, family & deep Patterns · cross-reference free</div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 16 }}>
            <div style={{ display: "flex", alignItems: "baseline", gap: 5 }}><span style={{ fontFamily: SERIF, fontSize: 24, fontWeight: 600, color: "#FBF4E8" }}>₹199</span><span style={{ fontFamily: SANS, fontSize: 11, color: aA("#FBF4E8", 0.5) }}>/mo</span></div>
            <Press scale={0.95}><div style={{ padding: "10px 16px", borderRadius: 999, background: glow }}><span style={{ fontFamily: SANS, fontSize: 13, fontWeight: 800, color: "#211B12" }}>7-day free trial</span></div></Press>
          </div>
        </div>
        {/* history */}
        <div style={{ ...card({ padding: "16px 18px" }), ...rise(260) }}>
          <div style={{ marginBottom: 4 }}><Label>History</Label></div>
          {hist.map(([w, amt]: any, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "11px 0", borderTop: i ? `1px solid ${HAIR}` : "none" }}>
              <span style={{ flex: 1, fontFamily: SANS, fontSize: 14, fontWeight: 600, color: INK }}>{w}</span>
              <span style={{ fontFamily: MONO, fontSize: 13, fontWeight: 600, color: (amt[0] === "+") ? accentDeep : GRAY }}>{amt}</span>
              <Flame s={12} c={(amt[0] === "+") ? glow : GRAY} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ===================== DECODE (Readings hub) =====================
const RASHI_GLYPH: any = { Cancer: "♋", Libra: "♎", Aries: "♈", Taurus: "♉", Gemini: "♊", Leo: "♌", Virgo: "♍", Scorpio: "♏", Sagittarius: "♐", Capricorn: "♑", Aquarius: "♒", Pisces: "♓" };
function DecodeScreen({ mood, bal, onWallet, onProfile, onBell }: any) {
  const { accent, accentDeep, glow } = mood;
  const Section = ({ children }: any) => (<div style={{ margin: "26px 2px 11px" }}><Label>{children}</Label></div>);
  const Row = ({ glyph, title, sub, price }: any) => (
    <Press scale={0.985} style={{ marginBottom: 10 }}>
      <div style={{ ...pill(18), padding: "13px 15px", display: "flex", alignItems: "center", gap: 13 }}>
        <GlossIcon c1={glow} c2={accentDeep} size={42} radius={13}><span style={{ fontSize: 19, color: "#FFF" }}>{glyph}</span></GlossIcon>
        <div style={{ flex: 1 }}><div style={{ fontFamily: SERIF, fontSize: 16.5, fontWeight: 500, color: INK }}>{title}</div><div style={{ fontFamily: SANS, fontSize: 12, color: GRAY, marginTop: 1 }}>{sub}</div></div>
        {price ? (<div style={{ display: "flex", alignItems: "center", gap: 3, padding: "5px 10px", borderRadius: 999, background: aA(accent, 0.1), border: `1px solid ${aA(accent, 0.24)}` }}><Flame s={11} c={glow} /><span style={{ fontFamily: MONO, fontSize: 11.5, fontWeight: 600, color: accentDeep }}>{price}</span></div>) : <Icon n="chevR" s={16} c={GRAY} />}
      </div>
    </Press>
  );
  const tools = [["✦", "Numerology", "your numbers", "#7B7FD0", "#5C60AE"], ["☍", "Palmistry", "read your palm", "#2E9C7E", "#1F7660"], ["◑", "Face Reading", "read your face", "#D06A8C", "#AC4E6E"], ["✷", "Tarot", "pull a card", "#E0982A", "#B5781A"]];
  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER, overflowY: "auto" }}>
      <div style={{ position: "absolute", top: 52, left: 18, right: 18, zIndex: 10 }}><TopCluster mood={mood} bal={bal} bump={0} alert={true} onProfile={onProfile} onWallet={onWallet} onBell={onBell} /></div>
      <div style={{ padding: "108px 18px 130px" }}>
        <div style={rise(0)}>
          <Label c={aA(accentDeep, 0.9)}>Readings & Tools</Label>
          <div style={{ fontFamily: SERIF, fontSize: 32, fontWeight: 500, color: INK, letterSpacing: -0.8, marginTop: 3 }}>Decode</div>
          <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 15, color: GRAY, marginTop: 4 }}>Everything your chart can tell you, in one place.</div>
        </div>
        {/* kundli anchor */}
        <div style={{ ...card({ padding: 20, marginTop: 18 }), ...rise(80) }}>
          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
            <div style={{ width: 72, height: 72, borderRadius: 999, flexShrink: 0, position: "relative", overflow: "hidden", background: `linear-gradient(155deg, ${glow}, ${accent} 55%, ${accentDeep})`, boxShadow: `inset 0 1px 2px ${aA("#FFF", 0.5)}, 0 8px 20px -6px ${aA(accentDeep, 0.6)}`, display: "flex", alignItems: "center", justifyContent: "center", animation: "floatY 5s ease-in-out infinite" }}>
              <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "46%", background: `linear-gradient(180deg, ${aA("#FFF", 0.4)}, ${aA("#FFF", 0)})` }} />
              <span style={{ fontSize: 34, color: "#FFFDF8", lineHeight: 1 }}>{RASHI_GLYPH.Cancer}</span>
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <Label c={aA(accentDeep, 0.9)}>Your kundli</Label>
              <div style={{ fontFamily: SERIF, fontSize: 21, fontWeight: 500, color: INK, marginTop: 3 }}>{NAME}</div>
              <div style={{ fontFamily: SANS, fontSize: 12, color: GRAY, marginTop: 2 }}>14 Aug 1998 · 4:20 am · Jaipur</div>
              <Press scale={0.96} style={{ display: "inline-block", marginTop: 11 }}><div style={{ display: "flex", alignItems: "center", gap: 6 }}><span style={{ fontFamily: SANS, fontSize: 12.5, fontWeight: 700, color: accentDeep }}>Open full chart</span><Icon n="arrowR" s={13} c={accentDeep} sw={2} /></div></Press>
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 16, paddingTop: 15, borderTop: `1px solid ${HAIR}` }}>
            {[["Lagna", "Libra", "ascendant"], ["Rashi", "Cancer", "moon sign"], ["Nakshatra", "Pushya", "birth star"]].map(([k, v, sub]) => (
              <div key={k} style={{ flex: 1, textAlign: "center" }}>
                <div style={{ fontFamily: MONO, fontSize: 8.5, fontWeight: 600, letterSpacing: 0.6, textTransform: "uppercase", color: accentDeep }}>{k}</div>
                <div style={{ fontFamily: SERIF, fontSize: 16.5, fontWeight: 500, color: INK, marginTop: 3 }}>{v}</div>
                <div style={{ fontFamily: SANS, fontSize: 9.5, color: GRAY, marginTop: 1 }}>{sub}</div>
              </div>
            ))}
          </div>
        </div>
        <Section>In-depth readings</Section>
        <Row glyph="✦" title="Full Life Reading" sub="your whole chart, read in depth" price="60" />
        <Row glyph="❤" title="Marriage Reading" sub="love, timing, and the person" price="60" />
        <Row glyph="✶" title="Career & Purpose" sub="where your work wants to go" price="45" />
        <Section>Matching & timing</Section>
        <Row glyph="⚯" title="Kundli Matching" sub="check two charts together" />
        <Row glyph="☼" title="Auspicious Days" sub="find a good day to begin" />
        <Section>Explore yourself</Section>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
          {tools.map(([g, t, sub, c1, c2]: any) => (
            <Press key={t} scale={0.97} style={{ width: "calc(50% - 5px)" }}>
              <div style={{ ...pill(18), padding: 16, boxSizing: "border-box" }}>
                <GlossIcon c1={c1} c2={c2} size={38} radius={12}><span style={{ fontSize: 18, color: "#FFF" }}>{g}</span></GlossIcon>
                <div style={{ fontFamily: SERIF, fontSize: 16, fontWeight: 500, color: INK, marginTop: 11 }}>{t}</div>
                <div style={{ fontFamily: SANS, fontSize: 11.5, color: GRAY, marginTop: 1 }}>{sub}</div>
              </div>
            </Press>
          ))}
        </div>
        <div style={{ textAlign: "center", fontFamily: SERIF, fontStyle: "italic", fontSize: 13.5, color: GRAY, marginTop: 16 }}>Try each once for free, then they cost a few Diyas.</div>
      </div>
    </div>
  );
}

// ===================== tab placeholder =====================
function Placeholder({ mood, label, bal, onProfile, onWallet, onBell }: any) {
  const { accent, accentDeep, glow } = mood;
  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER }}>
      <div style={{ position: "absolute", top: 52, left: 18, right: 18, zIndex: 10 }}><TopCluster mood={mood} bal={bal} bump={0} alert={true} onProfile={onProfile} onWallet={onWallet} onBell={onBell} /></div>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 14 }}>
        <MoodEmblem mood={mood} size={64} />
        <div style={{ fontFamily: SERIF, fontSize: 26, fontWeight: 500, color: INK }}>{label}</div>
        <div style={{ fontFamily: SANS, fontSize: 14, color: GRAY }}>coming soon</div>
      </div>
    </div>
  );
}

// ===================== detail sheets =====================
function EclipseSheet({ mood, type }: any) {
  const { accentDeep } = mood;
  const t = type || ECL.type;
  const sanskrit = t === "solar" ? "सूर्य ग्रहण" : "चन्द्र ग्रहण";
  return (<div>
    <Label c={aA(accentDeep, 0.9)}>Heads up</Label>
    <div style={{ fontFamily: SERIF, fontSize: 24, fontWeight: 500, color: INK, marginTop: 6 }}>A {t} eclipse on {ECL.date}</div>
    <div style={{ fontFamily: SERIF, fontSize: 16, lineHeight: 1.5, color: INK2, marginTop: 12, textWrap: "pretty" } as any}>{ECL.full ? ECL.full[t] : ""}</div>
    <div style={{ marginTop: 16, padding: 15, borderRadius: 14, background: WASH }}><Label>Caution window</Label><div style={{ fontFamily: SANS, fontSize: 13.5, lineHeight: 1.5, color: INK2, marginTop: 6 }}>The Sutak window begins about {ECL.sutakHours} hours before, around {ECL.sutakDate}, {ECL.sutakTime}.</div></div>
    <div style={{ textAlign: "center", marginTop: 14, fontFamily: SERIF, fontSize: 16, color: GRAY }}>{sanskrit}</div>
  </div>);
}
function RitualSheet({ mood, onDone }: any) {
  const { accent, accentDeep } = mood;
  const steps = ["Find a small lamp or candle as the light fades.", "Light it, and sit for a moment.", "Breathe slowly for one minute, eyes soft.", "When you're ready, let the day go."];
  return (<div>
    <Label c={aA(accentDeep, 0.9)}>Today's ritual</Label>
    <div style={{ fontFamily: SERIF, fontSize: 22, fontWeight: 500, color: INK, marginTop: 6 }}>Light a lamp at dusk</div>
    <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 16 }}>
      {steps.map((s, i) => (<div key={i} style={{ display: "flex", gap: 12, alignItems: "flex-start" }}><div style={{ width: 24, height: 24, flexShrink: 0, borderRadius: 999, background: aA(accent, 0.12), border: `1px solid ${aA(accent, 0.3)}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: MONO, fontSize: 11, fontWeight: 600, color: accentDeep }}>{i + 1}</div><span style={{ fontFamily: SERIF, fontSize: 15.5, lineHeight: 1.45, color: INK }}>{s}</span></div>))}
    </div>
    <Press scale={0.97} onClick={onDone} style={{ marginTop: 20 }}><div style={{ padding: "14px 0", borderRadius: 14, textAlign: "center", background: INK, boxShadow: `0 10px 20px -8px ${aA(INK, 0.5)}` }}><span style={{ fontFamily: SANS, fontSize: 14.5, fontWeight: 700, color: "#FFF" }}>Done · +2 diyas</span></div></Press>
  </div>);
}
// short Work / Money sheet (a placeholder for the fuller "Path" later)
// single-area sheet — Love / Work / Money alike. Adds the fuller "what it means today",
// a plain-astrology "why?", and ONE contextual link (only because its tab exists).
function AreaSheet({ mood, area, onGo }: any) {
  const { accent, accentDeep, glow } = mood;
  const la = ((window as any).LIFE_AREAS || {})[mood.key] || {};
  const meta = ((window as any).LIFE_AREA_META || {})[area] || {};
  const line = area === "Love" ? la.love : area === "Work" ? la.work : la.money;
  const col = area === "Love" ? ["#E48AA6", "#C55C7E"] : area === "Work" ? ["#6E86C4", "#4C63A0"] : ["#5FA97E", "#3E8060"];
  const ic = area === "Love" ? "heart" : area === "Work" ? "work" : "coin";
  const [why, setWhy] = useState(false);
  return (<div>
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <GlossIcon c1={col[0]} c2={col[1]} size={40} radius={13}><Icon n={ic} s={19} c="#FFF" sw={1.9} /></GlossIcon>
      <div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
          <span style={{ fontFamily: SERIF, fontSize: 23, fontWeight: 500, color: INK, letterSpacing: -0.3 }}>{area} today</span>
          <span style={{ fontFamily: MONO, fontSize: 10, letterSpacing: 0.7, textTransform: "uppercase", color: accentDeep }}>· {meta.planet}</span>
        </div>
        <div style={{ fontFamily: MONO, fontSize: 9.5, letterSpacing: 0.5, textTransform: "uppercase", color: GRAY, marginTop: 2 }}>{meta.houses} house</div>
      </div>
    </div>

    <div style={{ fontFamily: SERIF, fontSize: 17, lineHeight: 1.5, color: INK, marginTop: 16, textWrap: "pretty" } as any}>{line}</div>
    <div style={{ fontFamily: SANS, fontSize: 10.5, letterSpacing: 1, textTransform: "uppercase", color: GRAY, margin: "18px 0 7px" }}>What it means today</div>
    <div style={{ fontFamily: SERIF, fontSize: 15.5, lineHeight: 1.62, color: INK2, textWrap: "pretty" } as any}>{meta.detail}</div>

    {/* plain-astrology why?, inline accordion */}
    <Press scale={0.98} onClick={() => setWhy((w: boolean) => !w)} style={{ marginTop: 18 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 7, padding: "10px 13px", borderRadius: 12, background: aA(accentDeep, 0.06), border: `1px solid ${aA(accentDeep, 0.14)}`, width: "fit-content" }}>
        <span style={{ fontFamily: SANS, fontSize: 13, fontWeight: 700, color: accentDeep }}>why?</span>
        <div style={{ transform: why ? "rotate(180deg)" : "none", transition: "transform .25s", display: "flex" }}><Icon n="chevD" s={13} c={accentDeep} /></div>
      </div>
    </Press>
    <div style={{ maxHeight: why ? 200 : 0, opacity: why ? 1 : 0, overflow: "hidden", transition: "max-height .35s ease, opacity .3s ease" }}>
      <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 14.5, lineHeight: 1.6, color: GRAY, marginTop: 12, textWrap: "pretty" } as any}>{meta.why}</div>
    </div>

    {/* ONE contextual link, only because this tab exists */}
    {meta.link && (
      <Press scale={0.98} onClick={() => onGo(meta.link.tab)} style={{ marginTop: 22 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 16px", borderRadius: 14, background: `linear-gradient(150deg, ${aA(accent, 0.1)}, ${aA(glow, 0.04)})`, border: `1px solid ${aA(accent, 0.22)}` }}>
          <span style={{ fontFamily: SANS, fontSize: 14, fontWeight: 700, color: INK }}>{meta.link.label}</span>
          <Icon n="chevR" s={16} c={accentDeep} />
        </div>
      </Press>
    )}
  </div>);
}

// warm notifications — its own screen, opened from the top-bar bell
function NotifScreen({ mood, onBack }: any) {
  const { accent, accentDeep, glow } = mood;
  const items = [
    { ic: "moon", c1: glow, c2: accentDeep, t: "I've been thinking about you", s: "a small pattern from your last few days", now: "just now", unread: true, grp: "New" },
    { ic: "clock", c1: "#6E86C4", c2: "#4C63A0", t: "Your strong window opens at 11:40", s: "good for the pitch you noted", now: "2h ago", unread: true, grp: "New" },
    { ic: "flame", c1: "#D98A2B", c2: "#B26C18", t: "12-day streak, gently held", s: "check in today to keep it warm", now: "5h ago", unread: false, grp: "Earlier" },
  ];
  const groups = ["New", "Earlier"];
  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER, overflowY: "auto" }}>
      {/* pinned header with back */}
      <div style={{ position: "sticky", top: 0, zIndex: 10, padding: "56px 18px 14px", background: PAPER, display: "flex", alignItems: "center", gap: 13, boxShadow: `0 6px 14px -12px ${aA("#1A1408", 0.35)}` }}>
        <Press scale={0.9} onClick={onBack}><div style={{ width: 40, height: 40, borderRadius: 999, ...pill(999), display: "flex", alignItems: "center", justifyContent: "center" }}><Icon n="arrowL" s={18} c={INK} /></div></Press>
        <div>
          <Label c={aA(accentDeep, 0.9)}>For you</Label>
          <div style={{ fontFamily: SERIF, fontSize: 22, fontWeight: 500, color: INK, marginTop: 1 }}>A few quiet notes</div>
        </div>
      </div>
      <div style={{ padding: "8px 18px 130px" }}>
        {groups.map((g) => { const gi = items.filter((n) => n.grp === g); if (!gi.length) return null; return (
          <div key={g} style={{ marginTop: 18 }}>
            <div style={{ marginBottom: 6 }}><Label>{g}</Label></div>
            <div style={{ ...card({ padding: "4px 16px" }) }}>
              {gi.map((n, i) => (
                <Press key={i} scale={0.99}>
                  <div style={{ display: "flex", alignItems: "flex-start", gap: 13, padding: "14px 0", borderTop: i ? `1px solid ${HAIR}` : "none" }}>
                    <GlossIcon c1={n.c1} c2={n.c2} size={40} radius={13}><Icon n={n.ic} s={18} c="#FFF" sw={1.9} /></GlossIcon>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontFamily: SANS, fontSize: 14.5, fontWeight: 700, color: INK, lineHeight: 1.35, textWrap: "pretty" } as any}>{n.t}</div>
                      <div style={{ fontFamily: SERIF, fontSize: 13.5, color: GRAY, marginTop: 2, lineHeight: 1.4 }}>{n.s}</div>
                      <div style={{ fontFamily: MONO, fontSize: 9.5, letterSpacing: 0.6, textTransform: "uppercase", color: aA(GRAY, 0.8), marginTop: 5 }}>{n.now}</div>
                    </div>
                    {n.unread && <div style={{ width: 8, height: 8, borderRadius: 999, flexShrink: 0, marginTop: 6, background: accent, boxShadow: `0 0 6px ${aA(accent, 0.7)}` }} />}
                  </div>
                </Press>
              ))}
            </div>
          </div>
        ); })}
        <div style={{ textAlign: "center", marginTop: 26, fontFamily: SERIF, fontStyle: "italic", fontSize: 14, color: aA(GRAY, 0.9) }}>that's everything, for now</div>
      </div>
    </div>
  );
}

function JournalScreen({ mood, onBack, onSave, onTalk }: any) {
  const { accent, accentDeep, glow } = mood;
  const [text, setText] = useState(""); const [done, setDone] = useState<string | null>(null);
  const [rec, setRec] = useState(false); const [paused, setPaused] = useState(false); const [secs, setSecs] = useState(0);
  const ph = useRef((MIR.placeholders || ["Say it here."])[0]).current;
  useEffect(() => { if (!rec || paused) return; const id = setInterval(() => setSecs((s) => s + 1), 1000); return () => clearInterval(id); }, [rec, paused]);
  const startRec = () => { setSecs(0); setPaused(false); setRec(true); };
  const sendRec = () => { const vn = "I've been carrying a lot this week, and saying it out loud helps more than I expected."; setText((t) => (t ? t + " " : "") + vn); setRec(false); };
  const mmss = `${String(Math.floor(secs / 60)).padStart(2, "0")}:${String(secs % 60).padStart(2, "0")}`;
  const save = () => { if (!text.trim()) return; setDone((MIR.responses || {}).tender || "Thank you for trusting me with that."); onSave && onSave(); };
  return (
    <div style={{ position: "absolute", inset: 0, background: `linear-gradient(180deg, ${aA(glow, 0.16)} 0%, ${PAPER} 34%, ${PAPER} 100%)`, display: "flex", flexDirection: "column", overflow: "hidden" }}>
      {/* cozy ambient glow, top */}
      <div style={{ position: "absolute", top: -70, left: "50%", marginLeft: -140, width: 280, height: 220, borderRadius: 999, background: `radial-gradient(circle, ${aA(glow, 0.32)}, ${aA(glow, 0)} 70%)`, pointerEvents: "none" }} />
      <div style={{ position: "relative", padding: "54px 18px 8px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Press scale={0.9} onClick={onBack}><div style={{ ...pill(999), width: 42, height: 42, display: "flex", alignItems: "center", justifyContent: "center" }}><Icon n={done ? "close" : "arrowL"} s={19} c={INK} /></div></Press>
        <Label c={aA(accentDeep, 0.9)}>The Mirror</Label>
        <div style={{ width: 42 }} />
      </div>

      {done ? (
        <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 30px", textAlign: "center" }}>
          <div style={{ position: "relative", width: 118, height: 140, animation: "floatY 5s ease-in-out infinite" }}>
            <div style={{ position: "absolute", inset: 18, borderRadius: 999, background: `radial-gradient(circle at 50% 46%, ${aA(glow, 0.36)}, ${aA(glow, 0)} 70%)`, animation: "haloBreathe 6s ease-in-out infinite" }} />
            <img src="sage2.png" alt="" draggable={false} style={{ position: "relative", width: "100%", height: "100%", objectFit: "contain", filter: `drop-shadow(0 6px 14px ${aA("#1A1408", 0.18)})` }} />
          </div>
          <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 22, color: INK, marginTop: 24, lineHeight: 1.5, textWrap: "pretty" } as any}>{done}</div>
          <div style={{ fontFamily: MONO, fontSize: 10, letterSpacing: 1.2, textTransform: "uppercase", color: GRAY, marginTop: 20 }}>you wrote today</div>
          <Press scale={0.97} onClick={() => onTalk("")} style={{ marginTop: 26 }}><div style={{ display: "flex", alignItems: "center", gap: 8, padding: "12px 20px", borderRadius: 999, ...pill(999) }}><span style={{ fontFamily: SANS, fontSize: 14, fontWeight: 700, color: INK }}>talk about it?</span><Icon n="arrowR" s={15} c={accentDeep} sw={2} /></div></Press>
        </div>
      ) : (
        <>
          <div style={{ position: "relative", padding: "14px 22px 0" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
              <div style={{ position: "relative", width: 26, height: 26 }}>
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none"><defs><linearGradient id="jrnCr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#FFF6E4" /><stop offset="1" stopColor={accent} /></linearGradient></defs><path d="M18.4 4.3 A9 9 0 1 0 19.8 16.6 A7 7 0 1 1 18.4 4.3 Z" fill="url(#jrnCr)" /></svg>
              </div>
              <span style={{ fontFamily: MONO, fontSize: 10, letterSpacing: 1.2, textTransform: "uppercase", color: aA(accentDeep, 0.8) }}>{DATE}</span>
            </div>
            <div style={{ fontFamily: SERIF, fontSize: 27, fontWeight: 500, color: INK, letterSpacing: -0.4, marginTop: 12 }}>What's on your mind?</div>
            <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 14.5, color: aA(accentDeep, 0.85), marginTop: 6 }}>no pressure, no one else sees this</div>
          </div>
          {/* cozy ruled page holding the textarea */}
          <div style={{ position: "relative", flex: 1, margin: "16px 18px 0", borderRadius: "20px 20px 0 0", background: "linear-gradient(180deg, #FFFDFB, #FFFBF6)", border: `1px solid ${HAIR}`, borderBottom: "none", boxShadow: `0 -2px 24px -12px ${aA(accentDeep, 0.3)}, inset 0 1px 0 #FFF`, overflow: "hidden" }}>
            <div style={{ position: "absolute", inset: 0, backgroundImage: `repeating-linear-gradient(to bottom, transparent, transparent 33px, ${aA(accentDeep, 0.07)} 33px, ${aA(accentDeep, 0.07)} 34px)`, pointerEvents: "none" }} />
            <textarea autoFocus value={text} onChange={(e: any) => setText(e.target.value)} placeholder={ph} style={{ position: "relative", width: "100%", height: "100%", boxSizing: "border-box", padding: "16px 22px", resize: "none", border: "none", outline: "none", background: "transparent", color: INK, fontFamily: SERIF, fontSize: 18, lineHeight: "34px" }} />
          </div>
          <div style={{ position: "relative", padding: "12px 18px 30px", display: "flex", alignItems: "center", gap: 12, background: "#FFFBF6", borderTop: `1px solid ${HAIR}` }}>
            <Press scale={0.92} onClick={startRec}><div style={{ width: 50, height: 50, borderRadius: 999, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", background: aA(accent, 0.12), border: `1px solid ${aA(accent, 0.3)}` }}><Icon n="mic" s={21} c={accentDeep} sw={1.8} /></div></Press>
            <Press scale={0.98} onClick={save} style={{ flex: 1 }}><div style={{ padding: "15px 0", borderRadius: 999, textAlign: "center", background: text.trim() ? INK : WASH, boxShadow: text.trim() ? `0 10px 20px -8px ${aA(INK, 0.5)}` : "none" }}><span style={{ fontFamily: SANS, fontSize: 14.5, fontWeight: 700, color: text.trim() ? "#FFF" : GRAY }}>Leave it with me</span></div></Press>
          </div>
        </>
      )}

      {/* voice recording overlay */}
      {rec && (
        <div style={{ position: "absolute", inset: 0, zIndex: 20, background: `linear-gradient(180deg, ${aA(accentDeep, 0.14)}, rgba(20,16,12,0.5))`, backdropFilter: "blur(10px)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", animation: "fadeIn .3s ease both" }}>
          <div style={{ fontFamily: MONO, fontSize: 10.5, letterSpacing: 1.4, textTransform: "uppercase", color: aA("#FFF", 0.75) }}>{paused ? "paused" : "listening"}</div>
          {/* breathing mic halo */}
          <div style={{ position: "relative", width: 116, height: 116, margin: "22px 0 8px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            {!paused && <div style={{ position: "absolute", inset: 0, borderRadius: 999, background: aA(glow, 0.4), animation: "glowPulse 1.8s ease-in-out infinite", ["--gc" as any]: aA(glow, 0.5) } as any} />}
            <div style={{ width: 78, height: 78, borderRadius: 999, background: `radial-gradient(circle at 40% 34%, ${glow}, ${accentDeep})`, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: `0 12px 30px -8px ${aA(accentDeep, 0.7)}` }}><Icon n="mic" s={30} c="#FFF" sw={1.7} /></div>
          </div>
          {/* live waveform */}
          <div style={{ display: "flex", alignItems: "center", gap: 4, height: 40, marginTop: 6 }}>
            {[0.5, 0.8, 0.4, 1, 0.6, 0.9, 0.35, 0.75, 0.55, 0.95, 0.45, 0.7, 0.85].map((h, i) => (
              <div key={i} style={{ width: 4, height: 34, borderRadius: 2, background: aA("#FFF", 0.9), transformOrigin: "center", transform: `scaleY(${h})`, animation: paused ? "none" : `bar ${0.7 + (i % 4) * 0.18}s ease-in-out ${i * 0.05}s infinite` }} />
            ))}
          </div>
          <div style={{ fontFamily: MONO, fontSize: 15, letterSpacing: 1, color: "#FFF", marginTop: 18 }}>{mmss}</div>
          {/* controls: delete · pause/resume · send */}
          <div style={{ display: "flex", alignItems: "center", gap: 22, marginTop: 30 }}>
            <Press scale={0.9} onClick={() => setRec(false)}><div style={{ width: 54, height: 54, borderRadius: 999, display: "flex", alignItems: "center", justifyContent: "center", background: aA("#FFF", 0.14), border: `1px solid ${aA("#FFF", 0.3)}` }}><Icon n="trash" s={21} c="#FFF" sw={1.8} /></div></Press>
            <Press scale={0.92} onClick={() => setPaused((p) => !p)}><div style={{ width: 66, height: 66, borderRadius: 999, display: "flex", alignItems: "center", justifyContent: "center", background: "#FFF", boxShadow: `0 8px 20px -6px ${aA("#000", 0.4)}` }}><Icon n={paused ? "mic" : "pause"} s={26} c={INK} sw={2} /></div></Press>
            <Press scale={0.9} onClick={sendRec}><div style={{ width: 54, height: 54, borderRadius: 999, display: "flex", alignItems: "center", justifyContent: "center", background: `linear-gradient(155deg, ${glow}, ${accentDeep})`, boxShadow: `0 8px 20px -6px ${aA(accentDeep, 0.7)}` }}><Icon n="check" s={23} c="#FFF" sw={2.4} /></div></Press>
          </div>
          <div style={{ display: "flex", gap: 42, marginTop: 11 }}>
            <span style={{ fontFamily: SANS, fontSize: 11, color: aA("#FFF", 0.65) }}>delete</span>
            <span style={{ fontFamily: SANS, fontSize: 11, color: aA("#FFF", 0.65) }}>{paused ? "resume" : "pause"}</span>
            <span style={{ fontFamily: SANS, fontSize: 11, color: aA("#FFF", 0.65) }}>done</span>
          </div>
        </div>
      )}
    </div>
  );
}
function TimingSheet({ mood }: any) {
  const { accentDeep } = mood;
  const wins = [["Best", "11:40a – 12:30p", "important talks", "#3E9C7A"], ["Good", "2:00 – 3:15p", "steady work", accentDeep], ["Neutral", "3:15 – 6:00p", "ordinary tasks", GRAY], ["Ease off", "9:00 – 10:30a", "hold big decisions", "#C9954A"], ["Avoid", "6:30 – 7:15p", "rest, don't push", ORANGE]];
  return (<div>
    <Label c={aA(accentDeep, 0.9)}>Good times today</Label>
    <div style={{ fontFamily: SERIF, fontSize: 22, fontWeight: 500, color: INK, marginTop: 6, marginBottom: 4 }}>The day's windows</div>
    {wins.map(([k, t, note, c]: any, i) => (
      <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: "13px 0", borderTop: i ? `1px solid ${HAIR}` : "none" }}>
        <div style={{ width: 8, height: 8, borderRadius: 999, background: c, flexShrink: 0 }} />
        <div style={{ width: 62, flexShrink: 0 }}><span style={{ fontFamily: MONO, fontSize: 10, fontWeight: 600, letterSpacing: 1, textTransform: "uppercase", color: c }}>{k}</span></div>
        <div style={{ flex: 1 }}><div style={{ fontFamily: SERIF, fontSize: 15.5, color: INK }}>{t}</div><div style={{ fontFamily: SANS, fontSize: 12, color: GRAY }}>{note}</div></div>
      </div>
    ))}
  </div>);
}

// ===================== APP CONTAINER =====================
function AstroApp() {
  const [moodIdx, setMoodIdx] = useState(CYCLE.indexOf("Deep"));
  const mood = MOOD[CYCLE[moodIdx]] || MOOD["Deep"];
  const cycle = () => setMoodIdx((i: number) => (i + 1) % CYCLE.length);
  const [tab, setTab] = useState("Today");          // Today | Timeline | People | Rituals | Readings
  const [sub, setSub] = useState("Read");           // Read | Plan (Today only)
  const [screen, setScreen] = useState<string | null>(null); // chat | wallet | month (full overlay)
  const [sheet, setSheet] = useState<string | null>(null);
  const [areaKey, setAreaKey] = useState("Love");
  const [askSeed, setAskSeed] = useState("");
  const [bal, setBal] = useState(108);
  const [bump, setBump] = useState(0);
  const [wrote, setWrote] = useState(false);
  const [chatSeed, setChatSeed] = useState("");
  const [showEclipse, setShowEclipse] = useState(true);
  const [checkinOpen, setCheckinOpen] = useState(false);   // rises just after first open of the day
  const [checkinDone, setCheckinDone] = useState(false);
  const [eclType, setEclType] = useState(ECL.type || "solar");
  const earn = (n: number) => { setBal((b) => b + n); setBump((k) => k + 1); };
  useEffect(() => { const t = setTimeout(() => setCheckinOpen(true), 650); return () => clearTimeout(t); }, []);

  const goWallet = () => setScreen("wallet");
  const goChat = (seed = "") => { setChatSeed(seed); setSheet(null); setScreen("chat"); };
  const profile = () => {};   // You area not built yet
  const goPlan = () => { setSub("Plan"); };

  // overlay sub-screens (chat / wallet / month) sit above everything
  if (screen === "chat") return (<div style={{ position: "absolute", inset: 0 }}><ChatScreen mood={mood} seed={chatSeed} opener={new Date().getDate() % 3} onBack={() => { setChatSeed(""); setScreen(null); }} /></div>);
  if (screen === "wallet") return (<div style={{ position: "absolute", inset: 0 }}><WalletScreen mood={mood} bal={bal} onBack={() => setScreen(null)} /><MoonFAB mood={mood} insight={true} onTap={() => goChat()} /></div>);
  if (screen === "month") return (<div style={{ position: "absolute", inset: 0 }}><MonthScreen mood={mood} onBack={() => setScreen(null)} /></div>);
  if (screen === "journal") return (<div style={{ position: "absolute", inset: 0 }}><JournalScreen mood={mood} onBack={() => setScreen(null)} onSave={() => { setWrote(true); earn(1); }} onTalk={(q: string) => goChat(q)} /></div>);
  if (screen === "notif") return (<div style={{ position: "absolute", inset: 0 }}><NotifScreen mood={mood} onBack={() => setScreen(null)} /></div>);

  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER, fontFamily: SANS }}>
      {/* ---- TODAY (Read · Plan) ---- */}
      {tab === "Today" && (
        <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
          {/* pinned header: cluster + Read/Plan switcher */}
          <div style={{ padding: "56px 18px 12px", background: PAPER, zIndex: 20, boxShadow: `0 6px 14px -10px ${aA("#1A1408", 0.3)}` }}>
            <TopCluster mood={mood} bal={bal} bump={bump} alert={true} onProfile={profile} onWallet={goWallet} onBell={() => setScreen("notif")} />
            <div style={{ marginTop: 14 }}><SubTabs mood={mood} value={sub} onChange={setSub} /></div>
          </div>
          {/* scroll body */}
          <div style={{ flex: 1, overflowY: "auto" }}>
            <div style={{ padding: "10px 18px 130px" }}>
              {sub === "Read" ? (
                <>
                  {!checkinDone && !checkinOpen && <CheckInChip mood={mood} delay={0} onOpen={() => setCheckinOpen(true)} />}
                  <div style={{ marginBottom: 22 }}><LivingSkyHeader mood={mood} delay={40} onBell={() => {}} /></div>
                  {showEclipse && <EclipseCard mood={mood} delay={100} type={eclType} onToggleType={() => setEclType((t: string) => t === "solar" ? "lunar" : "solar")} onOpen={() => setSheet("eclipse")} />}
                  <ReadingCard mood={mood} delay={150} onCycle={cycle} onShare={() => {}} onTiming={goPlan} />
                  <LifeAreas mood={mood} delay={200} onArea={(k: string) => { setAreaKey(k); setSheet("area"); }} />
                  <JournalCard mood={mood} delay={250} written={wrote} onOpen={() => setScreen("journal")} />
                  <RitualPill mood={mood} delay={300} onBegin={() => setTab("Rituals")} />
                </>
              ) : (
                <PlanTab mood={mood} onMonth={() => setScreen("month")} onTool={(k: string, seed = "") => { setAskSeed(seed); setSheet(k); }} />
              )}
            </div>
          </div>
        </div>
      )}
      {tab === "Readings" && <DecodeScreen mood={mood} bal={bal} onWallet={goWallet} onProfile={profile} onBell={() => setScreen("notif")} />}
      {tab === "Timeline" && <Placeholder mood={mood} label="Timeline" bal={bal} onProfile={profile} onWallet={goWallet} onBell={() => setScreen("notif")} />}
      {tab === "People" && <Placeholder mood={mood} label="People" bal={bal} onProfile={profile} onWallet={goWallet} onBell={() => setScreen("notif")} />}
      {tab === "Rituals" && <Placeholder mood={mood} label="Rituals" bal={bal} onProfile={profile} onWallet={goWallet} onBell={() => setScreen("notif")} />}

      {/* floating Moon companion + bottom nav (every tab) */}
      <MoonFAB mood={mood} insight={true} onTap={() => goChat()} />
      <BottomNav mood={mood} active={tab} onTab={(t: string) => { setTab(t); }} />

      {/* the daily check-in POPUP (auto-rises on Today) */}
      <Sheet open={checkinOpen && tab === "Today"} onClose={() => setCheckinOpen(false)}>
        <CheckInSheet mood={mood} onEarn={earn} onClose={(done: boolean) => { setCheckinOpen(false); if (done) setCheckinDone(true); }} />
      </Sheet>

      {/* sheets */}
      <Sheet open={sheet === "eclipse"} onClose={() => setSheet(null)}><EclipseSheet mood={mood} type={eclType} /></Sheet>
      <Sheet open={sheet === "area"} onClose={() => setSheet(null)}><AreaSheet mood={mood} area={areaKey} onGo={(tab: string) => { setSheet(null); setTab(tab); }} /></Sheet>
      <Sheet open={sheet === "muhurat"} onClose={() => setSheet(null)}><MuhuratSheet mood={mood} /></Sheet>
      <Sheet open={sheet === "doctor"} onClose={() => setSheet(null)}><CalendarDoctorSheet mood={mood} /></Sheet>
      <Sheet open={sheet === "ask"} onClose={() => setSheet(null)}><AskMomentSheet mood={mood} seed={askSeed} onTalk={(q: string) => goChat(q)} /></Sheet>
      <Sheet open={sheet === "capsule"} onClose={() => setSheet(null)}><TimeCapsuleSheet mood={mood} /></Sheet>
    </div>
  );
}

(window as any).AstroApp = AstroApp;
})();
