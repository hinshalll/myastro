import { useEffect, useRef, useState } from 'react';
import {
  View, Text, TextInput, Pressable, StyleSheet, KeyboardAvoidingView, Platform, ScrollView,
} from 'react-native';
import { router } from 'expo-router';
import { BlurView } from 'expo-blur';
import Animated, {
  useSharedValue, useAnimatedStyle, withTiming, runOnJS, Easing,
} from 'react-native-reanimated';

import { useTheme } from '@/constants/ThemeContext';
import { fonts, radii } from '@/constants/theme';
import Icon from './Icon';
import WhyToggle from './WhyToggle';

const QUOTA = 3;
type Mode = 'ask' | 'decide';
type Reply = { head: string; body: string; why: string; sanskrit: string };

const SUGGESTIONS = [
  'Should I take this job?',
  'Is today good to travel?',
  'When will I meet someone?',
  'Why am I so tired this week?',
  'Should I have the hard talk today?',
  'Best week to move house?',
];

const DECIDE_TRY = [
  'Send the message now?',
  'Buy the flight today?',
  'Have the hard talk tonight?',
  'Sign the lease today?',
];

const REPLIES: Record<string, Reply> = {
  'should i take this job': {
    head: 'Yes — but wait until next week to sign.',
    body: 'Everything in your chart points to this being a real chapter shift. Saturn is moving through your work sector — a long, building yes. But the planet of contracts is tangled this week. Negotiate now, sign Tuesday or after.',
    why: 'Saturn in 10th = lasting career foundations. Mercury retrograde through Mon makes paperwork fragile.',
    sanskrit: 'शनि-दशा · कर्म-स्थानम्',
  },
  'is today good to travel': {
    head: "Today's fine. Tomorrow is better.",
    body: 'No red flags today, but the windows are short — leave before 11 am or after 5 pm. Tomorrow you have a full clear corridor.',
    why: 'Moon shifts signs at 11:15 today; tomorrow the Moon trines Jupiter for nine hours.',
    sanskrit: 'गोचर · चन्द्र-संक्रमण',
  },
  'when will i meet someone': {
    head: "A real spark in autumn — and you'll already know them.",
    body: "Venus crosses your relationship sector in October and lingers longer than usual. The pattern often shows up as someone you've already met, seen newly. Pay attention to second meetings between Sep and Nov.",
    why: 'Venus stations direct in your 7th house Oct 14, with a Jupiter aspect through November.',
    sanskrit: 'शुक्र-गोचर · सप्तम-भावे',
  },
  'why am i so tired': {
    head: "Your body is processing something your mind hasn't named yet.",
    body: 'Mars is moving through your private-self sector — exhausting internal work, even when nothing external is happening. Sleep more, expect less of yourself this week.',
    why: 'Mars in the 12th house is a 6-week stretch of low energy and heavy dreams. Ends in 11 days.',
    sanskrit: 'मङ्गल-गोचर · व्यय-स्थाने',
  },
};

const FALLBACK_REPLY: Reply = {
  head: 'Wait two days.',
  body: 'The chart says yes — but not yet. Mercury is finishing a slow walk-back through your decisions sector through Wednesday. Friday and Saturday are clean, decisive days. If you act before then, you\'ll second-guess yourself by Sunday.',
  why: 'Mercury retrograde shadow ends Wed 11:42 pm. Saturday Moon trines your natal Sun — a clean "yes" window.',
  sanskrit: 'बुधः वक्री · प्रश्न-कुण्डली',
};

function replyFor(q: string): Reply {
  const key = q.toLowerCase().replace(/[^a-z ]/g, '').trim();
  const hit = Object.keys(REPLIES).find(k => key.includes(k));
  return hit ? REPLIES[hit] : FALLBACK_REPLY;
}

