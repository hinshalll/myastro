import { useCallback, useEffect, useState } from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { router, useFocusEffect } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';

import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SEVEN_DAYS } from '@/constants/data';
import {
  TabScroll, FadeUp, Display, Body, Small, Kicker, Mono, Btn, Icon, PrecisionBanner,
} from '@/components/ui';
import CelestialCanvas from '@/components/CelestialCanvas';
import HeroMeta from '@/components/HeroMeta';
import DayRail from '@/components/DayRail';
import WhyToggle from '@/components/WhyToggle';

const MONTH = 'May';

export default function Today() {
  const [day, setDay] = useState(0);
  const [mood, setMood] = useState<string | null>(null);

  // Return to today whenever the tab regains focus
  useFocusEffect(useCallback(() => { setDay(0); }, []));

  const d = SEVEN_DAYS[day];
  const label = `${d.wkd} · ${d.dt} ${MONTH}`;

  return (
    <TabScroll>
      <PrecisionBanner />

      {/* Hero */}
      <CelestialCanvas kicker={label} sanskrit={d.sanskrit} />
      <View style={{ paddingHorizontal: 22, paddingTop: 24, alignItems: 'center' }}>
        <VibeWord word={d.word} />
        <Body style={{ marginTop: 8, textAlign: 'center', maxWidth: 280 }}>{d.line}</Body>
      </View>

      <HeroMeta day={day} />

      {/* 7-day rail — below the why */}
      <DayRailSection day={day} setDay={setDay} />

      <SignalCard />
      <MoodCheckIn onLog={setMood} />
      {mood && <MicroInsight mood={mood} />}
      <TimingStrip />
      <ChandraSandhi />
      <RitualCard />
      <EclipseCard />
      <PatternCard />
      <View style={{ height: 24 }} />
    </TabScroll>
  );
}

function VibeWord({ word }: { word: string }) {
  const { p } = useTheme();
  return (
    <Text style={{ fontFamily: fonts.sansMedium, fontSize: 28, lineHeight: 31, letterSpacing: -0.5, color: p.ink }}>
      {word}<Text style={{ color: p.gold }}>.</Text>
    </Text>
  );
}

