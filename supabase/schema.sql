-- ============================================================================
-- Myastro — Supabase schema (v1)
-- ============================================================================
-- Paste this whole file into Supabase → SQL Editor → New query → Run.
-- It is idempotent-ish (safe to re-run; uses IF NOT EXISTS where possible).
--
-- Design ref: MOBILE_APP_BLUEPRINT.md §8.4. Auth is handled by Supabase Auth
-- (the built-in `auth.users` table). Every app table keys off `auth.uid()`.
--
-- Row-Level Security (RLS) is ON for every user-data table: a logged-in user
-- can only read/write their OWN rows. Mood logs & journals are private to the
-- owner and never shared (blueprint rule). `cached_daily` is the only shared,
-- read-by-everyone table.
-- ============================================================================

-- ── App-level user record (extends auth.users) ─────────────────────────────
create table if not exists public.app_users (
  id          uuid primary key references auth.users(id) on delete cascade,
  email       text,
  language    text default 'en',
  push_token  text,                       -- Expo push token
  settings    jsonb default '{}'::jsonb,
  created_at  timestamptz default now()
);

-- ── Profiles: the user themselves + people they save (People tab) ───────────
-- source: 'self' (the account owner) | 'friend' (a live app user) | 'manual' (static chart)
create table if not exists public.profiles (
  id               uuid primary key default gen_random_uuid(),
  owner            uuid not null references auth.users(id) on delete cascade,
  name             text not null,
  birth_date       date not null,
  birth_time       time,                  -- nullable: unknown birth time → Moon-chart mode
  birth_time_known boolean default false,
  exact_time       boolean default false,
  birth_place      text,
  lat              double precision,
  lon              double precision,
  tz               text,                  -- e.g. 'Asia/Kolkata'
  gender           text,
  relation_tag     text,                  -- 'self' | 'partner' | 'mother' | 'friend' ...
  source           text not null default 'self',
  created_at       timestamptz default now()
);
create index if not exists profiles_owner_idx on public.profiles(owner);

-- ── Connections: friend requests + privacy tier (People tab growth loop) ────
create table if not exists public.connections (
  id             uuid primary key default gen_random_uuid(),
  owner_user_id  uuid not null references auth.users(id) on delete cascade,
  target_user_id uuid references auth.users(id) on delete cascade,
  status         text not null default 'pending',     -- 'pending' | 'accepted'
  share_tier     text not null default 'acquaintance',-- 'acquaintance' | 'close'
  created_at     timestamptz default now()
);
create index if not exists connections_owner_idx on public.connections(owner_user_id);
create index if not exists connections_target_idx on public.connections(target_user_id);

