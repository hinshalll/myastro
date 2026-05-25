import React, { useEffect, useState } from 'react';
import { View, Pressable, Text } from 'react-native';
import Svg, { Circle, Defs, RadialGradient, Stop } from 'react-native-svg';
import { LinearGradient } from 'expo-linear-gradient';
import { fonts, radius, useTheme } from '@/theme/theme';
import { Icon } from '@/ui/Icon';
import { H2, H3, Display, Body, Small, Kicker, Mono } from '@/ui/Type';
import { Card, Hr, Chip, Button, AppBar, IconButton, WhyToggle, WhyTinyHint } from '@/ui/primitives';
import { VibeRing } from '@/ui/primitives';
import { ConstellationBG } from '@/ui/Background';
import { useNav } from '@/nav/NavContext';

type HeroVariant = 'ring' | 'orb' | 'sky';
const HERO_VARIANT = 'ring' as HeroVariant;
const PAD = 22;

// ── Asterism spacer ──
const Asterism = () => {
  const { c } = useTheme();
  return <Text style={{ textAlign: 'center', fontFamily: fonts.display, fontSize: 16, color: c.inkMute, letterSpacing: 12, paddingTop: 22, paddingBottom: 14 }}>✦ · ✦</Text>;
};

// ── Hero: ring ──
const HeroRing = () => {
  const { c } = useTheme();
  return (
    <View style={{ paddingHorizontal: PAD, paddingTop: 14 }}>
      <Kicker style={{ marginBottom: 18 }}>Today · Fri 25 May</Kicker>
      <View style={{ flexDirection: 'row', alignItems: 'flex-end', gap: 24 }}>
        <View style={{ flex: 1 }}>
          <Display style={{ fontSize: 64, lineHeight: 62, letterSpacing: -2 }}>Magnetic.</Display>
          <Body style={{ marginTop: 14, maxWidth: 280 }}>People keep finding their way to you today. Say the harder thing.</Body>
        </View>
        <VibeRing value={0.78} size={72} color={c.gold} />
      </View>
      <WhyToggle sanskrit="चन्द्रः मघा-नक्षत्रे, शुक्रः त्रिकोणे">
        Your Moon sits in a warm, expressive star (Magha nakshatra) with Venus angled sweetly to it. Translation: warmth radiates and lands well.
      </WhyToggle>
    </View>
  );
};

// ── Hero: orb ──
const HeroOrb = () => {
  const { c } = useTheme();
  return (
    <View style={{ paddingHorizontal: PAD, paddingTop: 14, alignItems: 'center' }}>
      <Kicker style={{ marginBottom: 22 }}>Today · Fri 25 May</Kicker>
      <View style={{ width: 120, height: 120, marginBottom: 22, marginTop: 4 }}>
        <Svg width={120} height={120}>
          <Defs>
            <RadialGradient id="orb" cx="38%" cy="32%" r="75%">
              <Stop offset="0%" stopColor="#e6c373" /><Stop offset="40%" stopColor="#a07c2c" />
              <Stop offset="78%" stopColor="#4a3208" /><Stop offset="100%" stopColor="#1a1004" />
            </RadialGradient>
          </Defs>
          <Circle cx={60} cy={60} r={60} fill="url(#orb)" />
        </Svg>
        <View style={{ position: 'absolute', top: -10, left: -10, right: -10, bottom: -10, borderRadius: 70, borderWidth: 1, borderColor: c.gold, opacity: 0.25 }} />
      </View>
      <Display style={{ fontSize: 60, lineHeight: 58, letterSpacing: -2, textAlign: 'center' }}>Magnetic.</Display>
      <Body style={{ marginTop: 14, textAlign: 'center', paddingHorizontal: 16 }}>People keep finding their way to you today. Say the harder thing.</Body>
      <View style={{ alignSelf: 'stretch' }}>
        <WhyToggle sanskrit="चन्द्रः मघा-नक्षत्रे, शुक्रः त्रिकोणे">Moon in a warm, expressive star + Venus in a sweet angle. You&apos;re hard to look away from today.</WhyToggle>
      </View>
    </View>
  );
};