function DayRailSection({ day, setDay }: { day: number; setDay: (i: number) => void }) {
  const { p } = useTheme();
  return (
    <View style={{ paddingTop: 14, marginTop: 20, borderTopWidth: 1, borderTopColor: p.hairline }}>
      <View style={{ paddingHorizontal: 22, paddingBottom: 8, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <Kicker>Next 7 days</Kicker>
        <Small>tap a day</Small>
      </View>
      <DayRail active={day} onPick={setDay} />
    </View>
  );
}

// ─── Today's signal — do / don't ───
function SignalCard() {
  const { p } = useTheme();
  return (
    <FadeUp style={{ paddingHorizontal: 22, marginTop: 28 }}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <Kicker>Today's signal · 7am</Kicker>
        <Pressable onPress={() => router.push('/signal-preview')}>
          <Small>preview push →</Small>
        </Pressable>
      </View>
      <View style={{ marginTop: 14, flexDirection: 'row', gap: 22, paddingBottom: 4, borderBottomWidth: 1, borderBottomColor: p.hairline }}>
        <View style={{ flex: 1 }}>
          <Mono color={p.teal}>+ do</Mono>
          <Display size={19} style={{ marginTop: 8 }}>Send the half-finished idea.</Display>
        </View>
        <View style={{ flex: 1, borderLeftWidth: 1, borderLeftColor: p.hairline, paddingLeft: 22 }}>
          <Mono color={p.rose}>− don't</Mono>
          <Display size={19} style={{ marginTop: 8 }}>Reply when annoyed.</Display>
        </View>
      </View>
    </FadeUp>
  );
}

// ─── Mood check-in — collapses to a chip after 3 picks ───
const MOODS = ['calm', 'tender', 'sharp', 'heavy', 'wired'];
const ENERGIES = ['low', 'steady', 'bright', 'restless'];
const BODIES = ['rested', 'okay', 'tired', 'off'];

function MoodCheckIn({ onLog }: { onLog: (m: string) => void }) {
  const { p } = useTheme();
  const [mood, setMood] = useState<string | null>(null);
  const [energy, setEnergy] = useState<string | null>(null);
  const [body, setBody] = useState<string | null>(null);
  const [editing, setEditing] = useState(true);
  const done = !!(mood && energy && body);

  useEffect(() => {
    if (done) {
      onLog(mood!);
      const t = setTimeout(() => setEditing(false), 700);
      return () => clearTimeout(t);
    }
  }, [done, mood, energy, body]);

  if (!editing && done) {
    return (
      <FadeUp style={[styles.sectionTop, { borderTopColor: p.hairline }]}>
        <View style={[styles.summaryChip, { backgroundColor: p.surface, borderColor: p.border }]}>
          <Icon name="check" size={13} color={p.gold} />
          <Text style={[styles.pick, { color: p.ink }]}>{mood}</Text>
          <Dot c={p.inkFaint} />
          <Text style={[styles.pick, { color: p.ink }]}>{energy}</Text>
          <Dot c={p.inkFaint} />
          <Text style={[styles.pick, { color: p.ink }]}>{body}</Text>
          <Pressable onPress={() => setEditing(true)} style={{ marginLeft: 'auto' }}>
            <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, letterSpacing: 0.8, textTransform: 'uppercase', color: p.gold }}>edit</Text>
          </Pressable>
        </View>
      </FadeUp>
    );
  }

  return (
    <FadeUp style={[styles.sectionTop, { borderTopColor: p.hairline }]}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <Kicker>Check in · 3 taps</Kicker>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
          <Text style={{ fontFamily: fonts.sansMedium, fontSize: 10, letterSpacing: 1, textTransform: 'uppercase', color: p.gold }}>day 12</Text>
          <View style={{ flexDirection: 'row', gap: 2 }}>
            {Array.from({ length: 7 }).map((_, i) => (
              <View key={i} style={{ width: 4, height: 4, borderRadius: 2, backgroundColor: i < 6 ? p.gold : p.borderStrong }} />
            ))}
          </View>
        </View>
      </View>
      <ChipRow label="Mood" value={mood} options={MOODS} onPick={setMood} />
      <ChipRow label="Energy" value={energy} options={ENERGIES} onPick={setEnergy} />
      <ChipRow label="Body" value={body} options={BODIES} onPick={setBody} />
      {done && (
        <View style={{ marginTop: 14, paddingTop: 8, borderTopWidth: 1, borderTopColor: p.hairline, flexDirection: 'row', gap: 8, alignItems: 'center' }}>
          <Icon name="check" size={14} color={p.gold} />
          <Text style={{ fontFamily: fonts.sansMedium, fontSize: 12, color: p.gold }}>Saved.</Text>
        </View>
      )}
    </FadeUp>
  );
}

function Dot({ c }: { c: string }) {
  return <View style={{ width: 4, height: 4, borderRadius: 2, backgroundColor: c }} />;
}

