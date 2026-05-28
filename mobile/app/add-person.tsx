import { useState } from 'react';
import { View, Text, Pressable } from 'react-native';
import { router } from 'expo-router';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Card, Body, Small, Kicker, Display, Btn, Field, Input } from '@/components/ui';

export default function AddPerson() {
  const { p } = useTheme();
  const [mode, setMode] = useState<'invite' | 'manual'>('invite');
  const [closeness, setCloseness] = useState<'acquaintance' | 'close'>('acquaintance');

  return (
    <SubScreen title="Add a person">
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        {/* Mode switch */}
        <Card style={{ padding: 4, flexDirection: 'row', gap: 4 }}>
          {([['invite', 'Friend request', 'live · two-way'], ['manual', 'Manual chart', 'static · just compatibility']] as const).map(([k, l, sub]) => {
            const on = mode === k;
            return (
              <Pressable key={k} onPress={() => setMode(k)} style={{ flex: 1, paddingVertical: 10, borderRadius: 12, alignItems: 'center', backgroundColor: on ? p.ink : 'transparent' }}>
                <Text style={{ fontFamily: fonts.sansMedium, fontSize: 13, color: on ? p.bg0 : p.inkSoft }}>{l}</Text>
                <Text style={{ fontFamily: fonts.mono, fontSize: 8, marginTop: 3, color: on ? 'rgba(0,0,0,0.6)' : p.inkMute }}>{sub}</Text>
              </Pressable>
            );
          })}
        </Card>

        {mode === 'invite' ? (
          <View style={{ marginTop: 16 }}>
            <Card style={{ padding: 18 }}>
              <Display size={19}>They get to choose what they share back.</Display>
              <Body style={{ marginTop: 8 }}>
                Friend requests unlock live daily features — relationship weather, couple space, household grid. The other person controls their own privacy.
              </Body>
            </Card>

            <Field label="Send to" style={{ marginTop: 16 }}>
              <Input placeholder="Phone, email, or username" />
            </Field>

            <Card style={{ padding: 14, marginTop: 12 }}>
              <Body><Text style={{ color: p.gold, fontFamily: fonts.sansMedium }}>Preview  </Text>
                "Hey — I'm on Myastro. Want me to add you?" — they tap a link, fill in their own details.</Body>
            </Card>

            <Btn label="Send invite" variant="primary" size="lg" block style={{ marginTop: 16 }} onPress={() => router.back()} />
            <Small style={{ textAlign: 'center', marginTop: 10 }}>Free for your first 2 friends · Myastro+ for unlimited.</Small>

            <Kicker style={{ marginTop: 24, marginBottom: 10 }}>What they'll see (privacy tier)</Kicker>
            <Card style={{ padding: 4, flexDirection: 'row', gap: 4 }}>
              {([['acquaintance', 'Acquaintance', 'colleagues, your boss'], ['close', 'Close', 'partner, family']] as const).map(([k, l, sub]) => {
                const on = closeness === k;
                return (
                  <Pressable key={k} onPress={() => setCloseness(k)} style={{ flex: 1, padding: 12, borderRadius: 12, gap: 4, backgroundColor: on ? p.surfaceStrong : 'transparent' }}>
                    <Text style={{ fontFamily: fonts.sansMedium, fontSize: 13, color: p.ink }}>{l}</Text>
                    <Text style={{ fontFamily: fonts.mono, fontSize: 8, color: p.inkMute }}>{sub}</Text>
                  </Pressable>
                );
              })}
            </Card>
            <Small style={{ marginTop: 10 }}>
              {closeness === 'close'
                ? 'They see daily relationship weather + tension forecast + ritual nudges. Your mood logs and journal NEVER shareable.'
                : "They see general daily compatibility + basic elements only. Nothing they'd find awkward."}
            </Small>
          </View>
        ) : (
          <View style={{ marginTop: 16, gap: 14 }}>
            <Card style={{ padding: 14 }}>
              <Body>For someone <Text style={{ color: p.ink, fontFamily: fonts.sansMedium }}>not on Myastro</Text> — e.g. a prospective bride or groom, a child, a relative. Just compatibility & matchmaking; no live features.</Body>
            </Card>
            <Field label="Name"><Input placeholder="Their first name" /></Field>
            <Field label="Relationship"><Input defaultValue="Matchmaking" /></Field>
            <Field label="Born on"><Input defaultValue="1992-04-12" /></Field>
            <Field label="Born in"><Input defaultValue="Mumbai, India" /></Field>
            <Field label="Birth time (optional)"><Input defaultValue="06:30" /></Field>
            <Btn label="Save chart" variant="primary" size="lg" block onPress={() => router.back()} />
          </View>
        )}
      </View>
    </SubScreen>
  );
}
