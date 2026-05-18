"""Throwaway smoke test for math_engine/kundli/ — delete after verification.

Lives in kundli/ (repo subfolder) — needs sys.path tweak so it can import
math_engine from the AIS root.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Repo root is one level up from this file (kundli/ → AIS root)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from datetime import date, time
from math_engine.kundli import BirthData, compute_chart

bd = BirthData(
    name='Sachin Tendulkar', date=date(1973, 4, 24), time=time(16, 50),
    place='Mumbai', lat=19.0760, lon=72.8777, tz='Asia/Kolkata',
    gender='M', exact_time=True,
)
c = compute_chart(bd)

SIGNS = ['Ari','Tau','Gem','Can','Leo','Vir','Lib','Sco','Sag','Cap','Aqu','Pis']

print('=== FOUNDATION SMOKE TEST — Sachin Tendulkar (24-Apr-1973 16:50 Mumbai) ===')
print(f'Ayanamsha:  {c.ayanamsha_used} = {c.ayanamsha_value:.4f}°')
print(f'Local:      {c.datetime_local.isoformat()}')
print(f'Lagna:      {c.lagna.sign} {c.lagna.degree_in_sign_dms} (lord {c.lagna.lord}; {c.lagna.nakshatra} pada {c.lagna.pada})')
print(f'D9 Lagna:   {SIGNS[c.divisional_charts[9].lagna_sign_index]}  (public records: Aries)')
print()

print('PLANETS:')
for n, p in c.planets.items():
    tags = []
    if p.is_retrograde: tags.append('R')
    if p.is_combust:    tags.append('C')
    if p.dignity:       tags.append(p.dignity[:3])
    tag = ('  [' + ' '.join(tags) + ']') if tags else ''
    print(f'  {n:8} {p.sign:12} {p.longitude_dms}  H{p.house:2d}  {p.nakshatra} pada {p.pada}{tag}')
print()

print('PANCHANGA:')
print(f'  Tithi={c.panchanga.tithi}  Paksha={c.panchanga.paksha}')
print(f'  Yoga={c.panchanga.yoga}  Karana={c.panchanga.karana}  Weekday={c.panchanga.weekday}')
print()

print('JAIMINI CHARA KARAKAS:')
print(f'  AK  Atmakaraka:   {c.chara_karakas.atmakaraka} ({c.chara_karakas.atmakaraka_degree:.4f}°)')
print(f'  AmK Amatyakaraka: {c.chara_karakas.amatyakaraka} ({c.chara_karakas.amatyakaraka_degree:.4f}°)')
for p, name, deg in c.chara_karakas.chain:
    print(f'    {name:25} → {p} ({deg:.2f}°)')
print()

print('CONJUNCTIONS:')
for cj in c.conjunctions: print(f'  {cj}')
print()
print('MUTUAL ASPECTS:')
for ma in c.mutual_aspects: print(f'  {ma}')
print()

print('FUNCTIONAL PLANETS for Virgo Lagna:')
print(f'  Yogakarakas:  {c.functional.yogakarakas}')
print(f'  Ben (Func):   {c.functional.benefics}')
print(f'  Mal (Func):   {c.functional.malefics}')
print()

print('ALL 16 DIVISIONAL CHARTS:')
for n in [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]:
    d = c.divisional_charts[n]
    sun = SIGNS[d.planet_signs['Sun']]
    moo = SIGNS[d.planet_signs['Moon']]
    jup = SIGNS[d.planet_signs['Jupiter']]
    sat = SIGNS[d.planet_signs['Saturn']]
    print(f'  D{n:2d} {d.name:25} Lg={SIGNS[d.lagna_sign_index]}  Su={sun}  Mo={moo}  Ju={jup}  Sa={sat}')
print()

print('NAKSHATRA PROFILE:')
np = c.nakshatra_profile
print(f'  Janma Nak: {np["birth_nakshatra"]} pada {np["pada"]}  (Naam-akshar: {np["naam_akshar"]})')
print(f'  Devta: {np["deity"]}')
print(f'  Symbol: {np["symbol"]}')
print(f'  Gana={np["gana"]}  Yoni={np["yoni"][0]}/{np["yoni"][1]}  Nadi={np["nadi"]}')
print(f'  Varna={np["varna"]}  Vashya={np["vashya"]}  Tatva={np["tatva"]}')
print(f'  Guna={np["guna"]}  Psych-Gender={np["gender"]}')
print()

print('AVAKAHADA CHAKRA:')
for k, v in np['avakahada_chakra']:
    print(f'  {k:30}: {v}')
print()
print('LAGNA RELATIONSHIPS:')
print(f'  Lord chain: {c.lagna.lord_chain}')
print(f'  Arudha Lagna: H{c.lagna.arudha_house} ({c.lagna.arudha_sign})')
print(f'  Indu Lagna:   {c.lagna.indu_sign}')
