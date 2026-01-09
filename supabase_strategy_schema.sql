-- Additional Supabase Schema for Dynamic Strategy Management
-- Run this AFTER supabase_schema.sql

-- Table: Topics (Y-Axis of Strategy Matrix)
create table topics (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    description text,
    is_active boolean default true,
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now()
);

-- Table: Styles (X-Axis of Strategy Matrix)
create table styles (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    instruction text not null,
    is_active boolean default true,
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now()
);

-- Table: Content Schedule (Tracks which combos have been used)
create table content_schedule (
    id uuid primary key default gen_random_uuid(),
    topic_id uuid references topics(id),
    style_id uuid references styles(id),
    scheduled_date date not null,
    status text default 'planned' check (status in ('planned', 'drafted', 'published')),
    content_id uuid references content_library(id),
    created_at timestamp with time zone default now()
);

-- Seed initial topics from strategy_matrix.json
insert into topics (name, description) values
    ('SaaS Growth', 'Scaling software businesses'),
    ('Solopreneurship', 'Building one-person businesses'),
    ('No-Code Systems', 'Automation without programming'),
    ('Remote Leadership', 'Managing distributed teams'),
    ('Personal Branding', 'Building authority online');

-- Seed initial styles from strategy_matrix.json
insert into styles (name, instruction) values
    ('The Contrarian', 'State a commonly held belief in the industry, then dismantle it with data or experience. Polarizing but respectful.'),
    ('The Observation', 'Start with ''I analyzed X...'' or ''I watched X...''. Deduce a pattern that others are missing.'),
    ('The Actionable', 'Pure ''How-to''. Zero fluff. Use a numbered list. Promise a specific outcome in the hook.'),
    ('The Motivational', 'Focus on the struggle vs. the success. Use short, punchy sentences. End with an encouraging call to action.'),
    ('The Analytical', 'Break down a complex topic into simple components. Use ''First Principles'' thinking.'),
    ('X vs Y', 'Compare the ''Old Way'' of doing things vs. the ''New Way''. Use a visual comparison format.');

-- Function: Get a random unused topic/style combination
create or replace function get_next_combo()
returns table (topic_name text, topic_id uuid, style_name text, style_id uuid, style_instruction text)
language sql
as $$
    with used_combos as (
        select topic_id, style_id from content_schedule
        where scheduled_date >= current_date - interval '30 days'
    )
    select 
        t.name as topic_name,
        t.id as topic_id,
        s.name as style_name,
        s.id as style_id,
        s.instruction as style_instruction
    from topics t
    cross join styles s
    where t.is_active = true and s.is_active = true
    and not exists (
        select 1 from used_combos uc
        where uc.topic_id = t.id and uc.style_id = s.id
    )
    order by random()
    limit 1;
$$;

-- Function: Get a weighted topic/style combination based on performance
create or replace function get_weighted_combo()
returns table (topic_name text, topic_id uuid, style_name text, style_id uuid, style_instruction text)
language plpgsql
as $$
begin
    return query
    with style_weights as (
        -- Calculate average virality score per style name
        -- We use style name to match content_library.style
        select 
            s.id as style_id,
            s.name as style_name,
            -- Weight = 1.0 (base) + average virality score (if any)
            -- This ensures we always try new styles (weight 1.0) but favor winners
            (1.0 + coalesce(avg(cl.virality_score), 0)) as weight
        from styles s
        left join content_library cl on cl.style = s.name
        where s.is_active = true
        group by s.id, s.name
    ),
    used_combos as (
        select sc.topic_id, sc.style_id 
        from content_schedule sc
        where sc.scheduled_date >= current_date - interval '14 days'
    ),
    available_combos as (
        select 
            t.name as topic_name,
            t.id as topic_id,
            sw.style_name,
            sw.style_id,
            s.instruction as style_instruction,
            sw.weight
        from topics t
        cross join styles s
        join style_weights sw on sw.style_id = s.id
        where t.is_active = true and s.is_active = true
        and not exists (
            select 1 from used_combos uc
            where uc.topic_id = t.id and uc.style_id = s.id
        )
    )
    select 
        ac.topic_name,
        ac.topic_id,
        ac.style_name,
        ac.style_id,
        ac.style_instruction
    from available_combos ac
    -- Random selection weighted by performance
    -- We use a power of the random number times the weight to favor higher weights
    order by (random() * ac.weight) desc
    limit 1;
end;
$$;
