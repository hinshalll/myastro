// AstroApp.tsx — the container that wires navigation + shared state (astro-screens.tsx AstroApp).
// State-driven navigation, ported near-verbatim. This slice fully wires the Read sub-tab;
// Plan + Chat/Wallet/etc. overlays are placeholders built in the next phase.
import React, { useEffect, useRef, useState } from "react";
import { View, Text, ScrollView, Pressable, BackHandler } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MOOD_BY_KEY, CYCLE, demoTick } from "./theme";
import { PAPER, INK, GRAY, aA, sans, serif, shadow } from "./ui/palette";
import { Sheet } from "./ui/Sheet";
import { MoodEmblem } from "./ui/mood";
import { DemoBadge } from "./ui/DemoBadge";
import { TopCluster, MoonFAB, SubTabs, BottomNav } from "./today/chrome";
import { LivingSkyHeader } from "./today/LivingSkyHeader";
import { EclipseCard, SandhiCard, ReadingCard, LifeAreas, JournalCard, RitualPill } from "./today/read";
import { CheckInSheet, CheckInChip, checkInWindowOpen } from "./today/CheckIn";
import { EclipseSheet, SandhiSheet, AreaSheet } from "./today/sheets";
import { PlanTab } from "./plan/PlanTab";
import { MuhuratSheet, CalendarDoctorSheet, AskMomentSheet, TimeCapsuleSheet } from "./plan/toolsheets";
import { MonthScreen } from "./plan/MonthScreen";
import { ChatScreen } from "./screens/ChatScreen";
import { WalletScreen } from "./screens/WalletScreen";
import { DecodeScreen } from "./screens/DecodeScreen";
import { NotifScreen } from "./screens/NotifScreen";
import { JournalScreen } from "./screens/JournalScreen";
import { loadToday, TodayRead } from "./api/today";

// When the reading can't be fetched, SAY SO. This used to be tracked in state and never
// rendered, so a backend outage looked like a finished screen quietly showing the
// prototype's placeholder day. An honest "couldn't reach it" beats a confident wrong day.
function SkyOffline({ mood, onRetry }: { mood: any; onRetry: () => void }) {
  const { accent, accentDeep } = mood;
  return (
    <View style={{ marginBottom: 16, padding: 15, borderRadius: 16, backgroundColor: aA(accent, 0.07), borderWidth: 1, borderColor: aA(accent, 0.22), flexDirection: "row", alignItems: "center", gap: 12 }}>
      <View style={{ flex: 1 }}>
        <Text style={{ fontFamily: serif(500), fontSize: 16, color: INK }}>Today's reading didn't load</Text>
        <Text style={{ fontFamily: sans(400), fontSize: 12.5, color: GRAY, marginTop: 3, lineHeight: 17 }}>
          We couldn't reach the sky just now. Anything below is a placeholder, not your day.
        </Text>
      </View>
      <Pressable onPress={onRetry}>
        <View style={{ paddingVertical: 9, paddingHorizontal: 14, borderRadius: 999, backgroundColor: accentDeep }}>
          <Text style={{ fontFamily: sans(800), fontSize: 12.5, color: "#FFF" }}>Retry</Text>
        </View>
      </Pressable>
    </View>
  );
}

function Placeholder({ mood, label, insetTop }: any) {
  return (
    <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, alignItems: "center", justifyContent: "center", gap: 14 }}>
      <MoodEmblem mood={mood} size={64} />
      <Text style={{ fontFamily: serif(500), fontSize: 26, color: INK }}>{label}</Text>
      <Text style={{ fontFamily: sans(400), fontSize: 14, color: GRAY }}>coming soon</Text>
    </View>
  );
}

