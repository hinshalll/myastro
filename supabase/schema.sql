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
  -- depth_mode: how much astrology to SHOW by default (blueprint §6.10). Maps to
  -- the 3 card layers: 'simple' = body only; 'balanced' = body + the plain "why";
  -- 'full' = body + why + Sanskrit/technical. A default, not a lock — the user can
  -- drill up/down anywhere. This column is the fast read/write path.
  depth_mode  text not null default 'simple' check (depth_mode in ('simple','balanced','full')),
  settings    jsonb default '{}'::jsonb,
  created_at  timestamptz default now()
);
-- Idempotency: `create table if not exists` will NOT add new columns to an
-- already-existing app_users (e.g. a DB created before depth_mode landed). This
-- guarantees the column exists on re-run.
alter table public.app_users
  add column if not exists depth_mode text not null default 'simple'
  check (depth_mode in ('simple','balanced','full'));
-- Widen the check on an existing column (DBs created with the old 2-value check).
alter table public.app_users drop constraint if exists app_users_depth_mode_check;
alter table public.app_users
  add constraint app_users_depth_mode_check check (depth_mode in ('simple','balanced','full'));

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

-- ── Memory facts: the auto-remembered, distilled "what the app knows about you"
-- (THE MEMORY). Durable facts the AI EXTRACTS from journal entries + chat
-- (people, events, goals, fears, preferences, dates), deduped/merged. This is the
-- compressed layer; raw signals live in `journal_entries` + `checkins`. Chat is
-- EPHEMERAL (not stored) — only these distilled facts persist (this replaces the
-- old "save chat answer"). NO vector DB: a single user's facts are few, so they
-- are loaded + ranked directly (salience + recency). Qdrant stays for the shared
-- book RAG only; if semantic journal-search is ever wanted, use Supabase pgvector,
-- not a second service. Strictly private; the user can view/edit/delete any fact.
create table if not exists public.memory_facts (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  fact        text not null,                  -- the distilled durable fact (1-2 lines)
  category    text,                           -- 'person'|'relationship'|'event'|'goal'|'fear'|'preference'|'health'|'work'|'money'|'other'
  source      text not null default 'chat',   -- 'chat'|'journal'|'manual'
  source_ref  uuid,                            -- optional link to journal_entries.id etc.
  salience    real not null default 0.5,       -- 0..1 importance, for recall ranking
  times_seen  integer not null default 1,      -- reinforcement count (fact mentioned again)
  status      text not null default 'active',  -- 'active'|'superseded' (merge/dedupe)
  first_seen  timestamptz default now(),
  last_seen   timestamptz default now(),       -- recency, for recall ranking
  updated_at  timestamptz default now()
);
create index if not exists memory_facts_user_idx on public.memory_facts(user_id, status, salience desc);

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

-- ── Ask / Prashna conversation context (always-on Ask button) ───────────────
-- NOTE (v4): chat is now EPHEMERAL — conversations are NOT persisted. The
-- companion "remembers" only via the distilled `memory_facts` it auto-extracts.
-- This table is kept for optional short-lived session context / backward-compat;
-- it is no longer the source of recall. Safe to leave unused (like ad_rewards).
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

-- ── Today → Plan tab + Sage companion, table 'moon_messages' is legacy (v4.1) ─
-- My Day: typed to-dos auto-placed into the day's best windows. The placed
-- window + notify_at are computed SERVER-SIDE from /dashboard/timing, so the
-- client only has to schedule one local notification ~15 min before.
create table if not exists public.day_tasks (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references auth.users(id) on delete cascade,
  date           date not null,
  title          text not null,
  importance     text not null default 'normal',   -- 'normal' | 'important'
  window_start   text,                              -- "HH:MM" local (placed window)
  window_end     text,                              -- "HH:MM" local
  window_quality text,                              -- 'good' | 'neutral' | 'avoid'
  notify_at      text,                              -- "HH:MM" local, ~15 min before window
  done           boolean not null default false,
  created_at     timestamptz default now(),
  updated_at     timestamptz default now()
);
create index if not exists day_tasks_user_idx on public.day_tasks(user_id, date);

-- Time Capsule: a note written now, delivered at a future moment — a custom date,
-- or a computed one (next birthday / next Dasha chapter / next Jupiter-favours).
-- 2-3 days before deliver_on the app shows a HINT (no content); on the day it
-- reveals and `delivered` flips.
create table if not exists public.time_capsules (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references auth.users(id) on delete cascade,
  note           text not null,
  deliver_on     date not null,
  occasion       text,                              -- 'custom'|'birthday'|'dasha'|'jupiter'
  occasion_label text,                              -- e.g. "your next birthday"
  sealed_on      date not null default current_date,
  delivered      boolean not null default false,
  created_at     timestamptz default now(),
  updated_at     timestamptz default now()
);
create index if not exists time_capsules_user_idx on public.time_capsules(user_id, deliver_on);

