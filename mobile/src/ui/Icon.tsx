// Icon.tsx — the prototype's inline line-icon set (astro.tsx PATHS) as react-native-svg.
// Paths copied verbatim; they render 1:1.
import React from "react";
import Svg, { Path } from "react-native-svg";
import { INK } from "./palette";

export const PATHS: Record<string, string[]> = {
  bell: ["M6 9a6 6 0 0 1 12 0c0 5 1.5 6 2 7H4c.5-1 2-2 2-7Z", "M9.5 20a2.5 2.5 0 0 0 5 0"],
  share: ["M12 14V4", "M8.5 7.5 12 4l3.5 3.5", "M6 11v7a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-7"],
  chevR: ["M9.5 6 15 12l-5.5 6"],
  chevD: ["M6 9.5 12 15l6-5.5"],
  chevU: ["M6 14.5 12 9l6 5.5"],
  plus: ["M12 5v14", "M5 12h14"],
  sync: ["M4 11a8 8 0 0 1 13.5-4.5L20 9", "M20 4v5h-5", "M20 13a8 8 0 0 1-13.5 4.5L4 15", "M4 20v-5h5"],
  capsule: ["M8 3h8a2 2 0 0 1 2 2v6l-6 10-6-10V5a2 2 0 0 1 2-2Z", "M6 9h12"],
  compass: ["M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z", "M15.5 8.5l-2 5-5 2 2-5 5-2Z"],
  wand: ["M5 19 16 8", "M17 4l1.2 2.8L21 8l-2.8 1.2L17 12l-1.2-2.8L13 8l2.8-1.2L17 4Z", "M6 14l1 1"],
  scan: ["M4 8V5a1 1 0 0 1 1-1h3", "M16 4h3a1 1 0 0 1 1 1v3", "M20 16v3a1 1 0 0 1-1 1h-3", "M8 20H5a1 1 0 0 1-1-1v-3", "M8 12h8"],
  arrowR: ["M4 12h15", "M14 7l5 5-5 5"],
  arrowL: ["M19 12H4", "M10 7l-5 5 5 5"],
  close: ["M6 6l12 12", "M18 6 6 18"],
  check: ["M5 12.5 9.5 17 19 7"],
  mic: ["M12 3a2.6 2.6 0 0 0-2.6 2.6v5.2a2.6 2.6 0 0 0 5.2 0V5.6A2.6 2.6 0 0 0 12 3Z", "M6 11a6 6 0 0 0 12 0", "M12 17v3.5"],
  send: ["M4 12 20 4l-6 16-3-7-7-1Z"],
  trash: ["M4 7h16", "M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2", "M6 7l1 13a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-13", "M10 11v6", "M14 11v6"],
  pause: ["M9 5v14", "M15 5v14"],
  clock: ["M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z", "M12 7v5l3 2"],
  today: ["M3 11l9-7 9 7v8a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"],
  timeline: ["M5 5h14", "M5 12h14", "M5 19h9"],
  people: ["M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z", "M3 20c0-3 2.7-5 6-5s6 2 6 5", "M17 11a2.6 2.6 0 1 0 0-5.2", "M16.5 15c2.6 0 4.5 1.8 4.5 4.5"],
  rituals: ["M12 3c3.5 3.8 5 6 5 9a5 5 0 0 1-10 0c0-2 1-3 2.4-4.2"],
  readings: ["M3 3h18v18H3z", "M12 3 21 12 12 21 3 12Z", "M3 3 21 21", "M21 3 3 21"],
  heart: ["M12 20.5C12 20.5 3.5 15 3.5 8.9 3.5 6.1 5.6 4 8.2 4c1.8 0 3.1 1 3.8 2.3C12.7 5 14 4 15.8 4c2.6 0 4.7 2.1 4.7 4.9C20.5 15 12 20.5 12 20.5Z"],
  work: ["M4 8h16v11a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z", "M9 8V6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"],
  coin: ["M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z", "M12 7v10", "M9.5 9.5h4a1.6 1.6 0 0 1 0 3.2h-3a1.6 1.6 0 0 0 0 3.2h4"],
  spark: ["M12 3v18", "M3 12h18", "M6 6l12 12", "M18 6 6 18"],
  user: ["M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z", "M5 20a7 7 0 0 1 14 0"],
  ring: ["M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z"],
  sun: ["M12 5a7 7 0 1 0 0 14 7 7 0 0 0 0-14Z", "M12 1v2", "M12 21v2", "M4.2 4.2l1.4 1.4", "M18.4 18.4l1.4 1.4", "M1 12h2", "M21 12h2", "M4.2 19.8l1.4-1.4", "M18.4 5.6l1.4-1.4"],
  moonp: ["M20 14.5A8 8 0 0 1 9.5 4 7 7 0 1 0 20 14.5Z"],
  leaf: ["M5 19c0-8 6-13 14-13 0 8-5 14-14 13Z", "M5 19c3-4 6-6 9-7"],
  target: ["M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z", "M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z", "M12 12h.01"],
  cal: ["M4 6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z", "M4 9h16", "M8 3v4", "M16 3v4"],
  moon: ["M20 14.5A8 8 0 0 1 9.5 4 7 7 0 1 0 20 14.5Z"],
  flame: ["M12 3c4 4.5 6 7 6 11a6 6 0 0 1-12 0c0-2.5 1.4-4.2 3.2-5.6.9 1.3 1.6 1.6 2.8.4.5-1.4.3-3.4 0-5.8Z"],
};

export function Icon({ n, d, s = 20, c = INK, sw = 1.7 }: { n?: string; d?: string | string[]; s?: number; c?: string; sw?: number }) {
  const paths = n ? (PATHS[n] || []) : Array.isArray(d) ? d : d ? [d] : [];
  return (
    <Svg width={s} height={s} viewBox="0 0 24 24" fill="none">
      {paths.map((p, i) => (
        <Path key={i} d={p} stroke={c} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" />
      ))}
    </Svg>
  );
}

export function Flame({ s = 14, c = "#fff" }: { s?: number; c?: string }) {
  return (
    <Svg width={s} height={s * 1.15} viewBox="0 0 24 28">
      <Path d="M12 2c4.4 5 6.6 8 6.6 12.2A6.6 6.6 0 0 1 5.4 14.2C5.4 11.4 7 9.6 9 8.2 10 9.6 10.8 10 12 8.6c.6-1.6.4-3.8 0-6.6Z" fill={c} />
    </Svg>
  );
}
