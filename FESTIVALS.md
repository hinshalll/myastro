# Festival calendar — where it lives + how to update it (once a year)

The Today screen shows a warm **"Happy <festival>"** line in the greeting header on a
festival day, and the **My Panchang** month grid marks festival days. Both read from a
single **data file** so the dates can be refreshed without touching any code.

## The one file you edit
`shared/data/festivals_india.json`

That's it. It's plain data — a list of festivals per year. Never edit the Python.

```json
{
  "_last_updated": "2026-07-02",
  "2026": [
    { "date": "2026-11-08", "name": "Diwali" },
    { "date": "2026-03-04", "name": "Holi" }
  ],
  "2027": []
}
```

- **`date`** — `YYYY-MM-DD` (the day people celebrate / you'd greet them).
- **`name`** — shown as **"Happy <name>"**. (Optional `"greeting"` field overrides that,
  e.g. for a festival where "Happy" doesn't fit.)
- Keep only **widely-celebrated, joyful** festivals (ones you'd actually wish someone).
  Astronomical days (full/new moon, Ekadashi, eclipses) are already marked automatically
  by the engine — don't duplicate them here.

## How to update (about once a year, ~December)
1. Go to **drikpanchang.com** (the reference almanac) → the next year's festival calendar.
2. In `festivals_india.json`, add a new year block, e.g. `"2027": [ … ]`, with that year's
   major festivals as `{ "date": "…", "name": "…" }`, sorted by date.
3. Update `_last_updated` and the `_status` note for that year.
4. Done. No deploy logic changes; the loader picks it up.

**Prompt you can paste to an AI to do it for you:**
> "Here is my festivals_india.json. Add a `\"2027\"` block with the major all-India Hindu
> festival dates for 2027 from Drik Panchang (Makar Sankranti, Vasant Panchami, Maha
> Shivratri, Holi, Gudi Padwa, Ram Navami, Hanuman Jayanti, Baisakhi, Akshaya Tritiya,
> Raksha Bandhan, Janmashtami, Ganesh Chaturthi, Navratri, Dussehra, Karva Chauth,
> Dhanteras, Diwali, Govardhan Puja, Bhai Dooj, Chhath Puja, Guru Nanak Jayanti), each as
> {date:'YYYY-MM-DD', name:'…'}, sorted by date. Keep the same JSON shape."

## Good to know
- **Accuracy:** festival dates shift each year (lunar calendar) and can vary **±1 day** by
  region/tradition. Use the common all-India date; verify against Drik Panchang. A wrong
  greeting is low-stakes but we still care — that's why this is human/AI-verified data, not
  a computed guess.
- **Safe by default:** if a year isn't in the file (e.g. 2027 before you add it), the app
  simply shows **no** festival greeting for those dates — nothing breaks.
- **Other traditions:** you can add Eid, Christmas, regional festivals (Onam, Pongal, Durga
  Puja, Lohri…) the same way — same shape, same file.

## Code that reads it (for reference, don't edit to update dates)
- `shared/astro/festivals.py` — `festival_for(date)` and `festivals_in_range(start, end)`.
- Used by `POST /dashboard/hora` (the header greeting) and `POST /dashboard/panchang`
  (month-grid festival markers).
