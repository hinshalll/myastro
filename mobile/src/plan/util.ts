// util.ts — shared Plan-tab helpers (time + quality colours).
export function nowH() { const d = new Date(); return d.getHours() + d.getMinutes() / 60; }
export function fmtH(h: number) { const x = ((h % 24) + 24) % 24; let hr = Math.floor(x); const m = Math.round((x - hr) * 60); const ap = hr < 12 ? "am" : "pm"; let h12 = hr % 12; if (h12 === 0) h12 = 12; return `${h12}:${String(m).padStart(2, "0")}${ap}`; }
// quality -> solid fill for dots (matches the ribbon's semantic colours)
export function qFill(q: string) { return q === "best" ? "#3E9C7A" : q === "good" ? "#8FCFB0" : q === "hold" ? "#E7B24E" : q === "rest" ? "#9BA0BC" : "#E3E1DC"; }
export function qColor(q: string) { return q === "good" ? "#3E9C7A" : q === "mixed" ? "#E0A23C" : "#8E93B0"; }
export function qWord(q: string) { return q === "good" ? "good day" : q === "mixed" ? "mixed day" : "low-key day"; }
