import React, { useState } from 'react';
import { View, Pressable, StyleProp, ViewStyle, TextStyle } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import { Text } from 'react-native';
import { fonts, radius, useTheme } from '@/theme/theme';
import { Icon, IconName } from '@/ui/Icon';
import { Body, Deva } from '@/ui/Type';

// ── Card ──
export const Card = ({ strong, style, children }: { strong?: boolean; style?: StyleProp<ViewStyle>; children?: React.ReactNode }) => {
  const { c } = useTheme();
  return (
    <View style={[{
      backgroundColor: strong ? c.surfaceStrong : c.surface,
      borderWidth: 1,
      borderColor: strong ? c.borderStrong : c.border,
      borderRadius: radius.md,
    }, style]}>{children}</View>
  );
};

// ── Hairline divider ──
export const Hr = ({ style }: { style?: StyleProp<ViewStyle> }) => {
  const { c } = useTheme();
  return <View style={[{ height: 1, backgroundColor: c.hairline }, style]} />;
};

// ── Chip / pill ──
export const Chip = ({ label, active, gold, onPress, style }: {
  label: string; active?: boolean; gold?: boolean; onPress?: () => void; style?: StyleProp<ViewStyle>;
}) => {
  const { c } = useTheme();
  const bg = active ? c.ink : gold ? c.goldSoft : c.surface;
  const bd = active ? c.ink : gold ? c.gold : c.border;
  const fg = active ? c.bg0 : gold ? c.gold : c.inkSoft;
  return (
    <Pressable onPress={onPress} style={[{
      paddingHorizontal: 12, paddingVertical: 6, borderRadius: 999,
      backgroundColor: bg, borderWidth: 1, borderColor: bd,
      alignSelf: 'flex-start',
    }, style]}>
      <Text style={{ fontFamily: fonts.sans500, fontSize: 11, color: fg, letterSpacing: 0.2 }}>{label}</Text>
    </Pressable>
  );
};

// ── Button ──
type BtnVariant = 'default' | 'primary' | 'gold' | 'ghost';
export const Button = ({ title, variant = 'default', size = 'md', block, icon, onPress, style }: {
  title: string; variant?: BtnVariant; size?: 'sm' | 'md' | 'lg'; block?: boolean; icon?: IconName; onPress?: () => void; style?: StyleProp<ViewStyle>;
}) => {
  const { c } = useTheme();
  const pad = size === 'sm' ? { paddingVertical: 8, paddingHorizontal: 14 } : size === 'lg' ? { paddingVertical: 17, paddingHorizontal: 24 } : { paddingVertical: 13, paddingHorizontal: 22 };
  const fontSize = size === 'sm' ? 12 : size === 'lg' ? 15 : 14;
  let bg = 'transparent', bd = c.borderStrong, fg = c.ink;
  if (variant === 'primary') { bg = c.ink; bd = c.ink; fg = c.bg0; }
  else if (variant === 'gold') { bg = c.gold; bd = c.gold; fg = '#1a1408'; }
  else if (variant === 'ghost') { bd = c.border; }
  return (
    <Pressable onPress={onPress} style={({ pressed }) => [{
      ...pad, borderRadius: 999, borderWidth: 1, borderColor: bd, backgroundColor: bg,
      flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
      width: block ? '100%' : undefined, opacity: pressed ? 0.85 : 1,
    }, style]}>
      {icon && <Icon name={icon} size={fontSize + 2} color={fg} />}
      <Text style={{ fontFamily: fonts.sans500, fontSize, color: fg }}>{title}</Text>
    </Pressable>
  );
};

// ── App bar ──
export const AppBar = ({ title, onBack, right }: { title?: string; onBack?: () => void; right?: React.ReactNode }) => {
  const { c } = useTheme();
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 18, paddingTop: 6, paddingBottom: 4 }}>
      {onBack ? (
        <Pressable onPress={onBack} style={{ width: 36, height: 36, borderRadius: 18, borderWidth: 1, borderColor: c.border, alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="back" size={18} />
        </Pressable>
      ) : <View style={{ width: 36 }} />}
      <Text style={{ fontFamily: fonts.sans500, fontSize: 14, color: c.ink, letterSpacing: 0.5 }}>{title}</Text>
      <View style={{ width: 36, alignItems: 'flex-end' }}>{right ?? null}</View>
    </View>
  );
};

// round icon button used in app bars
export const IconButton = ({ name, onPress }: { name: IconName; onPress?: () => void }) => {
  const { c } = useTheme();
  return (
    <Pressable onPress={onPress} style={{ width: 36, height: 36, borderRadius: 18, borderWidth: 1, borderColor: c.border, alignItems: 'center', justifyContent: 'center' }}>
      <Icon name={name} size={16} />
    </Pressable>
  );
};

