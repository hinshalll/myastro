// steps.tsx — Steps 1-3: Name+gender, Birth date+place, Birth time.
// Ported from screens/onboarding/onboarding-flow.tsx. The birth-place field is WIRED LIVE
// to the backend geocoder (/geo/search via api/geo.ts) so we capture real lat/lon/tz for
// the chart. Everything else is faithful to the prototype. Voice: warm, plain, human.
import React, { useEffect, useMemo, useRef, useState } from "react";
import { View, Text } from "react-native";
import Svg, { Path, Circle } from "react-native-svg";
import { serif, sans, mono, aA } from "../ui/palette";
import { Press } from "../ui/atoms";
import { searchPlaces, Place } from "../api/geo";
import {
  P, OScreen, StepChrome, PrimaryButton, SoftChip, Field, Dropdown, Rise, CheckMark, Chevron, useTopPad, androidLift,
} from "./kit";
import { shortLabel } from "./data";

// shared serif kicker + title block
function Head({ kicker, title, sub }: { kicker?: string; title: string; sub?: string }) {
  return (
    <View>
      {kicker ? (
        <Rise delay={120} dist={12}>
          <Text style={{ fontFamily: mono(500), fontSize: 10.5, letterSpacing: 2.4, textTransform: "uppercase", color: P.violet, marginBottom: 12 }}>{kicker}</Text>
        </Rise>
      ) : null}
      <Rise delay={200} dist={14}>
        <Text style={{ fontFamily: serif(500), fontSize: 32, lineHeight: 36, color: P.ink, letterSpacing: -0.5 }}>{title}</Text>
      </Rise>
      {sub ? (
        <Rise delay={280} dist={12}>
          <Text style={{ fontFamily: sans(400), fontSize: 15, lineHeight: 23, color: P.inkMid, marginTop: 10 }}>{sub}</Text>
        </Rise>
      ) : null}
    </View>
  );
}

// ============================ STEP 1 — NAME + GENDER ================================
export function NameGender({ data, patch, step, onBack, onNext }: any) {
  const top = useTopPad(20);
  const genders = ["Female", "Male", "Other"];
  const canNext = (data.name || "").trim().length > 0;
  return (
    <OScreen crown={0.16} keyboard stars>
      <View style={{ flex: 1, paddingTop: top, paddingBottom: 34, paddingHorizontal: 26 }}>
        <StepChrome step={step} onBack={onBack} />
        <View style={{ height: 34 }} />
        <Head kicker="About you" title="Tell us about you." />

        <Rise delay={420} dist={14} style={{ marginTop: 34 }}>
          <Field label="What should we call you?" value={data.name} onChange={(v: string) => patch({ name: v })} placeholder="Your first name" autoCapitalize="words" />
        </Rise>

        <Rise delay={520} dist={14} style={{ marginTop: 26 }}>
          <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 10, gap: 6 }}>
            <Text style={{ fontFamily: mono(500), fontSize: 10, letterSpacing: 1.6, textTransform: "uppercase", color: P.inkFaint }}>Gender</Text>
            <Text style={{ fontFamily: sans(400), fontSize: 11, color: aA(P.inkFaint, 0.85) }}>· optional</Text>
          </View>
          <View style={{ flexDirection: "row", gap: 10 }}>
            {genders.map((g) => (
              <SoftChip key={g} label={g} grow active={data.gender === g} onPress={() => patch({ gender: data.gender === g ? null : g })} />
            ))}
          </View>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginTop: 10 }}>
            <Svg width={13} height={13} viewBox="0 0 24 24" fill="none">
              <Circle cx="12" cy="12" r="9" stroke={aA(P.inkFaint, 0.7)} strokeWidth={1.7} />
              <Path d="M12 11v5M12 8h.01" stroke={aA(P.inkFaint, 0.9)} strokeWidth={1.7} strokeLinecap="round" />
            </Svg>
            <Text style={{ fontFamily: sans(400), fontSize: 12.5, color: P.inkFaint }}>used for certain Vedic readings.</Text>
          </View>
        </Rise>

        <View style={{ flex: 1, minHeight: 24 }} />
        <Rise delay={640} dist={14}>
          <PrimaryButton label="Continue" disabled={!canNext} onPress={() => canNext && onNext()} />
        </Rise>
      </View>
    </OScreen>
  );
}

// ============================ STEP 2 — BIRTH DATE + PLACE ===========================
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