export function AstroApp() {
  // Re-taxes the demo ledger each render so the DEMO badge shows what is fake NOW, not what was
  // fake during the first paint before loadToday() resolved. Dev-only no-op in production.
  demoTick();
  const insets = useSafeAreaInsets();
  const [moodIdx, setMoodIdx] = useState(CYCLE.indexOf("Deep"));
  const [today, setToday] = useState<TodayRead | null>(null);
  const [todayErr, setTodayErr] = useState(false);
  // Today's real vibe word (from the live reading) drives the app's mood colour + emblem.
  // Until it loads — or if the backend can't be reached — we fall back to the demo mood cycle.
  const liveKey = today?.reading.vibeWord;
  const mood = MOOD_BY_KEY[(liveKey as string) || CYCLE[moodIdx]] || MOOD_BY_KEY["Deep"];
  const cycle = () => { if (!today) setMoodIdx((i) => (i + 1) % CYCLE.length); };

  const [tab, setTab] = useState("Today");
  const [sub, setSub] = useState("Read");
  const [screen, setScreen] = useState<string | null>(null);
  const [sheet, setSheet] = useState<string | null>(null);
  const [areaKey, setAreaKey] = useState("Love");
  // The row the user tapped, resolved against the SAME bundle the row itself rendered from.
  const areaLive = today ? (today.lifeAreas as any)[areaKey.toLowerCase()] ?? null : null;
  const [askSeed, setAskSeed] = useState("");
  const [bal, setBal] = useState(108);
  const [bump, setBump] = useState(0);
  const [wrote, setWrote] = useState(false);
  const [chatSeed, setChatSeed] = useState("");
  const [checkinOpen, setCheckinOpen] = useState(false);
  const [checkinDone, setCheckinDone] = useState(false);

  // Is the check-in allowed to ask yet? Evening only (5pm→midnight) where the user actually is.
  // Re-checked every minute so it appears on its own at 5pm and disappears at midnight, rather
  // than only at app launch — this is a companion someone leaves open, not a page they reload.
  const [checkinAsk, setCheckinAsk] = useState(() => checkInWindowOpen());
  useEffect(() => {
    const t = setInterval(() => setCheckinAsk(checkInWindowOpen()), 60_000);
    return () => clearInterval(t);
  }, []);
  const earn = (n: number) => { setBal((b) => b + n); setBump((k) => k + 1); };

  useEffect(() => { const t = setTimeout(() => setCheckinOpen(true), 650); return () => clearTimeout(t); }, []);

  // Load today's real reading (bundle + hora + eclipse + ritual) once on open.
  const [reloads, setReloads] = useState(0);
  useEffect(() => {
    let alive = true;
    loadToday()
      .then((d) => { if (alive) { setToday(d); setTodayErr(false); } })
      .catch(() => { if (alive) setTodayErr(true); });
    return () => { alive = false; };
  }, [reloads]);

  // Android hardware back closes overlays/sheets first
  useEffect(() => {
    const onBack = () => {
      if (sheet) { setSheet(null); return true; }
      if (screen) { setScreen(null); return true; }
      if (tab !== "Today") { setTab("Today"); return true; }
      return false;
    };
    const sub2 = BackHandler.addEventListener("hardwareBackPress", onBack);
    return () => sub2.remove();
  }, [sheet, screen, tab]);

  const scrollRef = useRef<ScrollView>(null);
  const goWallet = () => setScreen("wallet");
  const goChat = (seed = "") => { setChatSeed(typeof seed === "string" ? seed : ""); setSheet(null); setScreen("chat"); };
  const profile = () => {};
  // "Strongest window today" → open the Plan sub-tab and land straight on the My Day card
  // (it's first). Snap with animated:false so it doesn't visibly scroll up FROM wherever the
  // shared scroll offset was (which looked like it stopped on Ask the Moment first). Reset
  // both before and after the sub swaps, so the jump is instant regardless of layout timing.
  const goDay = () => {
    scrollRef.current?.scrollTo({ y: 0, animated: false });
    setSub("Plan");
    requestAnimationFrame(() => scrollRef.current?.scrollTo({ y: 0, animated: false }));
    setTimeout(() => scrollRef.current?.scrollTo({ y: 0, animated: false }), 60);
  };

  // full-screen overlays
  if (screen === "chat") return <ChatScreen mood={mood} seed={chatSeed} opener={new Date().getDate() % 3} onBack={() => { setChatSeed(""); setScreen(null); }} insetTop={insets.top} />;
  if (screen === "wallet") return (
    <View style={{ flex: 1 }}>
      <WalletScreen mood={mood} bal={bal} onBack={() => setScreen(null)} insetTop={insets.top} />
      <MoonFAB mood={mood} insight onTap={() => goChat()} />
    </View>
  );
  if (screen === "month") return <MonthScreen mood={mood} onBack={() => setScreen(null)} insetTop={insets.top} />;
  if (screen === "journal") return <JournalScreen mood={mood} onBack={() => setScreen(null)} onSave={() => { setWrote(true); earn(1); }} onTalk={(q: string) => goChat(q)} insetTop={insets.top} />;
  if (screen === "notif") return <NotifScreen mood={mood} onBack={() => setScreen(null)} insetTop={insets.top} />;

  return (
    <View style={{ flex: 1, backgroundColor: PAPER }}>
      {tab === "Today" && (
        <View style={{ flex: 1 }}>
          {/* pinned header */}
          <View style={{ paddingTop: insets.top + 8, paddingHorizontal: 18, paddingBottom: 12, backgroundColor: PAPER, zIndex: 20, ...shadow({ y: 4, blur: 14, opacity: 0.1, elevation: 4 }) } as any}>
            <TopCluster mood={mood} bal={bal} bump={bump} alert onProfile={profile} onWallet={goWallet} onBell={() => setScreen("notif")} />
            <View style={{ marginTop: 14 }}><SubTabs value={sub} onChange={setSub} /></View>
          </View>
          {/* scroll body */}
          <ScrollView ref={scrollRef} style={{ flex: 1 }} contentContainerStyle={{ paddingTop: 10, paddingHorizontal: 18, paddingBottom: 130 }} showsVerticalScrollIndicator={false}>
            {sub === "Read" ? (
              <>
                {/* evening only (5pm→midnight, local) — see checkInWindowOpen: asking in the
                    morning would store breakfast labelled as the whole day, and the pattern
                    engine correlates the DAY's energy against the sky */}
                {checkinAsk && !checkinDone && !checkinOpen && <CheckInChip mood={mood} delay={0} onOpen={() => setCheckinOpen(true)} />}
                {todayErr && <SkyOffline mood={mood} onRetry={() => { setTodayErr(false); setReloads((n) => n + 1); }} />}
                <View style={{ marginBottom: 22 }}><LivingSkyHeader mood={mood} delay={40} hora={today?.hora} /></View>
                {/* Both heads-up cards render themselves away when the sky has nothing to say. */}
                <EclipseCard mood={mood} delay={100} live={today?.eclipse ?? null} onOpen={() => setSheet("eclipse")} />
                <SandhiCard mood={mood} delay={120} live={today?.sandhi ?? null} onOpen={() => setSheet("sandhi")} />
                <ReadingCard mood={mood} delay={150} live={today?.reading} personal={today?.personal ?? null} strongWindow={today?.timing?.strongWindow} onCycle={cycle} onShare={() => {}} onTiming={goDay} />
                <LifeAreas mood={mood} delay={200} live={today?.lifeAreas} onArea={(k: string) => { setAreaKey(k); setSheet("area"); }} />
                <JournalCard mood={mood} delay={250} written={wrote} onOpen={() => setScreen("journal")} />
                <RitualPill mood={mood} delay={300} live={today?.ritual} onBegin={() => setTab("Rituals")} />
              </>
            ) : (
              <PlanTab mood={mood} timing={today?.timing} panchang={today?.panchang} onMonth={() => setScreen("month")} onTool={(k: string, seed = "") => { setAskSeed(seed); setSheet(k); }} />
            )}
          </ScrollView>
        </View>
      )}
      {tab === "Readings" && <DecodeScreen mood={mood} bal={bal} onWallet={goWallet} onProfile={profile} onBell={() => setScreen("notif")} insetTop={insets.top} />}
      {tab === "Timeline" && <Placeholder mood={mood} label="Timeline" />}
      {tab === "People" && <Placeholder mood={mood} label="People" />}
      {tab === "Rituals" && <Placeholder mood={mood} label="Rituals" />}

      <MoonFAB mood={mood} insight onTap={() => goChat()} />
      <BottomNav mood={mood} active={tab} onTab={setTab} />

      {/* check-in popup (auto-rises on Today) */}
      <Sheet open={checkinOpen && tab === "Today"} onClose={() => setCheckinOpen(false)}>
        <CheckInSheet mood={mood} onEarn={earn} onClose={(done: boolean) => { setCheckinOpen(false); if (done) setCheckinDone(true); }} />
      </Sheet>

      {/* detail sheets — each is a view over the SAME live payload as the card that opened
          it, so tapping in can never show a different day than the card promised */}
      <Sheet open={sheet === "eclipse"} onClose={() => setSheet(null)}><EclipseSheet mood={mood} live={today?.eclipse ?? null} /></Sheet>
      <Sheet open={sheet === "sandhi"} onClose={() => setSheet(null)}><SandhiSheet mood={mood} live={today?.sandhi ?? null} /></Sheet>
      <Sheet open={sheet === "area"} onClose={() => setSheet(null)}>
        <AreaSheet mood={mood} area={areaKey} live={areaLive} onGo={(t: string) => { setSheet(null); setTab(t); }} />
      </Sheet>
      <Sheet open={sheet === "muhurat"} onClose={() => setSheet(null)}><MuhuratSheet mood={mood} /></Sheet>
      <Sheet open={sheet === "doctor"} onClose={() => setSheet(null)}><CalendarDoctorSheet mood={mood} /></Sheet>
      <Sheet open={sheet === "ask"} onClose={() => setSheet(null)}><AskMomentSheet mood={mood} seed={askSeed} onTalk={(q: string) => goChat(q)} /></Sheet>
      <Sheet open={sheet === "capsule"} onClose={() => setSheet(null)}><TimeCapsuleSheet mood={mood} /></Sheet>

      {/* dev only: names every fake data source currently on screen. Renders nothing in prod. */}
      <DemoBadge />
    </View>
  );
}
