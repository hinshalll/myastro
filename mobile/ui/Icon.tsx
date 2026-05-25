import React from 'react';
import Svg, { Circle, Path, Rect, G } from 'react-native-svg';
import { useTheme } from '@/theme/theme';

export type IconName =
  | 'sun' | 'moon' | 'today' | 'people' | 'explore' | 'you' | 'ask' | 'chevron'
  | 'back' | 'close' | 'plus' | 'star' | 'sparkle' | 'settings' | 'lock' | 'flame'
  | 'leaf' | 'eye' | 'hand' | 'card' | 'number' | 'calendar' | 'search' | 'heart'
  | 'home' | 'share' | 'edit' | 'bell' | 'globe' | 'check' | 'wand' | 'map'
  | 'send' | 'info' | 'logo';

type Props = { name: IconName; size?: number; stroke?: number; color?: string };

export const Icon = ({ name, size = 22, stroke = 1.6, color }: Props) => {
  const { c } = useTheme();
  const s = color ?? c.ink;
  const common = {
    fill: 'none' as const,
    stroke: s,
    strokeWidth: stroke,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
  };
  const box = { width: size, height: size, viewBox: '0 0 24 24' };

  switch (name) {
    case 'sun':
      return <Svg {...box}><Circle cx="12" cy="12" r="4" {...common} /><Path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4 7 17M17 7l1.4-1.4" {...common} /></Svg>;
    case 'moon':
      return <Svg {...box}><Path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z" {...common} /></Svg>;
    case 'today':
      return <Svg {...box}><Circle cx="12" cy="12" r="9" {...common} /><Path d="M12 7v5l3 2" {...common} /></Svg>;
    case 'people':
      return <Svg {...box}><Circle cx="9" cy="9" r="3.4" {...common} /><Path d="M3.5 19a5.5 5.5 0 0 1 11 0" {...common} /><Circle cx="17" cy="8" r="2.5" {...common} /><Path d="M15.5 19a4.5 4.5 0 0 1 6 0" {...common} /></Svg>;
    case 'explore':
      return <Svg {...box}><Circle cx="12" cy="12" r="9" {...common} /><Path d="m15.5 8.5-2 5-5 2 2-5z" {...common} /></Svg>;
    case 'you':
      return <Svg {...box}><Circle cx="12" cy="8" r="3.6" {...common} /><Path d="M5 20a7 7 0 0 1 14 0" {...common} /></Svg>;
    case 'ask':
      return <Svg {...box}><Path d="M9 9a3 3 0 1 1 4.5 2.6c-.9.5-1.5 1.2-1.5 2.4" {...common} /><Circle cx="12" cy="17.5" r="0.4" fill={s} /></Svg>;
    case 'chevron':
      return <Svg {...box}><Path d="m9 6 6 6-6 6" {...common} /></Svg>;
    case 'back':
      return <Svg {...box}><Path d="m14 6-6 6 6 6" {...common} /></Svg>;
    case 'close':
      return <Svg {...box}><Path d="M6 6l12 12M18 6 6 18" {...common} /></Svg>;
    case 'plus':
      return <Svg {...box}><Path d="M12 5v14M5 12h14" {...common} /></Svg>;
    case 'star':
      return <Svg {...box}><Path d="m12 3 2.7 6 6.3.5-4.8 4 1.5 6.2L12 16.5 6.3 19.7 7.8 13.5 3 9.5l6.3-.5z" {...common} /></Svg>;
    case 'sparkle':
      return <Svg {...box}><Path d="M12 3v5M12 16v5M3 12h5M16 12h5M6 6l3 3M15 15l3 3M6 18l3-3M15 9l3-3" {...common} /></Svg>;
    case 'settings':
      return <Svg {...box}><Circle cx="12" cy="12" r="3" {...common} /><Path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" {...common} /></Svg>;
    case 'lock':
      return <Svg {...box}><Rect x="4.5" y="10.5" width="15" height="10" rx="2" {...common} /><Path d="M8 10.5V7a4 4 0 0 1 8 0v3.5" {...common} /></Svg>;
    case 'flame':
      return <Svg {...box}><Path d="M12 3c1 3.5 4 4.5 4 8a4 4 0 0 1-8 0c0-1.5.5-2.5 1.5-3.5C10.5 8 11.5 6 12 3z" {...common} /><Path d="M12 13c.5 1 1.5 1.5 1.5 3a1.5 1.5 0 0 1-3 0c0-1 .8-1.7 1.5-3z" {...common} /></Svg>;
    case 'leaf':
      return <Svg {...box}><Path d="M4 20s2-8 8-12 8-4 8-4-1 9-5 13-11 3-11 3z" {...common} /><Path d="M4 20 14 10" {...common} /></Svg>;
    case 'eye':
      return <Svg {...box}><Path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" {...common} /><Circle cx="12" cy="12" r="3" {...common} /></Svg>;
    case 'hand':
      return <Svg {...box}><Path d="M9 11V5.5a1.5 1.5 0 1 1 3 0V11" {...common} /><Path d="M12 11V4.5a1.5 1.5 0 1 1 3 0V11" {...common} /><Path d="M15 11V6.5a1.5 1.5 0 1 1 3 0V13" {...common} /><Path d="M9 11V8.5a1.5 1.5 0 1 0-3 0V15c0 3 2 6 6 6s6-2.5 6-6" {...common} /></Svg>;
    case 'card':
      return <Svg {...box}><Rect x="6" y="3" width="12" height="18" rx="2" {...common} /><Path d="M9 8h6M9 12h6M9 16h3" {...common} /></Svg>;
    case 'number':
      return <Svg {...box}><Path d="M5 9h14M5 15h14M10 4 8 20M16 4l-2 16" {...common} /></Svg>;
    case 'calendar':
      return <Svg {...box}><Rect x="4" y="5" width="16" height="16" rx="2" {...common} /><Path d="M4 10h16M9 3v4M15 3v4" {...common} /></Svg>;
    case 'search':
      return <Svg {...box}><Circle cx="11" cy="11" r="6" {...common} /><Path d="m20 20-4-4" {...common} /></Svg>;
    case 'heart':
      return <Svg {...box}><Path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z" {...common} /></Svg>;
    case 'home':
      return <Svg {...box}><Path d="M3 10 12 3l9 7v10a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z" {...common} /></Svg>;
    case 'share':
      return <Svg {...box}><Circle cx="6" cy="12" r="2.5" {...common} /><Circle cx="18" cy="6" r="2.5" {...common} /><Circle cx="18" cy="18" r="2.5" {...common} /><Path d="m8 11 8-4M8 13l8 4" {...common} /></Svg>;
    case 'edit':
      return <Svg {...box}><Path d="M4 20h4l11-11-4-4L4 16z" {...common} /><Path d="m13.5 6.5 4 4" {...common} /></Svg>;
    case 'bell':
      return <Svg {...box}><Path d="M6 9a6 6 0 0 1 12 0c0 7 3 7 3 9H3c0-2 3-2 3-9z" {...common} /><Path d="M10 21a2 2 0 0 0 4 0" {...common} /></Svg>;
    case 'globe':
      return <Svg {...box}><Circle cx="12" cy="12" r="9" {...common} /><Path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" {...common} /></Svg>;
    case 'check':
      return <Svg {...box}><Path d="m5 12 5 5L20 7" {...common} /></Svg>;
    case 'wand':
      return <Svg {...box}><Path d="m5 19 11-11" {...common} /><Path d="m15 5 3 3" {...common} /><Path d="M18 13v3M21 14.5h-3M5 5v3M7 6.5H4" {...common} /></Svg>;
    case 'map':
      return <Svg {...box}><Path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3z" {...common} /><Path d="M9 3v15M15 6v15" {...common} /></Svg>;
    case 'send':
      return <Svg {...box}><Path d="m4 12 17-8-5 18-3-7z" {...common} /><Path d="M11 13 4 12" {...common} /></Svg>;
    case 'info':
      return <Svg {...box}><Circle cx="12" cy="12" r="9" {...common} /><Path d="M12 8v1M12 11v6" {...common} /></Svg>;
    case 'logo':
      return (
        <Svg width={size} height={size} viewBox="0 0 40 40">
          <Circle cx="20" cy="20" r="14" fill="none" stroke={s} strokeWidth="1.4" />
          <Path d="M12 22c4-1 6-5 8-12 2 7 4 11 8 12-4 1-6 5-8 12-2-7-4-11-8-12z" fill={s} fillOpacity={0.15} stroke={s} strokeWidth="1.4" />
        </Svg>
      );
    default:
      return null;
  }
};
