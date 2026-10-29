-- NatureClean AI · Supabase SQL setup (run once in your project's SQL Editor).
-- Requires Supabase Auth with email/password enabled.
-- Scores represent self-reported participation, NOT verified litter removal.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  nickname text not null check (nickname ~ '^[A-Za-z0-9_-]{3,24}$'),
  created_at timestamptz not null default now()
);

-- Unique usernames irrespective of case.
create unique index if not exists natureclean_profiles_nickname_unique
  on public.profiles (lower(nickname));

create table if not exists public.submissions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  photo_hash text not null unique check (photo_hash ~ '^[0-9a-f]{64}$'),
  ai_count integer not null default 0 check (ai_count between 0 and 1000),
  counts jsonb not null,
  confirmed_count integer not null default 0,
  points integer not null default 0,
  created_at timestamptz not null default now()
);

create index if not exists natureclean_submissions_user_date
  on public.submissions (user_id, created_at desc);
create index if not exists natureclean_submissions_date
  on public.submissions (created_at desc);

-- Calculate points in the database. Clients CANNOT choose their points.
create or replace function public.natureclean_score_submission()
returns trigger
language plpgsql
set search_path = ''
as $$
declare
  item record;
  amount bigint;
  total bigint := 0;
begin
  if pg_catalog.jsonb_typeof(new.counts) <> 'object' then
    raise exception 'Counts must be an object';
  end if;
  for item in select key, value from pg_catalog.jsonb_each_text(new.counts) loop
    if item.key not in (
      'plastic_bottle', 'plastic_bag', 'plastic_packaging', 'beverage_can',
      'paper_cardboard', 'glass_bottle', 'pen', 'other_litter'
    ) then
      raise exception 'Unknown waste category';
    end if;
    if item.value !~ '^(0|[1-9][0-9]*)$' or length(item.value) > 3 then
      raise exception 'Invalid item count';
    end if;
    amount := item.value::bigint;
    if amount > 100 then
      raise exception 'Too many items in one category';
    end if;
    total := total + amount;
  end loop;
  if total < 1 or total > 100 then
    raise exception 'Confirm between 1 and 100 items';
  end if;
  new.confirmed_count := total;
  new.points := total * 10;
  return new;
end;
$$;

drop trigger if exists natureclean_score_before_insert on public.submissions;
create trigger natureclean_score_before_insert
before insert on public.submissions
for each row execute function public.natureclean_score_submission();

-- Access control: users can read their own submissions and profiles, not edit points.
alter table public.profiles enable row level security;
alter table public.submissions enable row level security;

revoke all on table public.profiles from anon, authenticated;
revoke all on table public.submissions from anon, authenticated;
grant select, insert (id, nickname), update (nickname) on public.profiles to authenticated;
grant select, insert (user_id, photo_hash, ai_count, counts) on public.submissions to authenticated;

drop policy if exists natureclean_profiles_read_own on public.profiles;
create policy natureclean_profiles_read_own on public.profiles
for select to authenticated using ((select auth.uid()) = id);

drop policy if exists natureclean_profiles_insert_own on public.profiles;
create policy natureclean_profiles_insert_own on public.profiles
for insert to authenticated with check ((select auth.uid()) = id);

drop policy if exists natureclean_profiles_update_own on public.profiles;
create policy natureclean_profiles_update_own on public.profiles
for update to authenticated using ((select auth.uid()) = id)
with check ((select auth.uid()) = id);

drop policy if exists natureclean_submissions_read_own on public.submissions;
create policy natureclean_submissions_read_own on public.submissions
for select to authenticated using ((select auth.uid()) = user_id);

drop policy if exists natureclean_submissions_insert_own on public.submissions;
create policy natureclean_submissions_insert_own on public.submissions
for insert to authenticated with check ((select auth.uid()) = user_id);

-- Public *aggregated* ranking (authenticated-only). No emails or photo hashes revealed.
-- Intentional SECURITY DEFINER with fixed search_path, fixed output and validated period.
create or replace function public.natureclean_leaderboard(p_period text default 'month')
returns table(nickname text, points bigint, items bigint, photos bigint)
language plpgsql
security definer
set search_path = ''
as $$
begin
  if p_period not in ('month', 'all') then
    raise exception 'Invalid leaderboard period';
  end if;
  return query
  select p.nickname,
         coalesce(sum(s.points), 0)::bigint,
         coalesce(sum(s.confirmed_count), 0)::bigint,
         count(s.id)::bigint
  from public.submissions s
  join public.profiles p on p.id = s.user_id
  where p_period = 'all' or (
    s.created_at >= (pg_catalog.date_trunc('month', now() at time zone 'Europe/Amsterdam')
                      at time zone 'Europe/Amsterdam')
    and s.created_at < ((pg_catalog.date_trunc('month', now() at time zone 'Europe/Amsterdam')
                        + interval '1 month') at time zone 'Europe/Amsterdam')
  )
  group by p.id, p.nickname
  order by sum(s.points) desc, count(s.id) desc, p.nickname asc
  limit 50;
end;
$$;

-- Personal totals and current-month totals; respects user_id from auth, not a client arg.
create or replace function public.natureclean_my_stats()
returns jsonb
language sql
stable
security invoker
set search_path = ''
as $$
  select pg_catalog.jsonb_build_object(
      'total_points', coalesce(sum(points), 0),
      'total_items', coalesce(sum(confirmed_count), 0),
      'photos', count(*),
      'month_points', coalesce(sum(points) filter (where
        created_at >= (pg_catalog.date_trunc('month', now() at time zone 'Europe/Amsterdam')
                       at time zone 'Europe/Amsterdam') and
        created_at < ((pg_catalog.date_trunc('month', now() at time zone 'Europe/Amsterdam')
                       + interval '1 month') at time zone 'Europe/Amsterdam')
      ), 0),
      'month_items', coalesce(sum(confirmed_count) filter (where
        created_at >= (pg_catalog.date_trunc('month', now() at time zone 'Europe/Amsterdam')
                       at time zone 'Europe/Amsterdam') and
        created_at < ((pg_catalog.date_trunc('month', now() at time zone 'Europe/Amsterdam')
                       + interval '1 month') at time zone 'Europe/Amsterdam')
      ), 0)
    )
  from public.submissions
  where user_id = (select auth.uid());
$$;

create or replace function public.natureclean_my_history()
returns table(month text, points bigint, items bigint)
language sql
stable
security invoker
set search_path = ''
as $$
  select to_char(created_at at time zone 'Europe/Amsterdam', 'YYYY-MM') as month,
         sum(s.points)::bigint as points,
         sum(s.confirmed_count)::bigint as items
  from public.submissions s
  where s.user_id = (select auth.uid())
  group by 1
  order by 1 desc
  limit 24;
$$;

-- Restrict RPC invocation to authenticated users.
revoke execute on function public.natureclean_leaderboard(text) from public, anon;
revoke execute on function public.natureclean_my_stats() from public, anon;
revoke execute on function public.natureclean_my_history() from public, anon;
revoke execute on function public.natureclean_score_submission() from public, anon, authenticated;
grant execute on function public.natureclean_leaderboard(text) to authenticated;
grant execute on function public.natureclean_my_stats() to authenticated;
grant execute on function public.natureclean_my_history() to authenticated;