type Verdict = 'yes' | 'wait' | 'gentle';
function decideFor(q: string): { verdict: Verdict; line: string } {
  const t = q.toLowerCase();
  if (/(angry|upset|annoyed|fight|argue|ex|reply)/.test(t))   return { verdict: 'wait',   line: "Not now. The reply you'd send today is sharper than the one you'd send Sunday." };
  if (/(sign|contract|commit|buy|big purchase|lease)/.test(t)) return { verdict: 'gentle', line: 'You can — but only after 5 pm. Mercury is still walking back through small print.' };
  if (/(travel|trip|drive|fly|flight)/.test(t))               return { verdict: 'yes',    line: 'Yes. Leave before 11 am or after 5. The middle of the day is fine for movement.' };
  if (/(call|message|text|reach out|send)/.test(t))           return { verdict: 'yes',    line: "Yes. They've been thinking about you too — say the warmer thing." };
  if (/(quit|leave|end|break up)/.test(t))                     return { verdict: 'wait',   line: "Wait two days. The conviction will still be there. The edge won't." };
  return { verdict: 'gentle', line: 'Move, but slowly. Today rewards small steps, not declarations.' };
}

type Msg = { who: 'me'; text: string } | { who: 'star'; reply: Reply };

export default function AskOverlay({
  initialQuery = '',
  initialMode = 'ask',
  onClose,
}: {
  initialQuery?: string;
  initialMode?: Mode;
  onClose: () => void;
}) {
  const { p, name } = useTheme();
  const [mode, setMode] = useState<Mode>(initialMode);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Msg[]>([]);
  const [typing, setTyping] = useState(false);
  const [decideQ, setDecideQ] = useState(initialMode === 'decide' ? initialQuery : '');
  const [decideResult, setDecideResult] = useState<{ q: string; verdict: Verdict; line: string } | null>(null);
  const [used, setUsed] = useState(0);
  const scrollRef = useRef<ScrollView>(null);
  const didInit = useRef(false);

  const ty = useSharedValue(700);
  const bd = useSharedValue(0);
  useEffect(() => {
    bd.value = withTiming(1, { duration: 220, easing: Easing.out(Easing.cubic) });
    ty.value = withTiming(0, { duration: 320, easing: Easing.out(Easing.cubic) });
  }, []);
  const handleClose = () => {
    bd.value = withTiming(0, { duration: 180 });
    ty.value = withTiming(700, { duration: 240, easing: Easing.in(Easing.cubic) }, (done) => {
      if (done) runOnJS(onClose)();
    });
  };

  const sheetStyle = useAnimatedStyle(() => ({ transform: [{ translateY: ty.value }] }));
  const bdStyle = useAnimatedStyle(() => ({ opacity: bd.value }));

  const ask = (q: string) => {
    if (used >= QUOTA) return;
    setMessages(m => [...m, { who: 'me', text: q }]);
    setUsed(u => u + 1);
    setInput('');
    setTyping(true);
    setTimeout(() => {
      setMessages(m => [...m, { who: 'star', reply: replyFor(q) }]);
      setTyping(false);
    }, 1100);
  };

  const decide = (q: string) => {
    if (used >= QUOTA || !q.trim()) return;
    setUsed(u => u + 1);
    setDecideResult({ q: q.trim(), ...decideFor(q) });
  };

  // Pre-fill on open (from Explore "most asked", or Decide entry)
  useEffect(() => {
    if (didInit.current) return;
    didInit.current = true;
    if (!initialQuery) return;
    if (initialMode === 'decide') setDecideQ(initialQuery);
    else setTimeout(() => ask(initialQuery), 350);
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollToEnd({ animated: true });
  }, [messages, typing]);

  const goPaywall = () => { handleClose(); setTimeout(() => router.push('/paywall'), 220); };
  const limit = used >= QUOTA;

  return (
    <View style={StyleSheet.absoluteFill}>
      <Animated.View style={[StyleSheet.absoluteFill, bdStyle]}>
        <Pressable onPress={handleClose} style={StyleSheet.absoluteFill}>
          <BlurView intensity={20} tint={name === 'dark' ? 'dark' : 'light'} style={StyleSheet.absoluteFill} />
          <View style={{ flex: 1, backgroundColor: 'rgba(2,1,8,0.55)' }} />
        </Pressable>
      </Animated.View>

      <Animated.View style={[styles.sheet, { backgroundColor: p.bg0, borderColor: p.border }, sheetStyle]}>
        <View style={styles.grabberWrap}><View style={[styles.grabber, { backgroundColor: p.inkMute }]} /></View>

        <View style={[styles.header, { borderBottomColor: p.hairline }]}>
          <View style={[styles.orbMini, { backgroundColor: p.gold }]} />
          <View style={[styles.seg, { backgroundColor: p.surface, borderColor: p.border }]}>
            {(['ask', 'decide'] as const).map(m => {
              const on = m === mode;
              return (
                <Pressable key={m} onPress={() => setMode(m)} style={[styles.segBtn, on && { backgroundColor: p.ink }]}>
                  <Text style={{ fontFamily: fonts.sansMedium, fontSize: 12, color: on ? p.bg0 : p.inkMute, textTransform: 'capitalize' }}>{m}</Text>
                </Pressable>
              );
            })}
          </View>
          <Quota used={used} />
          <Pressable onPress={handleClose} hitSlop={8} style={[styles.x, { borderColor: p.border }]}>
            <Icon name="close" size={16} />
          </Pressable>
        </View>

        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ flex: 1 }}>
          <ScrollView ref={scrollRef} contentContainerStyle={{ padding: 16, paddingBottom: 24 }} keyboardShouldPersistTaps="handled">
            {mode === 'ask' ? (
              <>
                {messages.length === 0 && (
                  <View>
                    <Text style={[styles.lead, { color: p.ink }]}>Ask anything.{'\n'}In your words.</Text>
                    <Text style={[styles.body, { color: p.inkSoft, marginTop: 12 }]}>
                      No special phrasing needed. "Should I text my ex?" works.
                    </Text>

                    <Pressable onPress={() => setMode('decide')} style={[styles.decideCta, { borderColor: p.gold, backgroundColor: p.goldSoft }]}>
                      <View style={[styles.decideIcon, { backgroundColor: p.bg0, borderColor: p.gold }]}>
                        <Icon name="check" size={16} color={p.gold} />
                      </View>
                      <View style={{ flex: 1 }}>
                        <Text style={{ fontFamily: fonts.sansMedium, fontSize: 13, color: p.ink }}>Just need a yes/no?</Text>
                        <Text style={[styles.small, { color: p.inkMute, marginTop: 2 }]}>Switch to Decide · instant verdict</Text>
                      </View>
                      <Icon name="chevron" size={16} color={p.gold} />
                    </Pressable>

                    <Text style={[styles.kicker, { color: p.inkMute, marginTop: 22, marginBottom: 10 }]}>Or try one of these</Text>
                    {SUGGESTIONS.map(q => (
                      <Pressable key={q} onPress={() => ask(q)} style={[styles.suggest, { borderColor: p.border, backgroundColor: p.surface }]}>
                        <Text style={{ color: p.gold, marginRight: 8 }}>·</Text>
                        <Text style={[styles.body, { color: p.inkSoft, flex: 1 }]}>{q}</Text>
                      </Pressable>
                    ))}
                  </View>
                )}

                {messages.map((m, i) => (
                  <View key={i} style={{ marginBottom: 14 }}>
                    {m.who === 'me' ? (
                      <View style={{ alignItems: 'flex-end' }}>
                        <Text style={[styles.bubbleMe, { backgroundColor: p.ink, color: p.bg0 }]}>{m.text}</Text>
                      </View>
                    ) : (
                      <View>
                        <View style={[styles.reply, { borderColor: p.border, backgroundColor: p.surface }]}>
                          <Text style={[styles.h3, { color: p.ink }]}>{m.reply.head}</Text>
                          <Text style={[styles.body, { color: p.inkSoft, marginTop: 8 }]}>{m.reply.body}</Text>
                          <WhyToggle sanskrit={m.reply.sanskrit}>{m.reply.why}</WhyToggle>
                        </View>
                        <View style={{ flexDirection: 'row', gap: 6, marginTop: 8, paddingLeft: 4 }}>
                          {['Tell me more', 'A different angle'].map(c => (
                            <Pressable key={c} onPress={() => ask(c)} style={[styles.followChip, { borderColor: p.gold, backgroundColor: p.goldSoft }]}>
                              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, color: p.gold }}>{c}</Text>
                            </Pressable>
                          ))}
                        </View>
                      </View>
                    )}
                  </View>
                ))}

                {typing && <TypingDots color={p.gold} />}

                {limit && !typing && (
                  <View style={[styles.reply, { borderColor: p.gold, backgroundColor: p.surface, marginTop: 8 }]}>
                    <Text style={[styles.kicker, { color: p.gold, marginBottom: 8 }]}>Daily limit reached</Text>
                    <Text style={[styles.h3, { color: p.ink }]}>You've used your 3 questions today.</Text>
                    <Text style={[styles.body, { color: p.inkSoft, marginTop: 8 }]}>
                      Myastro+ removes the cap. ₹49/week or ₹199/month.
                    </Text>
                    <Pressable onPress={goPaywall} style={[styles.unlock, { backgroundColor: p.gold }]}>
                      <Text style={{ fontFamily: fonts.sansMedium, fontSize: 14, color: '#1a1408' }}>Unlock unlimited</Text>
                    </Pressable>
                  </View>
                )}
              </>
            ) : (
              <View>
                <Text style={[styles.kicker, { color: p.gold, marginBottom: 10 }]}>Decide · quick yes/no</Text>
                <Text style={[styles.lead, { color: p.ink }]}>Should I do X{'\n'}right now?</Text>
                <Text style={[styles.body, { color: p.inkSoft, marginTop: 10 }]}>
                  One line in. One verdict + one warm line back. Use it for the small decisions.
                </Text>

                <View style={[styles.inputCard, { borderColor: p.border, backgroundColor: p.surface }]}>
                  <TextInput
                    value={decideQ}
                    onChangeText={setDecideQ}
                    placeholder="Should I…"
                    placeholderTextColor={p.inkMute}
                    style={[styles.input, { color: p.ink }]}
                    editable={!limit}
                    onSubmitEditing={() => decide(decideQ)}
                    returnKeyType="go"
                  />
                  <Pressable onPress={() => decide(decideQ)} style={[styles.decideBtn, { backgroundColor: p.ink, opacity: decideQ.trim() && !limit ? 1 : 0.6 }]}>
                    <Text style={{ color: p.bg0, fontFamily: fonts.sansMedium, fontSize: 14 }}>Decide</Text>
                  </Pressable>
                </View>

                {!decideResult && (
                  <>
                    <Text style={[styles.kicker, { color: p.inkMute, marginTop: 22, marginBottom: 8 }]}>Try one</Text>
                    <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6 }}>
                      {DECIDE_TRY.map(s => (
                        <Pressable key={s} onPress={() => setDecideQ(s)} style={[styles.tryChip, { borderColor: p.border, backgroundColor: p.surface }]}>
                          <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, color: p.inkSoft }}>{s}</Text>
                        </Pressable>
                      ))}
                    </View>
                  </>
                )}

                {decideResult && <VerdictCard result={decideResult} onReset={() => { setDecideResult(null); setDecideQ(''); }} onMore={() => setMode('ask')} />}
              </View>
            )}
          </ScrollView>

          {mode === 'ask' && (
            <View style={[styles.composer, { borderTopColor: p.hairline }]}>
              <TextInput
                value={input}
                onChangeText={setInput}
                placeholder={limit ? 'Daily limit reached' : 'Ask anything…'}
                placeholderTextColor={p.inkMute}
                editable={!limit}
                style={[styles.input, { color: p.ink, flex: 1, opacity: limit ? 0.5 : 1 }]}
                onSubmitEditing={() => input.trim() && ask(input.trim())}
                returnKeyType="send"
              />
              <Pressable onPress={() => input.trim() && ask(input.trim())} style={[styles.sendBtn, { backgroundColor: p.ink }]}>
                <Icon name="send" size={18} color={p.bg0} />
              </Pressable>
            </View>
          )}
        </KeyboardAvoidingView>
      </Animated.View>
    </View>
  );
}

