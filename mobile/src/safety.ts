// safety.ts — the crisis-language guard. Used by Chat AND Journal. Non-cosmetic: crisis
// language must always route to a gentle, non-clinical pointer to KIRAN. In production this
// must be server-authoritative; keep this client check as a floor, never remove it.
export const KIRAN = "1800-599-0019";

export const DISTRESS = [
  "kill myself", "end it", "suicide", "don't want to be here", "dont want to be here",
  "hurt myself", "no reason to live", "can't go on", "cant go on", "want to die", "worthless",
];

export function isDistress(text: string): boolean {
  const t = (text || "").toLowerCase();
  return DISTRESS.some((w) => t.includes(w));
}
