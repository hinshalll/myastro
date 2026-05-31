import { View, Text } from 'react-native';
import { router } from 'expo-router';
import Svg, { Circle } from 'react-native-svg';
import { useTheme } from '@/constants/ThemeContext';
import { fonts } from '@/constants/theme';
import { SubScreen, Body, Kicker, Mono, Btn, Icon } from '@/components/ui';
import ConstellationBG from '@/components/ConstellationBG';
import type { IconName } from '@/components/Icon';

const GLASS = 'rgba(8,7,14,0.78)';
const GBORDER = 'rgba(255,255,255,0.10)';

export default function Widget() {
  const { p } = useTheme();
  return (
    <SubScreen title="Home screen widget" scroll={false}>
      <View style={{ paddingHorizontal: 22, paddingBottom: 10 }}>
        <Body>See your daily vibe without opening the app.</Body>
      </View>

      <View style={{ flex: 1, marginHorizontal: 14, borderRadius: 28, padding: 18, paddingTop: 32, overflow: 'hidden', borderWidth: 1, borderColor: p.border, backgroundColor: '#1f1230' }}>
        <ConstellationBG seed={9} density={40} opacity={0.4} color="#ece6d4" />

        <View style={{ alignItems: 'center' }}>
          <Text style={{ fontFamily: fonts.sansMedium, fontSize: 10, letterSpacing: 2.2, color: 'rgba(236,230,212,0.6)' }}>FRI · MAY 25</Text>
          <Text style={{ fontFamily: fonts.sansMedium, fontSize: 56, lineHeight: 60, color: 'rgba(236,230,212,0.92)' }}>9:42</Text>
        </View>

        <View style={{ marginTop: 32, flexDirection: 'row', flexWrap: 'wrap', gap: 10 }}>
          <View style={{ width: '47%', aspectRatio: 1, borderRadius: 18, padding: 14, justifyContent: 'space-between', backgroundColor: GLASS, borderWidth: 1, borderColor: GBORDER }}>
            <Kicker color="rgba(236,230,212,0.7)" style={{ fontSize: 9 }}>Today</Kicker>
            <View>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 30, lineHeight: 32, color: '#f0e2bd' }}>Magnetic.</Text>
              <Text style={{ fontFamily: fonts.sans, fontSize: 10, lineHeight: 13, color: 'rgba(236,230,212,0.65)', marginTop: 6 }}>Send the half-finished idea.</Text>
            </View>
          </View>

          <View style={{ width: '47%', aspectRatio: 1, borderRadius: 18, padding: 14, justifyContent: 'space-between', backgroundColor: GLASS, borderWidth: 1, borderColor: GBORDER }}>
            <Kicker color="rgba(236,230,212,0.7)" style={{ fontSize: 9 }}>Ritual</Kicker>
            <View>
              <Mono color={p.gold}>day 8 / 21</Mono>
              <View style={{ marginTop: 6, height: 3, borderRadius: 2, backgroundColor: 'rgba(255,255,255,0.10)' }}>
                <View style={{ width: '38%', height: '100%', borderRadius: 2, backgroundColor: p.gold }} />
              </View>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 11, lineHeight: 14, color: 'rgba(236,230,212,0.9)', marginTop: 8 }}>Light a lamp at sunset.</Text>
            </View>
          </View>

          <View style={{ width: '100%', borderRadius: 18, padding: 14, flexDirection: 'row', alignItems: 'center', gap: 14, backgroundColor: GLASS, borderWidth: 1, borderColor: GBORDER }}>
            <Ring value={0.78} color={p.gold} />
            <View style={{ flex: 1 }}>
              <Kicker color="rgba(236,230,212,0.7)" style={{ fontSize: 9 }}>Good times today</Kicker>
              <Text style={{ fontFamily: fonts.sansMedium, fontSize: 13, color: 'rgba(236,230,212,0.95)', marginTop: 2 }}>12 – 4 pm · then 7 – 10 pm</Text>
            </View>
          </View>
        </View>

        {/* Mock dock */}
        <View style={{ position: 'absolute', left: 24, right: 24, bottom: 14, height: 56, borderRadius: 18, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around', backgroundColor: 'rgba(8,7,14,0.45)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.06)' }}>
          {(['phone', 'search', 'bell', 'home'] as IconName[]).map(i => (
            <View key={i} style={{ width: 38, height: 38, borderRadius: 10, backgroundColor: 'rgba(255,255,255,0.06)', alignItems: 'center', justifyContent: 'center' }}>
              <Icon name={i} size={16} color="rgba(255,255,255,0.7)" />
            </View>
          ))}
        </View>
      </View>

      <View style={{ paddingHorizontal: 22, paddingTop: 14, paddingBottom: 8, flexDirection: 'row', gap: 8 }}>
        <Btn label="Add to home screen" variant="primary" style={{ flex: 1 }} />
        <Btn label="Done" variant="ghost" onPress={() => router.back()} />
      </View>
    </SubScreen>
  );
}

function Ring({ value, color }: { value: number; color: string }) {
  const size = 44, r = size / 2 - 4, c = 2 * Math.PI * r;
  return (
    <Svg width={size} height={size}>
      <Circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth={3} />
      <Circle
        cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={3} strokeLinecap="round"
        strokeDasharray={`${c * value} ${c}`} transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
    </Svg>
  );
}
