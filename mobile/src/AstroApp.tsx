// AstroApp.tsx — the container that wires navigation + shared state (astro-screens.tsx AstroApp).
// State-driven navigation, ported near-verbatim. This slice fully wires the Read sub-tab;
// Plan + Chat/Wallet/etc. overlays are placeholders built in the next phase.
import React, { useEffect, useRef, useState } from "react";
import { View, Text, ScrollView, Pressable, BackHandler } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { MOOD_BY_KEY, CYCLE, ECLIPSE } from "./theme";
import { PAPER, INK, GRAY, aA, sans, serif, shadow } from "./ui/palette";
import { Sheet } from "./ui/Sheet";
import { MoodEmblem } from "./ui/mood";
import { TopCluster, MoonFAB, SubTabs, BottomNav } from "./today/chrome";
import { LivingSkyHeader } from "./today/LivingSkyHeader";
import { EclipseCard, ReadingCard, LifeAreas, JournalCard, RitualPill } from "./today/read";
import { CheckInSheet, CheckInChip } from "./today/CheckIn";
import { EclipseSheet, AreaSheet } from "./today/sheets";
import { PlanTab } from "./plan/PlanTab";
import { MuhuratSheet, CalendarDoctorSheet, AskMomentSheet, TimeCapsuleSheet } from "./plan/toolsheets";
import { MonthScreen } from "./plan/MonthScreen";
import { ChatScreen } from "./screens/ChatScreen";
import { WalletScreen } from "./screens/WalletScreen";
import { DecodeScreen } from "./screens/DecodeScreen";
import { NotifScreen } from "./screens/NotifScreen";
import { JournalScreen } from "./screens/JournalScreen";

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
  const insets = useSafeAreaInsets();
  const [moodIdx, setMoodIdx] = useState(CYCLE.indexOf("Deep"));
  const mood = MOOD_BY_KEY[CYCLE[moodIdx]] || MOOD_BY_KEY["Deep"];
  const cycle = () => setMoodIdx((i) => (i + 1) % CYCLE.length);

  const [tab, setTab] = useState("Today");
  const [sub, setSub] = useState("Read");
  const [screen, setScreen] = useState<string | null>(null);
  const [sheet, setSheet] = useState<string | null>(null);
  const [areaKey, setAreaKey] = useState("Love");
  const [askSeed, setAskSeed] = useState("");
  const [bal, setBal] = useState(108);
  const [bump, setBump] = useState(0);
  const [wrote, setWrote] = useState(false);
  const [chatSeed, setChatSeed] = useState("");
  const [checkinOpen, setCheckinOpen] = useState(false);
  const [checkinDone, setCheckinDone] = useState(false);
  const [eclType, setEclType] = useState(ECLIPSE.type || "solar");
  const [showEclipse] = useState(true);
  const earn = (n: number) => { setBal((b) => b + n); setBump((k) => k + 1); };

  useEffect(() => { const t = setTimeout(() => setCheckinOpen(true), 650); return () => clearTimeout(t); }, []);

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
                {!checkinDone && !checkinOpen && <CheckInChip mood={mood} delay={0} onOpen={() => setCheckinOpen(true)} />}
                <View style={{ marginBottom: 22 }}><LivingSkyHeader mood={mood} delay={40} /></View>
                {showEclipse && <EclipseCard mood={mood} delay={100} type={eclType} onToggleType={() => setEclType((t) => (t === "solar" ? "lunar" : "solar"))} onOpen={() => setSheet("eclipse")} />}
                <ReadingCard mood={mood} delay={150} onCycle={cycle} onShare={() => {}} onTiming={goDay} />
                <LifeAreas mood={mood} delay={200} onArea={(k: string) => { setAreaKey(k); setSheet("area"); }} />
                <JournalCard mood={mood} delay={250} written={wrote} onOpen={() => setScreen("journal")} />
                <RitualPill mood={mood} delay={300} onBegin={() => setTab("Rituals")} />
              </>
            ) : (
              <PlanTab mood={mood} onMonth={() => setScreen("month")} onTool={(k: string, seed = "") => { setAskSeed(seed); setSheet(k); }} />
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

      {/* detail sheets */}
      <Sheet open={sheet === "eclipse"} onClose={() => setSheet(null)}><EclipseSheet mood={mood} type={eclType} /></Sheet>
      <Sheet open={sheet === "area"} onClose={() => setSheet(null)}><AreaSheet mood={mood} area={areaKey} onGo={(t: string) => { setSheet(null); setTab(t); }} /></Sheet>
      <Sheet open={sheet === "muhurat"} onClose={() => setSheet(null)}><MuhuratSheet mood={mood} /></Sheet>
      <Sheet open={sheet === "doctor"} onClose={() => setSheet(null)}><CalendarDoctorSheet mood={mood} /></Sheet>
      <Sheet open={sheet === "ask"} onClose={() => setSheet(null)}><AskMomentSheet mood={mood} seed={askSeed} onTalk={(q: string) => goChat(q)} /></Sheet>
      <Sheet open={sheet === "capsule"} onClose={() => setSheet(null)}><TimeCapsuleSheet mood={mood} /></Sheet>
    </View>
  );
}