function ChipRow({ label, value, options, onPick }: {
  label: string; value: string | null; options: string[]; onPick: (v: string) => void;
}) {
  const { p } = useTheme();
  return (
    <View style={{ marginTop: 14 }}>
      <Mono style={{ marginBottom: 8 }}>{label}</Mono>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6 }}>
        {options.map(o => {
          const on = value === o;
          return (
            <Pressable key={o} onPress={() => onPick(o)} style={{
              paddingVertical: 6, paddingHorizontal: 12, borderRadius: 999, borderWidth: 1,
              backgroundColor: on ? p.ink : p.surface,
              borderColor: on ? p.ink : p.border,
            }}>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, color: on ? p.bg0 : p.inkSoft }}>{o}</Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

// ─── Day-1 micro-insight (mirror) ───
const MIRROR: Record<string, { line: string; why: string }> = {
  calm:   { line: "You logged 'calm' — the Moon is moving through your reflective house today. The quiet is real, not a numbness.", why: 'Moon in 4th house · stable, grounding placement.' },
  tender: { line: "You logged 'tender' — Venus is brushing your emotion-Moon. You'll feel softer than usual for a few hours.", why: 'Venus trine natal Moon · transit.' },
  sharp:  { line: "You logged 'sharp' — Mars is in a fast-moving angle. Edge is real today; channel it before 4 pm.", why: 'Mars in Aries · cardinal fire transit.' },
  heavy:  { line: "You logged 'heavy' — Saturn is touching your deepest chamber. This isn't a bad day, it's a deep one. Let it be slow.", why: 'Saturn transit 8th house · processing phase.' },
  wired:  { line: "You logged 'wired' — Mercury is sprinting today. Channel the speed into one thing, or you'll scatter.", why: 'Mercury in Gemini · accelerated mental transit.' },
};
function MicroInsight({ mood }: { mood: string }) {
  const { p } = useTheme();
  const m = MIRROR[mood];
  if (!m) return null;
  return (
    <FadeUp style={[styles.sectionTop, { borderTopColor: p.hairline }]}>
      <Kicker color={p.gold}>A mirror · just now</Kicker>
      <Display size={19} style={{ marginTop: 8 }}>{m.line}</Display>
      <WhyToggle>{m.why}</WhyToggle>
    </FadeUp>
  );
}

// ─── Good times today ───
function TimingStrip() {
  const { p } = useTheme();
  const bands = [
    { len: 6, type: 'meh' }, { len: 3, type: 'good' }, { len: 2, type: 'meh' },
    { len: 1, type: 'avoid' }, { len: 4, type: 'good' }, { len: 2, type: 'meh' },
    { len: 1, type: 'avoid' }, { len: 3, type: 'good' }, { len: 2, type: 'meh' },
  ];
  const color = (t: string) => t === 'good' ? p.gold : t === 'avoid' ? p.rose : p.borderStrong;
  return (
    <FadeUp style={[styles.sectionTop, { borderTopColor: p.hairline, marginTop: 28 }]}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <Kicker>Good times today</Kicker>
        <Pressable onPress={() => router.push('/timing')}><Small>full day →</Small></Pressable>
      </View>
      <View style={{ marginTop: 14, flexDirection: 'row', height: 6, borderRadius: 3, overflow: 'hidden' }}>
        {bands.map((b, i) => (
          <View key={i} style={{ flex: b.len, backgroundColor: color(b.type), opacity: b.type === 'meh' ? 0.5 : 1 }} />
        ))}
      </View>
      <View style={{ marginTop: 6, flexDirection: 'row', justifyContent: 'space-between' }}>
        {['00', '06', '12', '18', '24'].map(t => <Mono key={t}>{t}</Mono>)}
      </View>
      <View style={{ marginTop: 18, gap: 12 }}>
        <TimingLine dot={p.gold} title="Best stretch to act" accent={p.gold} accentText="12 – 4 pm." tail=" Send the message, make the ask, take the meeting." />
        <TimingLine dot={p.rose} title="Hold off" accent={p.rose} accentText="Around 6 pm." tail=" A soft dip — don't sign, don't send the angry reply." />
      </View>
    </FadeUp>
  );
}
function TimingLine({ dot, title, accent, accentText, tail }: {
  dot: string; title: string; accent: string; accentText: string; tail: string;
}) {
  const { p } = useTheme();
  return (
    <View style={{ flexDirection: 'row', gap: 12 }}>
      <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: dot, marginTop: 4 }} />
      <View style={{ flex: 1 }}>
        <Text style={{ fontFamily: fonts.sansMedium, fontSize: 13, color: p.ink }}>{title}</Text>
        <Text style={{ marginTop: 2, fontFamily: fonts.sans, fontSize: 12, lineHeight: 17, color: p.inkMute }}>
          <Text style={{ color: accent }}>{accentText}</Text>{tail}
        </Text>
      </View>
    </View>
  );
}