export function BirthPlace({ data, patch, step, onBack, onNext }: any) {
  const top = useTopPad(20);
  const [q, setQ] = useState(data.birthPlace ? shortLabel(data.birthPlace.label) : "");
  const [results, setResults] = useState<Place[]>([]);
  const [loading, setLoading] = useState(false);
  const seq = useRef(0);

  const days = useMemo(() => Array.from({ length: 31 }, (_, i) => ({ value: i + 1, label: String(i + 1) })), []);
  const months = useMemo(() => MONTHS.map((m, i) => ({ value: i + 1, label: m })), []);
  const nowY = new Date().getFullYear();
  const years = useMemo(() => Array.from({ length: nowY - 1900 + 1 }, (_, i) => ({ value: nowY - i, label: String(nowY - i) })), [nowY]);

  // WIRE: live geocoder. Debounced /geo/search -> {label,lat,lon,tz}. Real lat/lon/tz feed
  // the chart. (Replaces the prototype's in-file mock CITY_DB.)
  useEffect(() => {
    const s = q.trim();
    if (s.length < 2 || (data.birthPlace && shortLabel(data.birthPlace.label) === s)) { setResults([]); setLoading(false); return; }
    setLoading(true);
    const id = ++seq.current;
    const t = setTimeout(async () => {
      try { const r = await searchPlaces(s); if (id === seq.current) { setResults(r.slice(0, 5)); setLoading(false); } }
      catch { if (id === seq.current) { setResults([]); setLoading(false); } }
    }, 280);
    return () => clearTimeout(t);
  }, [q, data.birthPlace]);

  const dateSet = data.dobD && data.dobM && data.dobY;
  const canNext = dateSet && data.birthPlace;

  const pickCity = (c: Place) => { patch({ birthPlace: c }); setQ(shortLabel(c.label)); setResults([]); };

  return (
    <OScreen crown={0.16} scroll keyboard stars>
      <View style={{ flexGrow: 1, paddingTop: top, paddingBottom: 34, paddingHorizontal: 26 }}>
        <StepChrome step={step} onBack={onBack} />
        <View style={{ height: 34 }} />
        <Head kicker="Your beginning" title={"When and where\nwere you born?"} />

        {/* date of birth */}
        <Rise delay={400} dist={14} style={{ marginTop: 32 }}>
          <Text style={{ fontFamily: mono(500), fontSize: 10, letterSpacing: 1.6, textTransform: "uppercase", color: P.inkFaint, marginBottom: 10 }}>Date of birth</Text>
          <View style={{ flexDirection: "row", gap: 9 }}>
            <Dropdown flex={1} value={data.dobD} options={days} onChange={(v: number) => patch({ dobD: v })} placeholder="Day" />
            <Dropdown flex={1.5} value={data.dobM} options={months} onChange={(v: number) => patch({ dobM: v })} placeholder="Month" />
            <Dropdown flex={1.2} value={data.dobY} options={years} onChange={(v: number) => patch({ dobY: v })} placeholder="Year" />
          </View>
        </Rise>

        {/* place of birth */}
        <Rise delay={500} dist={14} style={{ marginTop: 24 }}>
          <Text style={{ fontFamily: mono(500), fontSize: 10, letterSpacing: 1.6, textTransform: "uppercase", color: P.inkFaint, marginBottom: 10 }}>Place of birth</Text>
          <Field value={q} placeholder="Search your birth place" autoCapitalize="words"
            onChange={(v: string) => { setQ(v); if (data.birthPlace) patch({ birthPlace: null }); }} />

          {/* live results (inline; pushes content down, no clipping). androidLift: this panel
              mounts right beside the FOCUSED place input, so an elevation here would knock the
              keyboard back down mid-search. */}
          {results.length > 0 && !data.birthPlace ? (
            <View style={{ marginTop: 8, backgroundColor: P.paper, borderRadius: 14, borderWidth: 1, borderColor: P.line, padding: 6, ...androidLift({ y: 14, blur: 40, opacity: 0.16, elevation: 4 }) } as any}>
              {results.map((c) => (
                <Press key={c.label} onPress={() => pickCity(c)} scale={0.99}
                  style={{ paddingVertical: 12, paddingHorizontal: 10, borderRadius: 10, flexDirection: "row", alignItems: "center", gap: 10 }}>
                  <Svg width={16} height={16} viewBox="0 0 24 24" fill="none">
                    <Path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11Z" stroke={P.violet} strokeWidth={1.7} />
                    <Circle cx="12" cy="10" r="2.4" stroke={P.violet} strokeWidth={1.7} />
                  </Svg>
                  <Text numberOfLines={1} style={{ flex: 1, fontFamily: sans(500), fontSize: 15, color: P.inkSoft }}>{c.label}</Text>
                </Press>
              ))}
            </View>
          ) : null}

          {/* REQUIRED LocationIQ attribution (must stay visible) */}
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "flex-end", marginTop: 10 }}>
            <Text style={{ fontFamily: sans(500), fontSize: 11.5, color: aA(P.inkFaint, 0.9) }}>
              Search by <Text style={{ fontFamily: sans(600), color: P.violet }}>LocationIQ</Text>
            </Text>
          </View>
        </Rise>

        {data.birthPlace ? (
          <View style={{ marginTop: 6, paddingVertical: 12, paddingHorizontal: 14, borderRadius: 12, backgroundColor: aA(P.violet, 0.06), borderWidth: 1, borderColor: aA(P.violet, 0.18), flexDirection: "row", alignItems: "center", gap: 10 }}>
            <CheckMark size={16} color={P.violet} />
            <Text numberOfLines={1} style={{ flex: 1, fontFamily: sans(500), fontSize: 13.5, color: P.violetDeep }}>{shortLabel(data.birthPlace.label)}</Text>
          </View>
        ) : null}

        <View style={{ flex: 1, minHeight: 24 }} />
        <Rise delay={720} dist={14} style={{ marginTop: 20 }}>
          <PrimaryButton label="Continue" disabled={!canNext} onPress={() => canNext && onNext()} />
        </Rise>
      </View>
    </OScreen>
  );
}