// ── Hero: sky ──
const HeroSky = () => {
  const { c } = useTheme();
  return (
    <View style={{ marginHorizontal: 14, marginTop: 6, borderRadius: 20, overflow: 'hidden', minHeight: 320, borderWidth: 1, borderColor: c.border }}>
      <LinearGradient colors={['#14102a', '#2a1542', '#3b1c3e']} style={{ position: 'absolute', inset: 0 }} />
      <ConstellationBG seed={11} density={45} opacity={0.4} />
      <View style={{ position: 'absolute', right: 30, top: 26, width: 36, height: 36, borderRadius: 18, overflow: 'hidden' }}>
        <Svg width={36} height={36}><Defs><RadialGradient id="moon" cx="40%" cy="35%" r="75%"><Stop offset="0%" stopColor="#f0e2bd" /><Stop offset="65%" stopColor="#c4a358" /><Stop offset="100%" stopColor="#5d4218" /></RadialGradient></Defs><Circle cx={18} cy={18} r={18} fill="url(#moon)" /></Svg>
      </View>
      <View style={{ paddingTop: 170, paddingHorizontal: PAD, paddingBottom: 24 }}>
        <Kicker style={{ marginBottom: 10, color: 'rgba(236,230,212,0.6)' }}>Today · Fri 25 May</Kicker>
        <Display style={{ fontSize: 62, lineHeight: 59, letterSpacing: -2, color: '#f0e2bd' }}>Magnetic.</Display>
        <Body style={{ marginTop: 12, maxWidth: 280, color: 'rgba(236,230,212,0.8)' }}>People keep finding their way to you. Say the harder thing.</Body>
        <WhyToggle sanskrit="चन्द्रः मघा-नक्षत्रे, शुक्रः त्रिकोणे">Moon in Magha nakshatra + Venus in a kind angle = strong day for being seen.</WhyToggle>
      </View>
    </View>
  );
};

// ── Today's Signal ──
const SignalCard = ({ onOpenPreview }: { onOpenPreview: () => void }) => {
  const { c } = useTheme();
  return (
    <View style={{ paddingHorizontal: PAD, marginTop: 18 }}>
      <Card style={{ padding: 18 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' }}>
          <Kicker>Today&apos;s signal · 7:00 am</Kicker>
          <Text onPress={onOpenPreview} style={{ fontFamily: fonts.sans, fontSize: 12, color: c.inkMute, textDecorationLine: 'underline' }}>preview push</Text>
        </View>
        <View style={{ flexDirection: 'row', marginTop: 12, gap: 14 }}>
          <View style={{ flex: 1 }}>
            <Mono style={{ color: c.teal }}>+ do</Mono>
            <Display style={{ fontSize: 18, lineHeight: 22, marginTop: 6 }}>Send the half-finished idea.</Display>
          </View>
          <View style={{ width: 1, backgroundColor: c.hairline }} />
          <View style={{ flex: 1 }}>
            <Mono style={{ color: c.rose }}>− don&apos;t</Mono>
            <Display style={{ fontSize: 18, lineHeight: 22, marginTop: 6 }}>Reply when annoyed.</Display>
          </View>
        </View>
      </Card>
    </View>
  );
};

// ── Day-1 micro-insight ──
const MICRO: Record<string, { line: string; why: string }> = {
  calm: { line: "You logged 'calm' — the Moon is moving through your reflective house today. The quiet is real, not a numbness.", why: 'Moon in 4th house · stable, grounding placement.' },
  tender: { line: "You logged 'tender' — Venus is brushing your emotion-Moon. You'll feel softer than usual for a few hours.", why: 'Venus trine natal Moon · transit.' },
  sharp: { line: "You logged 'sharp' — Mars is in a fast-moving angle. Edge is real today; channel it before 4 pm.", why: 'Mars in Aries · cardinal fire transit.' },
  heavy: { line: "You logged 'heavy' — Saturn is touching your deepest chamber. This isn't a bad day, it's a deep one. Let it be slow.", why: 'Saturn transit 8th house · processing phase.' },
  wired: { line: "You logged 'wired' — Mercury is sprinting today. Channel the speed into one thing, or you'll scatter.", why: 'Mercury in Gemini · accelerated mental transit.' },
};
const MicroInsight = ({ mood }: { mood: string | null }) => {
  const { c } = useTheme();
  if (!mood || !MICRO[mood]) return null;
  const m = MICRO[mood];
  return (
    <View style={{ paddingHorizontal: PAD, marginTop: 14 }}>
      <Card style={{ padding: 18, borderColor: c.gold }}>
        <Kicker gold>A mirror · just now</Kicker>
        <Display style={{ fontSize: 17, lineHeight: 23, marginTop: 8 }}>{m.line}</Display>
        <WhyToggle>{m.why}</WhyToggle>
      </Card>
    </View>
  );
};

// ── Mood check-in ──
const ChipRow = ({ label, value, options, onPick }: { label: string; value: string | null; options: string[]; onPick: (v: string) => void }) => {
  const { c } = useTheme();
  return (
    <View style={{ marginTop: 14 }}>
      <Mono style={{ marginBottom: 8 }}>{label}</Mono>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6 }}>
        {options.map(o => <Chip key={o} label={o} active={value === o} onPress={() => onPick(o)} />)}
      </View>
    </View>
  );
};

