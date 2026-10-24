-- Run in Supabase SQL Editor after creating the two Auth users.
-- This SQL creates shared tables and a private Storage bucket.
create extension if not exists pgcrypto;

create table if not exists public.couple_members (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text not null unique,
  created_at timestamptz not null default now()
);

-- Add the two users after creating them in Authentication > Users.
-- Replace UUID and email with actual Auth user IDs and emails:
-- insert into public.couple_members (user_id, email) values
-- ('ACA-AUTH-USER-UUID', 'aca@example.com'),
-- ('AKMAL-AUTH-USER-UUID', 'akmal@example.com');

create or replace function public.is_couple_member()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.couple_members cm
    where cm.user_id = auth.uid()
  );
$$;

revoke all on function public.is_couple_member() from public;
grant execute on function public.is_couple_member() to authenticated;

create table if not exists public.memories (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  memory_date date not null,
  location text not null default '',
  story text not null,
  favorite text not null default '',
  note text not null default '',
  photo_paths text[] not null default '{}',
  created_by uuid not null references auth.users(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.favorites (
  id uuid primary key default gen_random_uuid(),
  category text not null default 'LITTLE THINGS',
  text text not null,
  created_by uuid not null references auth.users(id),
  created_at timestamptz not null default now()
);

create table if not exists public.letters (
  id uuid primary key default gen_random_uuid(),
  body text not null default '',
  updated_by uuid not null references auth.users(id),
  updated_at timestamptz not null default now()
);

alter table public.couple_members enable row level security;
alter table public.memories enable row level security;
alter table public.favorites enable row level security;
alter table public.letters enable row level security;

-- Members can see only their own membership row. Membership management is done
-- in SQL Editor by the project owner, not from the client.
drop policy if exists "member can read own membership" on public.couple_members;
create policy "member can read own membership"
on public.couple_members for select to authenticated
using (user_id = auth.uid());

drop policy if exists "couple members read memories" on public.memories;
create policy "couple members read memories"
on public.memories for select to authenticated
using (public.is_couple_member());
drop policy if exists "couple members insert memories" on public.memories;
create policy "couple members insert memories"
on public.memories for insert to authenticated
with check (public.is_couple_member() and created_by = auth.uid());
drop policy if exists "couple members update memories" on public.memories;
create policy "couple members update memories"
on public.memories for update to authenticated
using (public.is_couple_member())
with check (public.is_couple_member());
drop policy if exists "couple members delete memories" on public.memories;
create policy "couple members delete memories"
on public.memories for delete to authenticated
using (public.is_couple_member());

drop policy if exists "couple members read favorites" on public.favorites;
create policy "couple members read favorites" on public.favorites for select to authenticated using (public.is_couple_member());
drop policy if exists "couple members insert favorites" on public.favorites;
create policy "couple members insert favorites" on public.favorites for insert to authenticated with check (public.is_couple_member() and created_by = auth.uid());
drop policy if exists "couple members delete favorites" on public.favorites;
create policy "couple members delete favorites" on public.favorites for delete to authenticated using (public.is_couple_member());

drop policy if exists "couple members read letters" on public.letters;
create policy "couple members read letters" on public.letters for select to authenticated using (public.is_couple_member());
drop policy if exists "couple members insert letters" on public.letters;
create policy "couple members insert letters" on public.letters for insert to authenticated with check (public.is_couple_member() and updated_by = auth.uid());
drop policy if exists "couple members update letters" on public.letters;
create policy "couple members update letters" on public.letters for update to authenticated using (public.is_couple_member()) with check (public.is_couple_member());

grant select on public.couple_members to authenticated;
grant select, insert, update, delete on public.memories to authenticated;
grant select, insert, delete on public.favorites to authenticated;
grant select, insert, update on public.letters to authenticated;

-- Private photo bucket. Signed URLs are generated by the app after authentication.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('memories', 'memories', false, 12582912, array['image/jpeg','image/png','image/webp'])
on conflict (id) do update set public = false;

drop policy if exists "couple can read memory photos" on storage.objects;
create policy "couple can read memory photos" on storage.objects for select to authenticated
using (bucket_id = 'memories' and public.is_couple_member());
drop policy if exists "couple can upload memory photos" on storage.objects;
create policy "couple can upload memory photos" on storage.objects for insert to authenticated
with check (bucket_id = 'memories' and public.is_couple_member());
drop policy if exists "couple can update memory photos" on storage.objects;
create policy "couple can update memory photos" on storage.objects for update to authenticated
using (bucket_id = 'memories' and public.is_couple_member())
with check (bucket_id = 'memories' and public.is_couple_member());
drop policy if exists "couple can delete memory photos" on storage.objects;
create policy "couple can delete memory photos" on storage.objects for delete to authenticated
using (bucket_id = 'memories' and public.is_couple_member());
