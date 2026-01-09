"""
ICOS RAG System - Core Library
Handles embeddings, storage, and retrieval for the Content OS.
"""

import os
from typing import Optional
from dataclasses import dataclass
from supabase import create_client, Client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize clients
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL", ""),
    os.environ.get("SUPABASE_KEY", "")
)
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))


@dataclass
class ContentRecord:
    content: str
    topic: str
    style: str
    platform: str = "linkedin"
    virality_score: Optional[float] = None
    verdict: Optional[str] = None
    improvement_tip: Optional[str] = None


def get_embedding(text: str) -> list[float]:
    """Generate embedding using OpenAI."""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def ingest_user_profile(content: str, category: str) -> dict:
    """Add a user profile chunk to the knowledge base."""
    embedding = get_embedding(content)
    result = supabase.table("user_profile").insert({
        "content": content,
        "category": category,
        "embedding": embedding
    }).execute()
    return result.data[0] if result.data else {}


def ingest_content(record: ContentRecord) -> dict:
    """Add published content with performance data."""
    embedding = get_embedding(record.content)
    result = supabase.table("content_library").insert({
        "content": record.content,
        "topic": record.topic,
        "style": record.style,
        "platform": record.platform,
        "virality_score": record.virality_score,
        "verdict": record.verdict,
        "improvement_tip": record.improvement_tip,
        "embedding": embedding
    }).execute()
    return result.data[0] if result.data else {}


def search_similar_content(query: str, limit: int = 3) -> list[dict]:
    """Find semantically similar past content."""
    query_embedding = get_embedding(query)
    result = supabase.rpc("match_content", {
        "query_embedding": query_embedding,
        "match_threshold": 0.7,
        "match_count": limit
    }).execute()
    return result.data if result.data else []


def get_top_winners(limit: int = 5) -> list[dict]:
    """Retrieve highest performing content."""
    result = supabase.rpc("get_winners", {"limit_count": limit}).execute()
    return result.data if result.data else []


def get_recent_improvement_tips(limit: int = 5) -> list[str]:
    """Get recent feedback to avoid past mistakes."""
    result = supabase.rpc("get_recent_tips", {"limit_count": limit}).execute()
    return [r["improvement_tip"] for r in result.data] if result.data else []


def build_rag_context(topic: str) -> str:
    """Build context for the Ghostwriter from RAG sources."""
    # Get similar winning content
    similar = search_similar_content(topic, limit=3)
    winners = [c for c in similar if c.get("verdict") == "WINNER"]
    
    # Get improvement tips
    tips = get_recent_improvement_tips(limit=5)
    
    context_parts = []
    
    if winners:
        context_parts.append("## Examples of High-Performing Content on This Topic:")
        for w in winners:
            context_parts.append(f"- Score: {w['virality_score']}\n{w['content'][:300]}...")
    
    if tips:
        context_parts.append("\n## Avoid These Mistakes (From Recent Analysis):")
        for tip in tips:
            context_parts.append(f"- {tip}")
    
    return "\n".join(context_parts) if context_parts else "No historical data yet."