const MoodCheckIn = ({ onLog }: { onLog: (m: string) => void }) => {
  const { c } = useTheme();
  const [mood, setMood] = useState<string | null>(null);
  const [energy, setEnergy] = useState<string | null>(null);
  const [body, setBody] = useState<string | null>(null);
  const done = !!(mood && energy && body);
  useEffect(() => { if (done && mood) onLog(mood); }, [done]);
  return (
    <View style={{ paddingHorizontal: PAD, marginTop: 14 }}>
      <Card style={{ padding: 18 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' }}>
          <Kicker>Check in · 3 taps</Kicker>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
            <Text style={{ fontFamily: fonts.sans500, fontSize: 10, letterSpacing: 1, textTransform: 'uppercase', color: c.gold }}>day 12</Text>
            <View style={{ flexDirection: 'row', gap: 2 }}>
              {Array.from({ length: 7 }).map((_, i) => (
                <View key={i} style={{ width: 4, height: 4, borderRadius: 2, backgroundColor: i < 6 ? c.gold : c.borderStrong }} />
              ))}
            </View>
          </View>
        </View>
        <ChipRow label="Mood" value={mood} options={['calm', 'tender', 'sharp', 'heavy', 'wired']} onPick={setMood} />
        <ChipRow label="Energy" value={energy} options={['low', 'steady', 'bright', 'restless']} onPick={setEnergy} />
        <ChipRow label="Body" value={body} options={['rested', 'okay', 'tired', 'off']} onPick={setBody} />
        {done ? (
          <View style={{ marginTop: 14, paddingTop: 8, borderTopWidth: 1, borderTopColor: c.hairline, flexDirection: 'row', alignItems: 'center', gap: 8 }}>
            <Icon name="check" size={14} color={c.gold} />
            <Text style={{ fontFamily: fonts.sans500, fontSize: 12, color: c.gold }}>Saved. See what we noticed →</Text>
          </View>
        ) : null}
      </Card>
    </View>
  );
};

// ── Good times strip ──
const TimingStrip = ({ onOpen }: { onOpen: () => void }) => {
  const { c } = useTheme();
  const bands = [
    { len: 6, type: 'meh' }, { len: 3, type: 'good' }, { len: 2, type: 'meh' }, { len: 1, type: 'avoid' },
    { len: 4, type: 'good' }, { len: 2, type: 'meh' }, { len: 1, type: 'avoid' }, { len: 3, type: 'good' }, { len: 2, type: 'meh' },
  ];
  const col: Record<string, string> = { good: c.gold, avoid: c.rose, meh: c.borderStrong };
  return (
    <View style={{ paddingHorizontal: PAD, marginTop: 14 }}>
      <Pressable onPress={onOpen}>
        <Card style={{ padding: 18 }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' }}>
            <Kicker>Good times today</Kicker>
            <Small>full day →</Small>
          </View>
          <View style={{ flexDirection: 'row', marginTop: 14, height: 8, borderRadius: 4, overflow: 'hidden' }}>
            {bands.map((b, i) => <View key={i} style={{ flex: b.len, backgroundColor: col[b.type] }} />)}
          </View>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 6 }}>
            {['00', '06', '12', '18', '24'].map(t => <Mono key={t}>{t}</Mono>)}
          </View>
          <Body style={{ marginTop: 12 }}>Strong window <Text style={{ color: c.gold }}>12 – 4 pm</Text>.  Soft dip around <Text style={{ color: c.rose }}>6 pm</Text>.</Body>
        </Card>
      </Pressable>
    </View>
  );
};

// ── Chandra Sandhi ──
const ChandraSandhi = () => {
  const { c } = useTheme();
  return (
    <View style={{ paddingHorizontal: PAD, marginTop: 14 }}>
      <Card style={{ padding: 16, flexDirection: 'row', gap: 14, alignItems: 'center' }}>
        <View style={{ width: 36, height: 36, borderRadius: 18, borderWidth: 1, borderColor: c.violet, alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="moon" size={18} color={c.violet} />
        </View>
        <View style={{ flex: 1 }}>
          <Kicker>Low window · 3:15 – 4:42 pm</Kicker>
          <Text style={{ fontFamily: fonts.sans500, fontSize: 14, lineHeight: 20, marginTop: 4, color: c.ink }}>Don&apos;t sign anything. Don&apos;t make a call you&apos;d regret.</Text>
        </View>
        <WhyTinyHint sanskrit="चन्द्र-सन्धि">Moon between signs · weak / reflective.</WhyTinyHint>
      </Card>
    </View>
  );
};

// ── Daily ritual ──
const RitualCard = ({ onOpen }: { onOpen: () => void }) => {
  const { c } = useTheme();
  return (
    <View style={{ paddingHorizontal: PAD, marginTop: 14 }}>
      <Pressable onPress={onOpen}>
        <Card style={{ padding: 18, flexDirection: 'row', gap: 14, alignItems: 'center' }}>
          <View style={{ width: 44, height: 44, borderRadius: 12, backgroundColor: c.goldSoft, borderWidth: 1, borderColor: c.gold, alignItems: 'center', justifyContent: 'center' }}>
            <Icon name="leaf" size={20} color={c.gold} />
          </View>
          <View style={{ flex: 1 }}>
            <Kicker>Tiny ritual · day 8 of 21</Kicker>
            <Display style={{ fontSize: 17, lineHeight: 21, marginTop: 4 }}>Light a lamp at sunset. Three slow breaths.</Display>
          </View>
          <Icon name="chevron" size={18} color={c.inkMute} />
        </Card>
      </Pressable>
    </View>
  );
};

// ── Eclipse alert ──
const EclipseCard = () => {
  const { c } = useTheme();
  return (
    <View style={{ paddingHorizontal: PAD, marginTop: 14 }}>
      <Card style={{ padding: 18, borderColor: 'rgba(210,135,152,0.35)' }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
          <View style={{ width: 28, height: 28, borderRadius: 14, overflow: 'hidden' }}>
            <Svg width={28} height={28}><Defs><RadialGradient id="ecl" cx="30%" cy="30%" r="75%"><Stop offset="30%" stopColor="#14101e" /><Stop offset="70%" stopColor="#000000" /></RadialGradient></Defs><Circle cx={14} cy={14} r={14} fill="url(#ecl)" /></Svg>
          </View>
          <View style={{ flex: 1 }}>
            <Kicker style={{ color: c.rose }}>Heads up · 6 days</Kicker>
            <Display style={{ fontSize: 17, marginTop: 2 }}>An eclipse is coming.</Display>
          </View>
        </View>
        <Body style={{ fontSize: 13, marginTop: 12 }}>Eclipses surface what&apos;s been shifting quietly. Don&apos;t start anything new this week — and observe Sutak hours on the day itself.</Body>
        <View style={{ flexDirection: 'row', gap: 8, marginTop: 14 }}>
          <Button title="What to expect" size="sm" />
          <Button title="Hide" size="sm" variant="ghost" />
        </View>
      </Card>
    </View>
  );
};

// ── Locked pattern card ──
const PatternCard = ({ onUnlock }: { onUnlock: () => void }) => {
  const { c } = useTheme();
  return (
    <View style={{ paddingHorizontal: PAD, marginTop: 14 }}>
      <Card style={{ padding: 18, overflow: 'hidden' }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
          <Kicker>This happened before</Kicker>
          <View style={{ paddingHorizontal: 8, paddingVertical: 3, borderRadius: 999, backgroundColor: c.goldSoft, borderWidth: 1, borderColor: c.gold }}>
            <Text style={{ fontFamily: fonts.sans500, fontSize: 9, letterSpacing: 1, textTransform: 'uppercase', color: c.gold }}>Myastro+</Text>
          </View>
        </View>
        <View style={{ marginTop: 12, opacity: 0.18 }}>
          <Display style={{ fontSize: 19, lineHeight: 25 }}>The last time Saturn touched this part of your chart was March 2017 — when you left the apartment on Hill Street and started over.</Display>
          <Body style={{ fontSize: 13, marginTop: 10 }}>You&apos;ll feel a familiar weight in your chest by Tuesday. This time you&apos;re not the same person.</Body>
        </View>
        <View style={{ position: 'absolute', inset: 0, alignItems: 'center', justifyContent: 'center', gap: 12, padding: 18 }}>
          <LinearGradient colors={['rgba(10,10,16,0)', 'rgba(10,10,16,0.65)']} style={{ position: 'absolute', inset: 0 }} />
          <Icon name="lock" size={20} color={c.gold} />
          <Display style={{ fontSize: 17, textAlign: 'center' }}>A pattern only you can see.</Display>
          <Button title="Unlock · ₹199/mo" variant="gold" size="sm" onPress={onUnlock} />
        </View>
      </Card>
    </View>
  );
};

// ── Precision banner ──
export const PrecisionBanner = ({ tier }: { tier: 'exact' | 'approximate' | 'unknown' }) => {
  const { c } = useTheme();
  if (tier === 'exact') return null;
  const s = tier === 'approximate'
    ? { color: c.inkMute, text: 'Birth time approximate · some readings flagged' }
    : { color: c.rose, text: 'Moon-chart mode · add your time to unlock more' };
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10, paddingHorizontal: 14, paddingVertical: 10, marginHorizontal: 14, marginTop: 10, borderRadius: 12, backgroundColor: c.surface, borderWidth: 1, borderColor: c.border }}>
      <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: s.color }} />
      <Body style={{ flex: 1, fontSize: 11 }}>{s.text}</Body>
      <Small style={{ color: c.gold }}>Add →</Small>
    </View>
  );
};