// ── Section header ──
export const Section = ({ title, more, onMore, children }: { title?: string; more?: string; onMore?: () => void; children?: React.ReactNode }) => {
  const { c } = useTheme();
  return (
    <>
      {title ? (
        <View style={{ flexDirection: 'row', alignItems: 'baseline', justifyContent: 'space-between', paddingHorizontal: 22, paddingTop: 28, paddingBottom: 12 }}>
          <Text style={{ fontFamily: fonts.sans500, fontSize: 11, letterSpacing: 2, textTransform: 'uppercase', color: c.inkMute }}>{title}</Text>
          {more ? <Text onPress={onMore} style={{ fontFamily: fonts.sans500, fontSize: 11, color: c.inkMute }}>{more}</Text> : null}
        </View>
      ) : null}
      {children}
    </>
  );
};

// ── Avatar ──
export const Avatar = ({ initials, size = 40 }: { initials: string; size?: number }) => {
  const { c } = useTheme();
  return (
    <View style={{ width: size, height: size, borderRadius: size / 2, backgroundColor: c.surfaceStrong, borderWidth: 1, borderColor: c.border, alignItems: 'center', justifyContent: 'center' }}>
      <Text style={{ fontFamily: fonts.sans500, fontSize: size * 0.35, color: c.ink }}>{initials}</Text>
    </View>
  );
};

// ── Vibe ring (circular gauge) ──
export const VibeRing = ({ value = 0.72, size = 96, label, color }: { value?: number; size?: number; label?: string; color?: string }) => {
  const { c } = useTheme();
  const col = color ?? c.gold;
  const r = size / 2 - 8;
  const circ = 2 * Math.PI * r;
  const dash = circ * value;
  return (
    <View style={{ width: size, height: size }}>
      <Svg width={size} height={size}>
        <Circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={c.ink} strokeOpacity={0.1} strokeWidth={3} />
        <Circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={col} strokeWidth={3} strokeLinecap="round"
          strokeDasharray={`${dash} ${circ}`} rotation={-90} originX={size / 2} originY={size / 2} />
      </Svg>
      {label ? (
        <View style={{ position: 'absolute', inset: 0, alignItems: 'center', justifyContent: 'center' }}>
          <Text style={{ fontFamily: fonts.displayItalic, fontSize: size * 0.32, color: c.ink }}>{label}</Text>
        </View>
      ) : null}
    </View>
  );
};

// ── Why? expandable detail ──
export const WhyToggle = ({ children, sanskrit }: { children?: React.ReactNode; sanskrit?: string }) => {
  const { c } = useTheme();
  const [open, setOpen] = useState(false);
  return (
    <View style={{ marginTop: 14 }}>
      <Pressable onPress={() => setOpen(o => !o)} style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
        <View style={{ width: 10, height: 1, backgroundColor: c.gold }} />
        <Text style={{ fontFamily: fonts.sans500, fontSize: 10, letterSpacing: 2, textTransform: 'uppercase', color: c.gold }}>why{open ? ' ⌄' : ' ›'}</Text>
      </Pressable>
      {open ? (
        <View style={{ marginTop: 10, paddingVertical: 12, borderTopWidth: 1, borderTopColor: c.hairline }}>
          {sanskrit ? <Deva style={{ marginBottom: 8, fontStyle: 'italic' }}>{sanskrit}</Deva> : null}
          {typeof children === 'string' ? <Body style={{ fontSize: 13 }}>{children}</Body> : children}
        </View>
      ) : null}
    </View>
  );
};

// ── Tiny "?" hint bubble ──
export const WhyTinyHint = ({ children, sanskrit }: { children?: React.ReactNode; sanskrit?: string }) => {
  const { c } = useTheme();
  const [open, setOpen] = useState(false);
  return (
    <View>
      <Pressable onPress={() => setOpen(o => !o)} style={{ width: 26, height: 26, borderRadius: 13, borderWidth: 1, borderColor: c.borderStrong, alignItems: 'center', justifyContent: 'center' }}>
        <Text style={{ fontFamily: fonts.displayItalic, fontSize: 12, color: c.inkMute }}>?</Text>
      </Pressable>
      {open ? (
        <Card style={{ position: 'absolute', right: 0, top: 32, width: 200, padding: 12, backgroundColor: c.bg1, zIndex: 5 }}>
          {sanskrit ? <Deva style={{ marginBottom: 4, fontStyle: 'italic' }}>{sanskrit}</Deva> : null}
          <Body style={{ fontSize: 12 }}>{children}</Body>
        </Card>
      ) : null}
    </View>
  );
};