// ============================ STEP 3 — BIRTH TIME ==================================
const PART_OF_DAY = [
  { key: "early morning", label: "Early morning", time: "06:00" },
  { key: "morning", label: "Morning", time: "09:00" },
  { key: "afternoon", label: "Afternoon", time: "14:00" },
  { key: "evening", label: "Evening", time: "18:00" },
  { key: "night", label: "Night", time: "22:00" },
];
const HOURS = Array.from({ length: 12 }, (_, i) => ({ value: i === 0 ? 12 : i, label: String(i === 0 ? 12 : i) }));
const MINS = Array.from({ length: 60 }, (_, i) => ({ value: i, label: String(i).padStart(2, "0") }));

function TimeOption({ o, active, onPress }: any) {
  return (
    <Press onPress={onPress} scale={0.985}
      style={{ paddingVertical: 16, paddingHorizontal: 16, borderRadius: 16, flexDirection: "row", gap: 13, alignItems: "flex-start",
        backgroundColor: active ? P.violetTintSoft : P.paper, borderWidth: 1.5, borderColor: active ? P.violet : P.line,
        ...androidLift(active ? { y: 10, blur: 26, opacity: 0.28, color: P.violet, elevation: 3 } : { y: 4, blur: 14, opacity: 0.12, elevation: 1 }) } as any}>
      <View style={{ width: 22, height: 22, borderRadius: 999, marginTop: 1, borderWidth: 2, borderColor: active ? P.violet : aA(P.inkFaint, 0.5), alignItems: "center", justifyContent: "center", backgroundColor: active ? P.violet : "transparent" }}>
        {active ? (
          <Svg width={12} height={12} viewBox="0 0 24 24" fill="none"><Path d="M5 12.5 9.5 17 19 7" stroke="#fff" strokeWidth={2.6} strokeLinecap="round" strokeLinejoin="round" /></Svg>
        ) : null}
      </View>
      <View style={{ flex: 1 }}>
        <Text style={{ fontFamily: sans(700), fontSize: 15.5, color: active ? P.violetDeep : P.ink }}>{o.title}</Text>
        <Text style={{ fontFamily: sans(400), fontSize: 13, lineHeight: 19.5, color: active ? aA(P.violetDeep, 0.8) : P.inkMid, marginTop: 3 }}>{o.note}</Text>
      </View>
    </Press>
  );
}