// ── TODAY screen ──
export const TodayScreen = () => {
  const { c } = useTheme();
  const { nav, precision } = useNav();
  const [lastMood, setLastMood] = useState<string | null>(null);
  const Hero = HERO_VARIANT === 'orb' ? HeroOrb : HERO_VARIANT === 'sky' ? HeroSky : HeroRing;
  return (
    <View>
      <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 18, paddingTop: 6, paddingBottom: 4 }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
          <Icon name="logo" size={22} color={c.gold} />
          <Text style={{ fontFamily: fonts.sans500, fontSize: 14, color: c.ink, letterSpacing: 0.5 }}>Myastro</Text>
        </View>
        <IconButton name="bell" onPress={() => nav('signal-preview')} />
      </View>
      <PrecisionBanner tier={precision} />
      <Hero />
      <Asterism />
      <SignalCard onOpenPreview={() => nav('signal-preview')} />
      <MoodCheckIn onLog={setLastMood} />
      <MicroInsight mood={lastMood} />
      <TimingStrip onOpen={() => nav('timing')} />
      <ChandraSandhi />
      <RitualCard onOpen={() => nav('rituals-hub')} />
      <EclipseCard />
      <PatternCard onUnlock={() => nav('paywall')} />
      <View style={{ height: 16 }} />
    </View>
  );
};