function Quota({ used }: { used: number }) {
  const { p } = useTheme();
  const remaining = Math.max(0, QUOTA - used);
  return (
    <View style={{ flexDirection: 'row', gap: 5, alignItems: 'center' }}>
      {Array.from({ length: QUOTA }).map((_, i) => (
        <View key={i} style={{
          width: 8, height: 8, borderRadius: 4,
          backgroundColor: i < remaining ? p.gold : 'transparent',
          borderWidth: 1, borderColor: i < remaining ? p.gold : p.borderStrong,
        }} />
      ))}
      <Text style={{ fontFamily: fonts.sansMedium, fontSize: 10, color: p.inkMute, letterSpacing: 1, marginLeft: 4 }}>{remaining}/{QUOTA}</Text>
    </View>
  );
}

function TypingDots({ color }: { color: string }) {
  return (
    <View style={{ flexDirection: 'row', gap: 6, padding: 12 }}>
      {[0, 1, 2].map(i => <Dot key={i} color={color} delay={i * 200} />)}
    </View>
  );
}
function Dot({ color, delay }: { color: string; delay: number }) {
  const o = useSharedValue(0.25);
  useEffect(() => {
    const t = setTimeout(() => {
      o.value = withTiming(1, { duration: 600, easing: Easing.inOut(Easing.sin) });
    }, delay);
    return () => clearTimeout(t);
  }, []);
  const a = useAnimatedStyle(() => ({ opacity: o.value }));
  return <Animated.View style={[{ width: 6, height: 6, borderRadius: 3, backgroundColor: color }, a]} />;
}

