-- Supabase SQL Schema for ICOS RAG System
-- Run this in Supabase SQL Editor

-- Enable pgvector extension
create extension if not exists vector;

-- Table: User Profile Chunks
create table user_profile (
    id uuid primary key default gen_random_uuid(),
    content text not null,
    category text check (category in ('bio', 'expertise', 'values', 'voice_sample')),
    embedding vector(1536),
    created_at timestamp with time zone default now()
);

-- Table: Content Library (Posts + Performance)
create table content_library (
    id uuid primary key default gen_random_uuid(),
    content text not null,
    topic text,
    style text,
    platform text check (platform in ('linkedin', 'twitter', 'newsletter')),
    virality_score float,
    verdict text check (verdict in ('FLOP', 'AVERAGE', 'WINNER')),
    improvement_tip text,
    embedding vector(1536),
    published_at timestamp with time zone,
    analyzed_at timestamp with time zone default now()
);

-- Function: Semantic Search for Similar Content
create or replace function match_content(
    query_embedding vector(1536),
    match_threshold float default 0.7,
    match_count int default 5
)
returns table (
    id uuid,
    content text,
    topic text,
    style text,
    virality_score float,
    verdict text,
    improvement_tip text,
    similarity float
)
language plpgsql
as $$
begin
    return query
    select
        cl.id,
        cl.content,
        cl.topic,
        cl.style,
        cl.virality_score,
        cl.verdict,
        cl.improvement_tip,
        1 - (cl.embedding <=> query_embedding) as similarity
    from content_library cl
    where 1 - (cl.embedding <=> query_embedding) > match_threshold
    order by cl.embedding <=> query_embedding
    limit match_count;
end;
$$;

-- Function: Get Top Winners
create or replace function get_winners(limit_count int default 5)
returns table (
    id uuid,
    content text,
    topic text,
    virality_score float,
    improvement_tip text
)
language sql
as $$
    select id, content, topic, virality_score, improvement_tip
    from content_library
    where verdict = 'WINNER'
    order by virality_score desc
    limit limit_count;
$$;

-- Function: Get Recent Improvement Tips
create or replace function get_recent_tips(limit_count int default 5)
returns table (improvement_tip text)
language sql
as $$
    select improvement_tip
    from content_library
    where improvement_tip is not null
    order by analyzed_at desc
    limit limit_count;
$$;

-- Index for faster similarity search
create index on content_library using ivfflat (embedding vector_cosine_ops) with (lists = 100);
create index on user_profile using ivfflat (embedding vector_cosine_ops) with (lists = 100);