// ── Full-day timing ──
export const TimingScreen = () => {
  const { c } = useTheme();
  const { back } = useNav();
  const slots = [
    { time: '5:30 – 6:45 am', label: 'sit with it', type: 'good', note: 'Best stretch to be alone.' },
    { time: '7:00 – 9:00 am', label: 'neutral', type: 'meh', note: '' },
    { time: '9:00 – 11:30 am', label: 'do the work', type: 'good', note: 'Focus runs deep here.' },
    { time: '11:30 – 12:30', label: 'pause on email', type: 'avoid', note: 'A message could land sideways.' },
    { time: '12:30 – 4:00 pm', label: 'meet people', type: 'good', note: 'Warmth radiates. Say yes to plans.' },
    { time: '3:15 – 4:42 pm', label: 'low window', type: 'avoid', note: 'Chandra Sandhi · reflective hour.' },
    { time: '4:00 – 6:00 pm', label: 'neutral', type: 'meh', note: '' },
    { time: '6:00 – 6:45 pm', label: "don't react", type: 'avoid', note: 'Something will sting. It will pass.' },
    { time: '7:00 – 10:00 pm', label: 'soft hours', type: 'good', note: 'Cook. Call someone. Read.' },
  ];
  const dot: Record<string, string> = { good: c.gold, avoid: c.rose, meh: c.inkMute };
  return (
    <View>
      <AppBar title="Today's hours" onBack={back} />
      <View style={{ paddingHorizontal: PAD, paddingTop: 8 }}>
        <H2 style={{ marginBottom: 4 }}>Your day, hour by hour.</H2>
        <Body style={{ marginBottom: 18 }}>Plan around the windows.</Body>
        <Card style={{ padding: 4 }}>
          {slots.map((s, i) => (
            <View key={i} style={{ flexDirection: 'row', alignItems: 'center', gap: 14, paddingHorizontal: 14, paddingVertical: 14, borderBottomWidth: i === slots.length - 1 ? 0 : 1, borderBottomColor: c.hairline }}>
              <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: dot[s.type] }} />
              <View style={{ flex: 1 }}>
                <Text style={{ fontFamily: fonts.sans500, fontSize: 14, color: c.ink }}>{s.label}</Text>
                <Mono style={{ marginTop: 4 }}>{s.time}</Mono>
                {s.note ? <Body style={{ fontSize: 12, marginTop: 6 }}>{s.note}</Body> : null}
              </View>
            </View>
          ))}
        </Card>
        <View style={{ height: 20 }} />
      </View>
    </View>
  );
};