-- Moon messages: the PROACTIVE companion. The server writes an opener (a pattern
-- it noticed, a look-back, or one thoughtful nudge) when today's sky triggers one
-- of the user's unlocked patterns; the app shows the Moon glow + dot until read.
-- Server WRITES via the service client (like memory_facts); the user READS/marks-read
-- via RLS. `for_date` dedupes one opener of a kind per day.
create table if not exists public.moon_messages (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  kind         text not null default 'nudge',       -- 'welcome' | 'pattern' | 'lookback' | 'nudge'
  body         text not null,                        -- the warm opener line
  meta         jsonb,                                -- what triggered it (for tap-through)
  read         boolean not null default false,
  for_date     date,                                 -- the day it was generated for (dedupe)
  created_at   timestamptz default now()
);
create index if not exists moon_messages_user_idx on public.moon_messages(user_id, read, created_at desc);

-- ── Diyas: the in-app currency (blueprint §7) ──────────────────────────────
-- Display name in the app = "Diyas" (lamps; lit by practice/streaks, spent on
-- AI readings, gifted, or topped-up). Table names are kept NEUTRAL so the
-- display word can be renamed without a DB migration. Wallets/ledger are written
-- SERVER-SIDE ONLY (service role) so a client can never inflate its own balance.
create table if not exists public.coin_wallets (
  user_id         uuid primary key references auth.users(id) on delete cascade,
  balance         integer not null default 0 check (balance >= 0),
  lifetime_earned integer not null default 0,
  lifetime_spent  integer not null default 0,
  updated_at      timestamptz default now()
);

-- Append-only ledger: every wallet change is one signed row (audit trail).
-- delta > 0 = diyas in; delta < 0 = diyas out. balance_after snapshots the
-- resulting balance for cheap auditing/debugging.
create table if not exists public.coin_transactions (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  delta         integer not null,            -- signed: +earned/bought/ad, -spent/gifted-out
  source        text not null,               -- 'earned_daily'|'earned_streak'|'earned_practice'|'bought_iap'|'ad_reward'|'spent'|'referral_bonus'|'gift_received'|'gift_sent'|'admin_adjust'
  ref           text,                         -- e.g. 'full_life_reading' | IAP receipt id | mantra/journey key
  meta          jsonb,
  balance_after integer,                      -- wallet balance after this row applied
  created_at    timestamptz default now()
);
create index if not exists coin_tx_user_idx on public.coin_transactions(user_id, created_at);

-- Atomic wallet + ledger update. delta>0 credits, delta<0 debits.
-- Locks the wallet row, REJECTS (returns null) if a debit would overdraw, then
-- updates the balance + lifetime totals and appends one signed ledger row.
-- SECURITY DEFINER + server-only callers = clients can never mint Diyas.
create or replace function public.apply_coin_delta(
  p_user uuid, p_delta int, p_source text, p_ref text, p_meta jsonb
) returns int
language plpgsql
security definer
as $$
declare
  v_balance int;
  v_new int;
begin
  insert into public.coin_wallets(user_id, balance) values (p_user, 0)
    on conflict (user_id) do nothing;
  select balance into v_balance from public.coin_wallets where user_id = p_user for update;
  v_new := v_balance + p_delta;
  if v_new < 0 then
    return null;                              -- insufficient diyas
  end if;
  update public.coin_wallets
     set balance         = v_new,
         lifetime_earned = lifetime_earned + greatest(p_delta, 0),
         lifetime_spent  = lifetime_spent  + greatest(-p_delta, 0),
         updated_at      = now()
   where user_id = p_user;
  insert into public.coin_transactions(user_id, delta, source, ref, meta, balance_after)
    values (p_user, p_delta, p_source, p_ref, p_meta, v_new);
  return v_new;
end;
$$;
-- CRITICAL: lock this SECURITY DEFINER function to the server only. Without
-- this, Postgres grants EXECUTE to PUBLIC, so a client with the anon key could
-- call it via PostgREST RPC and mint Diyas. Only the service_role (the backend)
-- may call it.
revoke all on function public.apply_coin_delta(uuid, int, text, text, jsonb)
  from public, anon, authenticated;
grant execute on function public.apply_coin_delta(uuid, int, text, text, jsonb)
  to service_role;

-- ── Referrals: invite → both earn diyas (blueprint §7 growth loop) ──────────
create table if not exists public.referrals (
  id               uuid primary key default gen_random_uuid(),
  referrer_user_id uuid not null references auth.users(id) on delete cascade,
  referee_user_id  uuid references auth.users(id) on delete set null,  -- filled when invitee signs up
  code             text not null unique,      -- short shareable code
  status           text not null default 'pending',  -- 'pending'|'redeemed'|'rewarded'
  created_at       timestamptz default now(),
  redeemed_at      timestamptz
);
create index if not exists referrals_referrer_idx on public.referrals(referrer_user_id);
create index if not exists referrals_code_idx on public.referrals(code);

