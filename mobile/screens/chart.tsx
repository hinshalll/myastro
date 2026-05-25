import React, { useCallback, useEffect, useState } from 'react';
import { View, ActivityIndicator, Pressable } from 'react-native';
import { fonts, useTheme } from '@/theme/theme';
import { H1, H2, H3, Body, Small, Kicker, Mono } from '@/ui/Type';
import { Card, AppBar, Button, Hr } from '@/ui/primitives';
import { Icon } from '@/ui/Icon';
import { useNav } from '@/nav/NavContext';
import { PrecisionBanner } from '@/screens/today';
import { computeChart, ChartResult, BirthProfile, API_BASE } from '@/lib/api';

// Demo birth details (editable input comes next). New Delhi, 15 Aug 1990, 14:30.
const DEMO_PROFILE: BirthProfile = {
  name: 'You',
  date: '1990-08-15',
  time: '14:30',
  birth_time_known: true,
  exact_time: true,
  place: 'New Delhi',
  lat: 28.6139,
  lon: 77.209,
  tz: 'Asia/Kolkata',
  gender: 'M',
};

const PlacementCard = ({ icon, label, sign, sub }: { icon: any; label: string; sign: string; sub?: string }) => {
  const { c } = useTheme();
  return (
    <Card style={{ flex: 1, padding: 16 }}>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
        <Icon name={icon} size={16} color={c.gold} />
        <Kicker>{label}</Kicker>
      </View>
      <H3 style={{ marginTop: 8 }}>{sign}</H3>
      {sub ? <Small style={{ marginTop: 2 }}>{sub}</Small> : null}
    </Card>
  );
};

export const ChartScreen = () => {
  const { c } = useTheme();
  const { back } = useNav();
  const [data, setData] = useState<ChartResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await computeChart(DEMO_PROFILE);
      setData(res);
    } catch (e: any) {
      setError(e?.message ?? 'Could not reach the backend.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <View style={{ flex: 1 }}>
      <AppBar title="Your Chart · live" onBack={back} />

      {loading ? (
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', gap: 14, padding: 40 }}>
          <ActivityIndicator color={c.gold} />
          <Small>Computing your chart…</Small>
        </View>
      ) : error ? (
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', gap: 12, padding: 30 }}>
          <Icon name="info" size={26} color={c.rose} />
          <H3 style={{ textAlign: 'center' }}>Can&apos;t reach the chart engine</H3>
          <Body style={{ textAlign: 'center' }}>
            Make sure the backend is running and your phone is on the same Wi-Fi.{'\n'}Trying: {API_BASE}
          </Body>
          <Small style={{ textAlign: 'center', color: c.inkFaint }}>{error}</Small>
          <Button title="Try again" variant="gold" size="sm" onPress={load} />
        </View>
      ) : data ? (
        <View style={{ paddingHorizontal: 22, paddingTop: 4 }}>
          <PrecisionBanner tier={data.time_precision} />

          {/* Headline: Moon */}
          <View style={{ marginTop: 14, marginBottom: 4 }}>
            <Kicker style={{ marginBottom: 8 }}>Your Moon · the emotional core</Kicker>
            <H1>{data.moon ? `Moon in ${data.moon.sign}` : '—'}</H1>
            {data.moon ? <Body style={{ marginTop: 6 }}>{data.moon.nakshatra} · ruled by {data.moon.nakshatra_lord}</Body> : null}
          </View>

          {/* Sun + Ascendant */}
          <View style={{ flexDirection: 'row', gap: 10, marginTop: 14 }}>
            <PlacementCard icon="sun" label="Sun" sign={data.sun ? data.sun.sign : '—'} sub={data.sun?.nakshatra} />
            <PlacementCard
              icon="today"
              label="Rising"
              sign={data.ascendant_sign ?? 'Add birth time'}
              sub={data.ascendant_nakshatra ?? (data.houses_reliable ? undefined : 'unlocked with exact time')}
            />
          </View>

          {/* Planet table */}
          <Kicker style={{ marginTop: 26, marginBottom: 10 }}>The nine placements</Kicker>
          <Card style={{ paddingHorizontal: 4 }}>
            {data.planets.map((p, i) => (
              <View key={p.name} style={{ flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingVertical: 13, borderBottomWidth: i === data.planets.length - 1 ? 0 : 1, borderBottomColor: c.hairline }}>
                <View style={{ width: 78 }}>
                  <Body style={{ color: c.ink, fontFamily: fonts.sans500 }}>{p.name}</Body>
                  {p.retrograde ? <Mono style={{ color: c.rose, marginTop: 2 }}>retro</Mono> : null}
                </View>
                <View style={{ flex: 1 }}>
                  <Body style={{ color: c.ink }}>{p.sign}{p.house ? `  ·  house ${p.house}` : ''}</Body>
                  <Small style={{ marginTop: 2 }}>{p.nakshatra}</Small>
                </View>
                <Mono>{p.degree}</Mono>
              </View>
            ))}
          </Card>

          <Small style={{ marginTop: 16, color: c.inkFaint }}>
            Computed live by Swiss Ephemeris (sidereal · Lahiri). Demo birth details for now — your own input comes next.
          </Small>
          <View style={{ height: 24 }} />
        </View>
      ) : null}
    </View>
  );
};

// Minimal functional You tab (real design ported after the design is finalized)
export const YouScreen = () => {
  const { c } = useTheme();
  const { nav } = useNav();
  return (
    <View style={{ paddingHorizontal: 22, paddingTop: 6 }}>
      <H2 style={{ marginTop: 8 }}>You</H2>
      <Body style={{ marginTop: 4, marginBottom: 18 }}>Your chart, patterns, and life story.</Body>
      <Pressable onPress={() => nav('chart')}>
        <Card style={{ padding: 18, flexDirection: 'row', gap: 14, alignItems: 'center', borderColor: c.gold }}>
          <View style={{ width: 44, height: 44, borderRadius: 12, backgroundColor: c.goldSoft, borderWidth: 1, borderColor: c.gold, alignItems: 'center', justifyContent: 'center' }}>
            <Icon name="star" size={20} color={c.gold} />
          </View>
          <View style={{ flex: 1 }}>
            <Kicker gold>Live · real data</Kicker>
            <H3 style={{ marginTop: 2 }}>Your Chart</H3>
            <Small style={{ marginTop: 2 }}>Computed from real astronomy</Small>
          </View>
          <Icon name="chevron" size={18} color={c.inkMute} />
        </Card>
      </Pressable>
      <Small style={{ marginTop: 18, color: c.inkFaint }}>The rest of this tab (Life Chapters, Patterns, Purpose…) is ported once the design is finalized.</Small>
    </View>
  );
};