// ── Rituals hub ──
export const RitualsHub = () => {
  const { c } = useTheme();
  const { back, nav } = useNav();
  const journeys = [
    { title: 'Open the heart', sub: 'Venus · soften', days: 40, icon: 'heart' as const },
    { title: 'Money flow', sub: 'Jupiter · expansion', days: 21, icon: 'sparkle' as const },
    { title: 'Old grief', sub: 'Moon · release', days: 40, icon: 'moon' as const },
    { title: 'Health & body', sub: 'Sun · vitality', days: 21, icon: 'sun' as const },
    { title: 'Speak the truth', sub: 'Mars · courage', days: 21, icon: 'flame' as const },
  ];
  return (
    <View>
      <AppBar title="Rituals" onBack={back} />
      <View style={{ paddingHorizontal: PAD, paddingTop: 8 }}>
        <H2 style={{ marginBottom: 4 }}>Small daily things.</H2>
        <Body style={{ marginBottom: 20 }}>Choose one. Show up for it.</Body>
        <Kicker style={{ marginBottom: 10 }}>In progress</Kicker>
        <Pressable onPress={() => nav('ritual-detail')}>
          <Card strong style={{ padding: 18, marginBottom: 16 }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 14 }}>
              <View style={{ width: 44, height: 44, borderRadius: 12, backgroundColor: c.goldSoft, borderWidth: 1, borderColor: c.gold, alignItems: 'center', justifyContent: 'center' }}>
                <Icon name="leaf" size={22} color={c.gold} />
              </View>
              <View style={{ flex: 1 }}>
                <Display style={{ fontSize: 19, lineHeight: 23 }}>Settle the mind</Display>
                <Mono style={{ marginTop: 4, color: c.gold }}>Day 8 of 21</Mono>
              </View>
            </View>
            <View style={{ marginTop: 14, height: 3, borderRadius: 2, backgroundColor: c.border }}>
              <View style={{ width: `${(8 / 21) * 100}%`, height: '100%', backgroundColor: c.gold, borderRadius: 2 }} />
            </View>
          </Card>
        </Pressable>
        <Kicker style={{ marginBottom: 10 }}>Begin a journey</Kicker>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 10 }}>
          {journeys.map(j => (
            <Card key={j.title} style={{ padding: 14, width: '47.5%' }}>
              <View style={{ width: 32, height: 32, borderRadius: 10, backgroundColor: c.surfaceStrong, alignItems: 'center', justifyContent: 'center' }}>
                <Icon name={j.icon} size={16} color={c.gold} />
              </View>
              <Text style={{ fontFamily: fonts.sans500, fontSize: 14, color: c.ink, marginTop: 10 }}>{j.title}</Text>
              <Small style={{ marginTop: 2 }}>{j.sub}</Small>
              <Mono style={{ marginTop: 8 }}>{j.days} days</Mono>
            </Card>
          ))}
        </View>
        <Pressable onPress={() => nav('mala')} style={{ marginTop: 16 }}>
          <Card style={{ padding: 16, flexDirection: 'row', gap: 12, alignItems: 'center' }}>
            <View style={{ width: 36, height: 36, borderRadius: 10, backgroundColor: c.surfaceStrong, alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="sparkle" size={18} color={c.gold} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ fontFamily: fonts.sans500, fontSize: 14, color: c.ink }}>Mala · bead counter</Text>
              <Small>108 taps · with haptics</Small>
            </View>
            <Icon name="chevron" size={18} color={c.inkMute} />
          </Card>
        </Pressable>
        <View style={{ height: 20 }} />
      </View>
    </View>
  );
};