-- ── Gifts: gift a reading/report or diyas (diaspora lever, blueprint §7) ─────
-- The diya debit happens via a coin_transactions row (source='gift_sent');
-- the recipient redeems claim_token → server creates the underlying purchase.
create table if not exists public.gifts (
  id                uuid primary key default gen_random_uuid(),
  sender_user_id    uuid not null references auth.users(id) on delete cascade,
  recipient_user_id uuid references auth.users(id) on delete set null,  -- null until a non-user claims
  recipient_contact text,                      -- email/phone for not-yet-users
  item              text not null,             -- 'full_life_reading' | 'diyas' | ...
  coin_cost         integer not null default 0,
  message           text,
  status            text not null default 'pending',  -- 'pending'|'claimed'|'expired'
  claim_token       text unique,
  created_at        timestamptz default now(),
  claimed_at        timestamptz
);
create index if not exists gifts_sender_idx on public.gifts(sender_user_id);
create index if not exists gifts_recipient_idx on public.gifts(recipient_user_id);

-- ── Ad rewards: rewarded-video tracking (blueprint §7) ──────────────────────
-- One row per verified ad view. UNIQUE(network, ssv_id) makes a duplicate
-- server-side-verification callback impossible to claim twice. Service-role only.
create table if not exists public.ad_rewards (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  network       text not null,               -- 'admob' | 'unity' | ...
  ssv_id        text not null,               -- server-side-verification id from the ad network
  coins_awarded integer not null default 0,
  created_at    timestamptz default now(),
  unique (network, ssv_id)
);
create index if not exists ad_rewards_user_idx on public.ad_rewards(user_id);

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
alter table public.memory_facts   enable row level security;
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
alter table public.day_tasks         enable row level security;
alter table public.time_capsules     enable row level security;
alter table public.moon_messages     enable row level security;
alter table public.coin_wallets      enable row level security;
alter table public.coin_transactions enable row level security;
alter table public.referrals         enable row level security;
alter table public.gifts             enable row level security;
alter table public.ad_rewards        enable row level security;

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

drop policy if exists memory_facts_owner on public.memory_facts;
create policy memory_facts_owner on public.memory_facts
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

drop policy if exists day_tasks_owner on public.day_tasks;
create policy day_tasks_owner on public.day_tasks
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists time_capsules_owner on public.time_capsules;
create policy time_capsules_owner on public.time_capsules
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists moon_messages_owner on public.moon_messages;
create policy moon_messages_owner on public.moon_messages
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());

-- Currency tables: a user may READ their own wallet/ledger/ads, but all WRITES
-- go through the server (service role bypasses RLS). No insert/update/delete
-- policy is granted to normal users → they can never alter their own balance.
drop policy if exists coin_wallets_read on public.coin_wallets;
create policy coin_wallets_read on public.coin_wallets
  for select using (user_id = auth.uid());

drop policy if exists coin_tx_read on public.coin_transactions;
create policy coin_tx_read on public.coin_transactions
  for select using (user_id = auth.uid());

drop policy if exists ad_rewards_read on public.ad_rewards;
create policy ad_rewards_read on public.ad_rewards
  for select using (user_id = auth.uid());

-- Referrals: the referrer (and the referee, once linked) can read; writes server-side.
drop policy if exists referrals_read on public.referrals;
create policy referrals_read on public.referrals
  for select using (referrer_user_id = auth.uid() or referee_user_id = auth.uid());

-- Gifts: sender and recipient can read their gifts; writes server-side
-- (the diya debit must be applied atomically on the server).
drop policy if exists gifts_read on public.gifts;
create policy gifts_read on public.gifts
  for select using (sender_user_id = auth.uid() or recipient_user_id = auth.uid());

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

-- ── Auto-stamp updated_at on rows that change ───────────────────────────────
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists coin_wallets_set_updated on public.coin_wallets;
create trigger coin_wallets_set_updated before update on public.coin_wallets
  for each row execute function public.set_updated_at();

drop trigger if exists ai_conv_set_updated on public.ai_conversations;
create trigger ai_conv_set_updated before update on public.ai_conversations
  for each row execute function public.set_updated_at();

drop trigger if exists ritual_set_updated on public.ritual_journeys;
create trigger ritual_set_updated before update on public.ritual_journeys
  for each row execute function public.set_updated_at();

drop trigger if exists memory_facts_set_updated on public.memory_facts;
create trigger memory_facts_set_updated before update on public.memory_facts
  for each row execute function public.set_updated_at();

drop trigger if exists day_tasks_set_updated on public.day_tasks;
create trigger day_tasks_set_updated before update on public.day_tasks
  for each row execute function public.set_updated_at();

drop trigger if exists time_capsules_set_updated on public.time_capsules;
create trigger time_capsules_set_updated before update on public.time_capsules
  for each row execute function public.set_updated_at();

-- Prune index: lets us cheaply delete stale shared daily content later.
create index if not exists cached_daily_created_idx on public.cached_daily(created_at);