const VERDICT_LABEL: Record<Verdict, string> = { yes: 'Yes', wait: 'Wait', gentle: 'Proceed gently' };
function VerdictCard({ result, onReset, onMore }: {
  result: { q: string; verdict: Verdict; line: string }; onReset: () => void; onMore: () => void;
}) {
  const { p } = useTheme();
  const color = result.verdict === 'yes' ? p.gold : result.verdict === 'wait' ? p.inkMute : p.teal;
  const bg = result.verdict === 'yes' ? p.goldSoft : result.verdict === 'gentle' ? 'rgba(124,182,173,0.08)' : p.surface;
  return (
    <View style={[styles.reply, { borderColor: p.border, backgroundColor: p.surface, marginTop: 16 }]}>
      <Text style={[styles.kicker, { color: p.inkMute }]}>You asked</Text>
      <Text style={[styles.h3, { color: p.ink, marginTop: 4 }]}>"{result.q}"</Text>
      <View style={[styles.verdictPill, { borderColor: color, backgroundColor: bg, marginTop: 14 }]}>
        <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, color, letterSpacing: 1.8, textTransform: 'uppercase' }}>{VERDICT_LABEL[result.verdict]}</Text>
      </View>
      <Text style={[styles.body, { color: p.ink, marginTop: 14 }]}>{result.line}</Text>
      <View style={{ flexDirection: 'row', gap: 8, marginTop: 18 }}>
        <Pressable onPress={onReset} style={[styles.ghostBtn, { borderColor: p.border }]}>
          <Text style={{ fontFamily: fonts.sansMedium, fontSize: 12, color: p.ink }}>Ask another</Text>
        </Pressable>
        <Pressable onPress={onMore} style={[styles.ghostBtn, { borderColor: p.borderStrong }]}>
          <Text style={{ fontFamily: fonts.sansMedium, fontSize: 12, color: p.ink }}>Tell me more →</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  sheet: {
    position: 'absolute', left: 0, right: 0, bottom: 0, height: '90%',
    borderTopLeftRadius: 28, borderTopRightRadius: 28, borderWidth: 1, overflow: 'hidden',
  },
  grabberWrap: { alignItems: 'center', paddingTop: 10, paddingBottom: 6 },
  grabber: { width: 36, height: 4, borderRadius: 2, opacity: 0.6 },
  header: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    paddingHorizontal: 18, paddingBottom: 14, borderBottomWidth: 1,
  },
  orbMini: { width: 28, height: 28, borderRadius: 14 },
  seg: { flexDirection: 'row', padding: 3, borderRadius: radii.pill, borderWidth: 1, flex: 1 },
  segBtn: { flex: 1, alignItems: 'center', paddingVertical: 7, borderRadius: radii.pill },
  x: { width: 32, height: 32, borderRadius: 16, borderWidth: 1, alignItems: 'center', justifyContent: 'center' },
  lead: { fontFamily: fonts.sansMedium, fontSize: 30, lineHeight: 33, letterSpacing: -0.5 },
  kicker: { fontFamily: fonts.sansMedium, fontSize: 10, letterSpacing: 2.2, textTransform: 'uppercase' },
  body: { fontFamily: fonts.sans, fontSize: 13, lineHeight: 20 },
  small: { fontFamily: fonts.sans, fontSize: 12 },
  h3: { fontFamily: fonts.sansMedium, fontSize: 18, lineHeight: 23 },
  decideCta: { flexDirection: 'row', alignItems: 'center', gap: 12, marginTop: 18, padding: 14, borderWidth: 1, borderRadius: radii.md },
  decideIcon: { width: 32, height: 32, borderRadius: 10, borderWidth: 1, alignItems: 'center', justifyContent: 'center' },
  suggest: { flexDirection: 'row', alignItems: 'center', padding: 14, borderWidth: 1, borderRadius: radii.md, marginBottom: 6 },
  bubbleMe: {
    fontFamily: fonts.sans, fontSize: 14, lineHeight: 19,
    paddingHorizontal: 16, paddingVertical: 11, borderRadius: 16, borderBottomRightRadius: 4,
    maxWidth: '80%', overflow: 'hidden',
  },
  reply: { padding: 16, borderWidth: 1, borderRadius: radii.md, borderTopLeftRadius: 4 },
  followChip: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: radii.pill, borderWidth: 1 },
  verdictPill: { alignSelf: 'flex-start', paddingHorizontal: 14, paddingVertical: 6, borderWidth: 1, borderRadius: radii.pill },
  inputCard: { marginTop: 18, padding: 4, borderWidth: 1, borderRadius: radii.md },
  input: { fontFamily: fonts.sans, fontSize: 16, paddingHorizontal: 12, paddingVertical: 12 },
  decideBtn: { marginTop: 6, paddingVertical: 13, borderRadius: radii.sm, alignItems: 'center' },
  tryChip: { paddingHorizontal: 12, paddingVertical: 8, borderRadius: radii.pill, borderWidth: 1 },
  unlock: { marginTop: 14, paddingVertical: 13, borderRadius: radii.pill, alignItems: 'center' },
  ghostBtn: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: radii.pill, borderWidth: 1 },
  composer: { flexDirection: 'row', gap: 8, padding: 12, borderTopWidth: 1, alignItems: 'center' },
  sendBtn: { width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
});