export const RitualDetail = () => {
  const { c } = useTheme();
  const { back } = useNav();
  const [checked, setChecked] = useState([true, true, false]);
  const tasks = ['Sit by a window for three minutes.', 'Three slow breaths, eyes closed.', "Write one sentence you don't want to say."];
  return (
    <View>
      <AppBar title="Settle the mind" onBack={back} right={<IconButton name="share" />} />
      <View style={{ paddingHorizontal: PAD, paddingTop: 8 }}>
        <Card style={{ padding: 20 }}>
          <Kicker>Day 8 of 21</Kicker>
          <Display style={{ fontSize: 24, lineHeight: 29, marginTop: 8 }}>The body remembers before the mind catches up.</Display>
          <View style={{ marginTop: 20, flexDirection: 'row', gap: 3 }}>
            {Array.from({ length: 21 }).map((_, i) => (
              <View key={i} style={{ flex: 1, height: 4, borderRadius: 2, backgroundColor: i < 8 ? c.gold : c.border }} />
            ))}
          </View>
          <WhyToggle sanskrit="चन्द्र-शान्ति · Moon-pacification practice">This 21-day cycle works on Moon energy — emotional regulation through small, rhythmic acts. Repetition + breath = recalibration.</WhyToggle>
        </Card>
        <Kicker style={{ marginTop: 20, marginBottom: 10 }}>Today · three things</Kicker>
        {tasks.map((t, i) => (
          <Pressable key={i} onPress={() => setChecked(arr => arr.map((v, j) => (j === i ? !v : v)))} style={{ marginBottom: 8 }}>
            <Card style={{ padding: 14, flexDirection: 'row', gap: 12, alignItems: 'center', borderColor: checked[i] ? c.gold : c.border }}>
              <View style={{ width: 22, height: 22, borderRadius: 6, borderWidth: 1, borderColor: checked[i] ? c.gold : c.borderStrong, backgroundColor: checked[i] ? c.gold : 'transparent', alignItems: 'center', justifyContent: 'center' }}>
                {checked[i] ? <Icon name="check" size={14} color="#1a1408" /> : null}
              </View>
              <Text style={{ fontFamily: fonts.sans, fontSize: 14, textDecorationLine: checked[i] ? 'line-through' : 'none', color: checked[i] ? c.inkMute : c.ink, flex: 1 }}>{t}</Text>
            </Card>
          </Pressable>
        ))}
        <View style={{ height: 20 }} />
      </View>
    </View>
  );
};