// ─── Chandra Sandhi · low window ───
function ChandraSandhi() {
  const { p } = useTheme();
  return (
    <FadeUp style={[styles.sectionTop, { borderTopColor: p.hairline }]}>
      <View style={{ flexDirection: 'row', gap: 14, alignItems: 'flex-start' }}>
        <View style={{ width: 30, height: 30, borderRadius: 15, borderWidth: 1, borderColor: p.slate, alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="moon" size={15} color={p.slate} />
        </View>
        <View style={{ flex: 1 }}>
          <Kicker>Low window · 3:15 – 4:42 pm</Kicker>
          <Text style={{ marginTop: 6, fontFamily: fonts.sans, fontSize: 14, lineHeight: 20, color: p.ink }}>
            Don't sign anything. Don't make a call you'd regret.
          </Text>
          <WhyToggle sanskrit="चन्द्र-सन्धि">Moon between signs · weak / reflective.</WhyToggle>
        </View>
      </View>
    </FadeUp>
  );
}

// ─── Daily ritual ───
function RitualCard() {
  const { p } = useTheme();
  return (
    <FadeUp style={[styles.sectionTop, { borderTopColor: p.hairline }]}>
      <Pressable onPress={() => router.push('/rituals')} style={{ flexDirection: 'row', gap: 14, alignItems: 'center' }}>
        <View style={{ width: 40, height: 40, borderRadius: 20, borderWidth: 1, borderColor: p.gold, alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="leaf" size={17} color={p.gold} />
        </View>
        <View style={{ flex: 1 }}>
          <Kicker>Tiny ritual · day 8 of 21</Kicker>
          <Display size={17} style={{ marginTop: 6 }}>Light a lamp at sunset. Three slow breaths.</Display>
        </View>
        <Icon name="chevron" size={16} color={p.inkMute} />
      </Pressable>
    </FadeUp>
  );
}

// ─── Eclipse alert ───
function EclipseCard() {
  const { p } = useTheme();
  return (
    <FadeUp style={[styles.sectionTop, { borderTopColor: p.hairline }]}>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 14 }}>
        <View style={{ width: 28, height: 28, borderRadius: 14, backgroundColor: '#14101e', shadowColor: p.gold, shadowOpacity: 0.4, shadowRadius: 14, elevation: 6 }} />
        <View style={{ flex: 1 }}>
          <Kicker color={p.rose}>Heads up · 6 days</Kicker>
          <Display size={17} style={{ marginTop: 4 }}>An eclipse is coming.</Display>
        </View>
      </View>
      <Body style={{ marginTop: 12, maxWidth: 320 }}>
        Eclipses surface what's been shifting quietly. Don't start anything new this week — and observe Sutak hours on the day itself.
      </Body>
      <View style={{ flexDirection: 'row', gap: 10, marginTop: 14 }}>
        <Btn label="What to expect" size="sm" />
        <Btn label="Hide" size="sm" variant="ghost" />
      </View>
    </FadeUp>
  );
}

// ─── Premium "this happened before" ───
function PatternCard() {
  const { p, name } = useTheme();
  return (
    <FadeUp style={[styles.sectionTop, { borderTopColor: p.hairline }]}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <Kicker>This happened before</Kicker>
        <View style={[styles.tag, { backgroundColor: p.goldSoft, borderColor: p.gold }]}>
          <Text style={{ fontFamily: fonts.sansMedium, fontSize: 9, letterSpacing: 1.2, textTransform: 'uppercase', color: p.gold }}>Myastro+</Text>
        </View>
      </View>

      <View style={{ marginTop: 12, position: 'relative', overflow: 'hidden', borderRadius: 12 }}>
        <View>
          <Display size={19}>
            The last time Saturn touched this part of your chart was March 2017 — when you left the apartment on Hill Street and started over.
          </Display>
          <Body style={{ marginTop: 10 }}>
            You'll feel a familiar weight in your chest by Tuesday. This time you're not the same person.
          </Body>
        </View>

        <BlurView intensity={18} tint={name === 'dark' ? 'dark' : 'light'} style={StyleSheet.absoluteFill} />
        <LinearGradient
          colors={['transparent', name === 'dark' ? 'rgba(11,9,7,0.85)' : 'rgba(255,255,255,0.85)']}
          style={[StyleSheet.absoluteFill, { alignItems: 'center', justifyContent: 'center', gap: 12, padding: 18 }]}
        >
          <Icon name="lock" size={18} color={p.gold} />
          <Display size={17} style={{ textAlign: 'center' }}>A pattern only you can see.</Display>
          <Btn label="Unlock · ₹199/mo" variant="gold" size="sm" onPress={() => router.push('/paywall')} />
        </LinearGradient>
      </View>
    </FadeUp>
  );
}

const styles = StyleSheet.create({
  sectionTop: { paddingHorizontal: 22, marginTop: 22, paddingTop: 22, borderTopWidth: 1 },
  summaryChip: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    paddingVertical: 12, paddingHorizontal: 16, borderRadius: 999, borderWidth: 1,
  },
  pick: { fontFamily: fonts.sansMedium, fontSize: 12 },
  tag: { paddingVertical: 3, paddingHorizontal: 8, borderRadius: 999, borderWidth: 1 },
});