-- ── Check-ins: the core wedge (3-tap mood log + the day's astro state) ──────
create table if not exists public.checkins (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  date         date not null,
  mood         text,
  energy       text,
  clarity      text,
  astro_state  jsonb,                     -- the computed transit/moon state for that day
  created_at   timestamptz default now(),
  unique (user_id, date)                  -- one check-in per day
);
create index if not exists checkins_user_idx on public.checkins(user_id, date);

-- ── Patterns: the Pattern Engine payoff (personal correlations) ─────────────
create table if not exists public.patterns (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  pattern_text text not null,
  evidence     jsonb,
  unlocked_at  timestamptz default now()
);
create index if not exists patterns_user_idx on public.patterns(user_id);

-- ── Journal entries (optional free-text; strictly private) ──────────────────
create table if not exists public.journal_entries (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  date         date not null,
  text         text,
  astro_state  jsonb,
  created_at   timestamptz default now()
);
create index if not exists journal_user_idx on public.journal_entries(user_id, date);

-- ── Streaks ─────────────────────────────────────────────────────────────────
create table if not exists public.streaks (
  user_id    uuid not null references auth.users(id) on delete cascade,
  kind       text not null default 'checkin',   -- 'checkin' | 'ritual' | ...
  count      integer not null default 0,
  last_date  date,
  primary key (user_id, kind)
);

-- ── Monetization ─────────────────────────────────────────────────────────────
create table if not exists public.subscriptions (
  user_id    uuid primary key references auth.users(id) on delete cascade,
  plan       text,                         -- 'weekly' | 'monthly' | 'annual'
  status     text default 'inactive',
  renews_at  timestamptz
);
create table if not exists public.purchases (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  item        text not null,               -- 'full_life_reading' | 'marriage_report' | ...
  created_at  timestamptz default now()
);
create index if not exists purchases_user_idx on public.purchases(user_id);

-- ── Caches (cost discipline) ─────────────────────────────────────────────────
-- Shared daily content: generated once/day, read by everyone in the same state.
create table if not exists public.cached_daily (
  date            date not null,
  astro_state_key text not null,
  content         jsonb not null,
  created_at      timestamptz default now(),
  primary key (date, astro_state_key)
);
-- Per-chart computed-once results. The cache key includes `precision` so that
-- adding/confirming a birth time later (unknown→approximate→exact) recomputes
-- once instead of serving a stale lower-precision result (blueprint §8.3 rule 4).
create table if not exists public.cached_chart (
  id          uuid primary key default gen_random_uuid(),
  profile_id  uuid not null references public.profiles(id) on delete cascade,
  kind        text not null,               -- 'kundli' | 'dharma' | 'dasha' | 'full_reading' ...
  precision   text not null default 'unknown',  -- 'exact' | 'approximate' | 'unknown'
  content     jsonb not null,
  created_at  timestamptz default now(),
  unique (profile_id, kind, precision)
);

-- ── Usage counters: enforce freemium soft caps (blueprint §7) ───────────────
-- One row per user/day/kind. kind: 'ask' | 'reading' | 'palm' | 'face' | 'tarot'.
create table if not exists public.usage_counters (
  user_id  uuid not null references auth.users(id) on delete cascade,
  date     date not null,
  kind     text not null,
  count    integer not null default 0,
  primary key (user_id, date, kind)
);

-- ── Groups: Family grid (household) + Couple space (blueprint Tab 2) ────────
-- A group bundles several profiles the user already saved/connected.
create table if not exists public.groups (
  id          uuid primary key default gen_random_uuid(),
  owner       uuid not null references auth.users(id) on delete cascade,
  kind        text not null,               -- 'household' | 'couple'
  name        text,
  created_at  timestamptz default now()
);
create table if not exists public.group_members (
  group_id    uuid not null references public.groups(id) on delete cascade,
  profile_id  uuid not null references public.profiles(id) on delete cascade,
  role        text,                        -- 'me' | 'partner' | 'parent' | 'child' ...
  primary key (group_id, profile_id)
);

-- ── Ritual journeys: 21/40-day gamified remedy journeys + mala (blueprint §6.3) ──
create table if not exists public.ritual_journeys (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  journey_key  text not null,              -- 'settle_mind' | 'open_heart' | 'money_flow' ...
  total_days   integer not null,
  current_day  integer not null default 0,
  status       text not null default 'active',  -- 'active' | 'completed' | 'abandoned'
  progress     jsonb default '{}'::jsonb,  -- per-day task completion
  started_at   timestamptz default now(),
  updated_at   timestamptz default now()
);
create index if not exists ritual_journeys_user_idx on public.ritual_journeys(user_id);

-- ── Rewards / badges: streak milestones, unlocked perks (blueprint §6.4) ────
create table if not exists public.rewards (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  kind       text not null,                -- 'badge' | 'streak_milestone' | 'free_unlock'
  ref        text,                         -- e.g. '7_day_streak'
  meta       jsonb,
  earned_at  timestamptz default now()
);
create index if not exists rewards_user_idx on public.rewards(user_id);

-- ── Ask / Prashna conversation history (always-on Ask button) ───────────────
create table if not exists public.ai_conversations (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  kind        text not null default 'ask', -- 'ask' | 'prashna' | 'decision'
  title       text,
  messages    jsonb not null default '[]'::jsonb,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);
create index if not exists ai_conversations_user_idx on public.ai_conversations(user_id);

-- NOTE: notification preferences (which alerts are on/off) and dismissed cards
-- (e.g. "Hide" on the eclipse card) live in app_users.settings (jsonb) — no
-- dedicated table needed.

-- ============================================================================
-- Row-Level Security
-- ============================================================================
alter table public.app_users      enable row level security;
alter table public.profiles       enable row level security;
alter table public.connections    enable row level security;
alter table public.checkins       enable row level security;
alter table public.patterns       enable row level security;
alter table public.journal_entries enable row level security;
alter table public.streaks        enable row level security;
alter table public.subscriptions  enable row level security;
alter table public.purchases      enable row level security;
alter table public.cached_chart   enable row level security;
alter table public.cached_daily   enable row level security;
alter table public.usage_counters enable row level security;
alter table public.groups         enable row level security;
alter table public.group_members  enable row level security;
alter table public.ritual_journeys enable row level security;
alter table public.rewards        enable row level security;
alter table public.ai_conversations enable row level security;

-- Helper: "the row belongs to the current user" policies.
-- app_users: row id == auth.uid()
drop policy if exists app_users_self on public.app_users;
create policy app_users_self on public.app_users
  for all using (id = auth.uid()) with check (id = auth.uid());

-- owner == auth.uid() tables
drop policy if exists profiles_owner on public.profiles;
create policy profiles_owner on public.profiles
  for all using (owner = auth.uid()) with check (owner = auth.uid());

drop policy if exists connections_owner on public.connections;
create policy connections_owner on public.connections
  for all using (owner_user_id = auth.uid() or target_user_id = auth.uid())
  with check (owner_user_id = auth.uid());

-- user_id == auth.uid() tables
drop policy if exists checkins_owner on public.checkins;
create policy checkins_owner on public.checkins
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists patterns_owner on public.patterns;
create policy patterns_owner on public.patterns
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists journal_owner on public.journal_entries;
create policy journal_owner on public.journal_entries
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists streaks_owner on public.streaks;
create policy streaks_owner on public.streaks
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists subs_owner on public.subscriptions;
create policy subs_owner on public.subscriptions
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists purchases_owner on public.purchases;
create policy purchases_owner on public.purchases
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

-- cached_chart: tied to a profile the user owns
drop policy if exists cached_chart_owner on public.cached_chart;
create policy cached_chart_owner on public.cached_chart
  for all using (
    exists (select 1 from public.profiles p where p.id = profile_id and p.owner = auth.uid())
  ) with check (
    exists (select 1 from public.profiles p where p.id = profile_id and p.owner = auth.uid())
  );

-- cached_daily: shared read for any logged-in user; writes done server-side
-- (service role bypasses RLS), so no insert policy for normal users.
drop policy if exists cached_daily_read on public.cached_daily;
create policy cached_daily_read on public.cached_daily
  for select using (auth.role() = 'authenticated');

-- new user-data tables: own rows only
drop policy if exists usage_owner on public.usage_counters;
create policy usage_owner on public.usage_counters
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists groups_owner on public.groups;
create policy groups_owner on public.groups
  for all using (owner = auth.uid()) with check (owner = auth.uid());

drop policy if exists group_members_owner on public.group_members;
create policy group_members_owner on public.group_members
  for all using (
    exists (select 1 from public.groups g where g.id = group_id and g.owner = auth.uid())
  ) with check (
    exists (select 1 from public.groups g where g.id = group_id and g.owner = auth.uid())
  );

drop policy if exists ritual_owner on public.ritual_journeys;
create policy ritual_owner on public.ritual_journeys
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists rewards_owner on public.rewards;
create policy rewards_owner on public.rewards
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists ai_conv_owner on public.ai_conversations;
create policy ai_conv_owner on public.ai_conversations
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

-- ── Auto-create an app_users row when a new auth user signs up ──────────────
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.app_users (id, email) values (new.id, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