export function BirthTime({ data, patch, step, onBack, onNext }: any) {
  const top = useTopPad(20);
  const [why, setWhy] = useState(false);
  const [hh, setHH] = useState(9); const [mm, setMM] = useState(0); const [ap, setAP] = useState("AM");
  const prec = data.birthTimePrecision;

  // These notes state EXACTLY what each choice opens, because each one really does change the
  // app (verified against the backend: exact -> houses + divisionals; roughly -> houses only;
  // don't know -> Moon-led, no rising). The old "approximate" note said "only the finest timing
  // details may shift", which was an over-promise: a rough time costs you every divisional
  // chart, and D9 Navamsa is the whole basis of the marriage and partnership readings. That is
  // a feature area, not a detail, and quietly losing it would read as the app being wrong.
  const opts = [
    { key: "exact", title: "I know my exact time", note: "Everything opens up: your rising sign, your houses, and the marriage and career readings." },
    { key: "approximate", title: "I know it roughly", note: "Enough for your rising sign and your houses. The marriage and career readings need the exact minute." },
    { key: "unknown", title: "I don't know it", note: "No problem, and very common. We read from your Moon, which already says a great deal. Add your time whenever you find it and the rest opens up." },
  ];

  const choose = (k: string) => {
    if (k === "exact") { const h24 = ap === "PM" ? (hh % 12) + 12 : hh % 12; patch({ birthTimePrecision: "exact", birthTime: `${String(h24).padStart(2, "0")}:${String(mm).padStart(2, "0")}`, partOfDay: null }); }
    else if (k === "approximate") { patch({ birthTimePrecision: "approximate", birthTime: null, partOfDay: null }); }
    else { patch({ birthTimePrecision: "unknown", birthTime: null, partOfDay: null }); }
  };
  // keep the captured exact time in sync while the picker changes
  useEffect(() => {
    if (prec === "exact") { const h24 = ap === "PM" ? (hh % 12) + 12 : hh % 12; patch({ birthTime: `${String(h24).padStart(2, "0")}:${String(mm).padStart(2, "0")}` }); }
  }, [hh, mm, ap]);
  const pickPart = (p: any) => patch({ birthTimePrecision: "approximate", partOfDay: p.key, birthTime: p.time });

  // "exact" always holds a time (the picker seeds 9:00 AM); "approximate" only holds one once a
  // part of day is picked; "unknown" is a complete answer in itself.
  const canNext = prec === "exact" || prec === "unknown" || (prec === "approximate" && !!data.partOfDay);

  return (
    <OScreen crown={0.16} scroll stars>
      <View style={{ flexGrow: 1, paddingTop: top, paddingBottom: 34, paddingHorizontal: 26 }}>
        <StepChrome step={step} onBack={onBack} />
        <View style={{ height: 34 }} />
        <Head kicker="The finer tuning" title="Do you know your birth time?" />

        <View style={{ marginTop: 28, gap: 12 }}>
          {opts.map((o, i) => {
            const active = prec === o.key;
            return (
              <Rise key={o.key} delay={400 + i * 60} dist={14}>
                <TimeOption o={o} active={active} onPress={() => choose(o.key)} />
                {active && o.key === "exact" ? (
                  <View style={{ marginTop: 10, padding: 14, borderRadius: 14, backgroundColor: aA(P.violet, 0.05), borderWidth: 1, borderColor: aA(P.violet, 0.16), flexDirection: "row", alignItems: "center", gap: 8 }}>
                    <Dropdown flex={1} value={hh} options={HOURS} onChange={setHH} placeholder="Hr" />
                    <Text style={{ fontFamily: serif(500), fontSize: 22, color: P.inkFaint }}>:</Text>
                    <Dropdown flex={1} value={mm} options={MINS} onChange={setMM} placeholder="Min" />
                    <Dropdown flex={1} value={ap} options={["AM", "PM"]} onChange={setAP} placeholder="AM" />
                  </View>
                ) : null}
                {active && o.key === "approximate" ? (
                  <View style={{ marginTop: 10, flexDirection: "row", flexWrap: "wrap", gap: 8 }}>
                    {PART_OF_DAY.map((p) => <SoftChip key={p.key} label={p.label} active={data.partOfDay === p.key} onPress={() => pickPart(p)} />)}
                  </View>
                ) : null}
              </Rise>
            );
          })}
        </View>

        {/* why does this matter */}
        <Rise delay={620} dist={12} style={{ marginTop: 18 }}>
          <Press onPress={() => setWhy((v) => !v)} scale={0.98} style={{ flexDirection: "row", alignItems: "center", gap: 6, paddingVertical: 6, paddingHorizontal: 2, alignSelf: "flex-start" }}>
            <Text style={{ fontFamily: sans(600), fontSize: 13.5, color: P.violet }}>Why does this matter?</Text>
            <Chevron dir={why ? "up" : "down"} size={15} color={P.violet} />
          </Press>
          {why ? (
            <View style={{ marginTop: 4, paddingVertical: 12, paddingHorizontal: 14, borderRadius: 12, backgroundColor: P.field, borderWidth: 1, borderColor: P.line }}>
              <Text style={{ fontFamily: sans(400), fontSize: 13.5, lineHeight: 21.5, color: P.inkMid }}>Your birth time sets the angle of the whole sky at your first breath. With the exact minute we can place your rising sign and the twelve houses, which sharpen the timing of things. Without it, we lean on the Moon, which already says a great deal about who you are.</Text>
            </View>
          ) : null}
        </Rise>

        <View style={{ flex: 1, minHeight: 28 }} />
        {/* Must actually answer. "I know it roughly" also needs a part of day, otherwise we hold
            no clock time at all and timeTier() would honestly demote them to a Moon-led chart
            without them ever understanding why the rising sign vanished. */}
        <Rise delay={520} dist={14} style={{ marginTop: 20 }}>
          <PrimaryButton label="Continue" disabled={!canNext} onPress={() => canNext && onNext()} />
        </Rise>
      </View>
    </OScreen>
  );
}
