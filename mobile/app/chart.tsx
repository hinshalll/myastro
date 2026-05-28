import { View, Text } from 'react-native';
import Svg, { Circle, Line, G, Text as SvgText } from 'react-native-svg';
import { useTheme } from '@/constants/ThemeContext';
import { SubScreen, Card, CardStrong, Body, Mono, Kicker, Display, AppBarIconBtn } from '@/components/ui';
import WhyToggle from '@/components/WhyToggle';

const PLANETS = [
  { sym: '☉', a: 35, r: 38, c: '#e6c373' },
  { sym: '☽', a: 110, r: 38, c: '#cdd0e0' },
  { sym: '♀', a: 65, r: 32, c: '#d28798' },
  { sym: '♂', a: 180, r: 38, c: '#c46462' },
  { sym: '♃', a: 230, r: 34, c: '#d4ad55' },
  { sym: '♄', a: 290, r: 38, c: '#6a7180' },
  { sym: '☿', a: 50, r: 34, c: '#7cb6ad' },
];

const SECTIONS = [
  { title: 'You at the core', body: 'A slow-burning fire. Patient, persistent, surprisingly fierce when something matters.', sanskrit: 'लग्न-स्वामी कुम्भे · दशा-शनि' },
  { title: 'How you love', body: "You don't fall fast. You fall once and stay. Loyalty feels easy; novelty feels expensive.", sanskrit: 'शुक्रः वृश्चिक-राशौ' },
  { title: 'How you work', body: "You need long stretches of quiet. Open offices wreck you. Mornings before everyone's awake — that's when you're sharpest.", sanskrit: 'दशम-स्वामी एकादशे' },
  { title: 'Where you wobble', body: "You hide when you're hurt. By the time anyone notices, you've been alone in it for weeks.", sanskrit: 'चन्द्रः द्वादशे' },
];

export default function Chart() {
  const { p } = useTheme();
  return (
    <SubScreen title="Your chart" right={<AppBarIconBtn icon="share" />}>
      <View style={{ paddingHorizontal: 22, paddingTop: 8 }}>
        <CardStrong style={{ padding: 18, alignItems: 'center' }}>
          <Kicker>A picture of you</Kicker>
          <Svg width={240} height={240} viewBox="0 0 100 100" style={{ marginVertical: 14 }}>
            <Circle cx={50} cy={50} r={46} fill="none" stroke={p.gold} strokeWidth={0.4} opacity={0.5} />
            <Circle cx={50} cy={50} r={36} fill="none" stroke={p.gold} strokeWidth={0.3} opacity={0.35} />
            <Circle cx={50} cy={50} r={22} fill="none" stroke={p.gold} strokeWidth={0.3} opacity={0.25} />
            {Array.from({ length: 12 }).map((_, i) => {
              const a = ((i * 30 - 90) * Math.PI) / 180;
              return (
                <Line key={i}
                  x1={50 + 22 * Math.cos(a)} y1={50 + 22 * Math.sin(a)}
                  x2={50 + 46 * Math.cos(a)} y2={50 + 46 * Math.sin(a)}
                  stroke={p.gold} strokeWidth={0.25} opacity={0.35} />
              );
            })}
            {PLANETS.map((pl, i) => {
              const rad = ((pl.a - 90) * Math.PI) / 180;
              const x = 50 + pl.r * Math.cos(rad);
              const y = 50 + pl.r * Math.sin(rad);
              return (
                <G key={i}>
                  <Circle cx={x} cy={y} r={2.5} fill={pl.c} opacity={0.9} />
                  <SvgText x={x} y={y + 1} fontSize={3} fill={pl.c} textAnchor="middle">{pl.sym}</SvgText>
                </G>
              );
            })}
            <Circle cx={50} cy={50} r={2.5} fill={p.gold} />
          </Svg>
          <Mono>tap a star · why →</Mono>
        </CardStrong>

        <Head title="In plain English" />
        {SECTIONS.map(c => (
          <Card key={c.title} style={{ padding: 18, marginBottom: 8 }}>
            <Display size={19}>{c.title}</Display>
            <Body style={{ marginTop: 8 }}>{c.body}</Body>
            <WhyToggle sanskrit={c.sanskrit}>
              Read off your Ascendant lord, Moon's nakshatra, and the angle between Mars and Saturn — all in your "deep work" houses.
            </WhyToggle>
          </Card>
        ))}
      </View>
    </SubScreen>
  );
}

function Head({ title }: { title: string }) {
  const { p } = useTheme();
  return <Text style={{ fontFamily: 'HankenGrotesk_500Medium', fontSize: 11, letterSpacing: 1.8, textTransform: 'uppercase', color: p.inkMute, paddingVertical: 14, paddingTop: 28 }}>{title}</Text>;
}