export const MalaScreen = () => {
  const { c } = useTheme();
  const { back } = useNav();
  const [count, setCount] = useState(43);
  return (
    <View style={{ flex: 1 }}>
      <AppBar title="Mala" onBack={back} />
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', paddingHorizontal: PAD }}>
        <Kicker style={{ marginBottom: 12 }}>108 to complete · {108 - count} left</Kicker>
        <Display style={{ fontSize: 96, lineHeight: 96 }}>{count}</Display>
        <Pressable onPress={() => setCount(n => Math.min(108, n + 1))} style={{ marginTop: 28, width: 220, height: 220, borderRadius: 110, alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
          <Svg width={220} height={220} style={{ position: 'absolute' }}><Defs><RadialGradient id="bead" cx="38%" cy="32%" r="75%"><Stop offset="0%" stopColor="#c8a253" /><Stop offset="50%" stopColor="#8b6a2b" /><Stop offset="100%" stopColor="#4a3208" /></RadialGradient></Defs><Circle cx={110} cy={110} r={110} fill="url(#bead)" /></Svg>
          <Text style={{ fontFamily: fonts.displayItalic, fontSize: 18, color: '#1d1408' }}>tap</Text>
        </Pressable>
        <View style={{ marginTop: 32, flexDirection: 'row', gap: 16, alignItems: 'center' }}>
          <Text style={{ fontFamily: fonts.sans500, fontSize: 10, letterSpacing: 1, textTransform: 'uppercase', color: c.inkMute }}>streak 5</Text>
          <Text style={{ color: c.inkMute }}>·</Text>
          <Text onPress={() => setCount(0)} style={{ fontFamily: fonts.sans500, fontSize: 10, letterSpacing: 1, textTransform: 'uppercase', color: c.inkMute }}>reset</Text>
        </View>
      </View>
    </View>
  );
};

export const SignalPreviewScreen = () => {
  const { c } = useTheme();
  const { back } = useNav();
  const alerts: [string, string, any][] = [
    ['Eclipse · 6 days ahead', 'Sutak begins 4:32 am', 'bell'],
    ['"This happened before"', 'Premium · proactive memory', 'sparkle'],
    ['Birth-time nudge', "If you added 'later'", 'edit'],
  ];
  return (
    <View>
      <AppBar title="Today's Signal · preview" onBack={back} />
      <View style={{ paddingHorizontal: PAD, paddingTop: 8 }}>
        <Body>This is the one notification you&apos;ll get each morning. No spam — that&apos;s the deal.</Body>
        <Kicker style={{ marginTop: 24, marginBottom: 10 }}>Lock screen · 7:00 am</Kicker>
        <View style={{ borderRadius: 24, padding: 24, overflow: 'hidden', borderWidth: 1, borderColor: c.border }}>
          <LinearGradient colors={['#14101e', '#2a1542']} style={{ position: 'absolute', inset: 0 }} />
          <ConstellationBG seed={5} density={40} opacity={0.4} />
          <View style={{ alignItems: 'center' }}>
            <Kicker style={{ color: 'rgba(236,230,212,0.65)' }}>FRI · MAY 25</Kicker>
            <Display style={{ fontSize: 56, lineHeight: 56, marginTop: 4, color: 'rgba(236,230,212,0.95)' }}>7:00</Display>
          </View>
          <View style={{ marginTop: 50, backgroundColor: 'rgba(10,8,28,0.7)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.10)', borderRadius: 18, padding: 14, flexDirection: 'row', gap: 12, alignItems: 'flex-start' }}>
            <View style={{ width: 32, height: 32, borderRadius: 8, backgroundColor: c.gold, alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="logo" size={20} color="#1a1408" />
            </View>
            <View style={{ flex: 1 }}>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                <Kicker style={{ color: 'rgba(236,230,212,0.7)' }}>MYASTRO</Kicker>
                <Kicker style={{ color: 'rgba(236,230,212,0.5)' }}>now</Kicker>
              </View>
              <Text style={{ fontFamily: fonts.sans500, fontSize: 14, lineHeight: 19, color: 'rgba(236,230,212,0.95)', marginTop: 6 }}>Magnetic day. Send the half-finished idea — don&apos;t reply when annoyed.</Text>
            </View>
          </View>
        </View>
        <Kicker style={{ marginTop: 24, marginBottom: 10 }}>Other alerts (optional)</Kicker>
        <Card>
          {alerts.map(([t, s, ic], i) => (
            <View key={i} style={{ flexDirection: 'row', alignItems: 'center', gap: 14, paddingHorizontal: 18, paddingVertical: 14, borderBottomWidth: i === alerts.length - 1 ? 0 : 1, borderBottomColor: c.hairline }}>
              <Icon name={ic} size={16} color={c.gold} />
              <View style={{ flex: 1 }}>
                <Text style={{ fontFamily: fonts.sans500, fontSize: 14, color: c.ink }}>{t}</Text>
                <Small style={{ marginTop: 2 }}>{s}</Small>
              </View>
            </View>
          ))}
        </Card>
        <View style={{ height: 20 }} />
      </View>
    </View>
  );
};
