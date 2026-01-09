"""
ICOS Strategy Manager
CRUD operations for topics and styles in the strategy matrix.
"""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL", ""),
    os.environ.get("SUPABASE_KEY", "")
)


# ========== TOPICS ==========

def list_topics(active_only: bool = True) -> list[dict]:
    """List all topics."""
    query = supabase.table("topics").select("*")
    if active_only:
        query = query.eq("is_active", True)
    result = query.order("name").execute()
    return result.data if result.data else []


def add_topic(name: str, description: str = "") -> dict:
    """Add a new topic."""
    result = supabase.table("topics").insert({
        "name": name,
        "description": description
    }).execute()
    return result.data[0] if result.data else {}


def update_topic(topic_id: str, name: str = None, description: str = None, is_active: bool = None) -> dict:
    """Update an existing topic."""
    updates = {"updated_at": "now()"}
    if name is not None:
        updates["name"] = name
    if description is not None:
        updates["description"] = description
    if is_active is not None:
        updates["is_active"] = is_active
    
    result = supabase.table("topics").update(updates).eq("id", topic_id).execute()
    return result.data[0] if result.data else {}


def delete_topic(topic_id: str) -> bool:
    """Soft delete a topic (set inactive)."""
    result = supabase.table("topics").update({"is_active": False}).eq("id", topic_id).execute()
    return len(result.data) > 0 if result.data else False


# ========== STYLES ==========

def list_styles(active_only: bool = True) -> list[dict]:
    """List all styles."""
    query = supabase.table("styles").select("*")
    if active_only:
        query = query.eq("is_active", True)
    result = query.order("name").execute()
    return result.data if result.data else []


def add_style(name: str, instruction: str) -> dict:
    """Add a new style."""
    result = supabase.table("styles").insert({
        "name": name,
        "instruction": instruction
    }).execute()
    return result.data[0] if result.data else {}


def update_style(style_id: str, name: str = None, instruction: str = None, is_active: bool = None) -> dict:
    """Update an existing style."""
    updates = {"updated_at": "now()"}
    if name is not None:
        updates["name"] = name
    if instruction is not None:
        updates["instruction"] = instruction
    if is_active is not None:
        updates["is_active"] = is_active
    
    result = supabase.table("styles").update(updates).eq("id", style_id).execute()
    return result.data[0] if result.data else {}


def delete_style(style_id: str) -> bool:
    """Soft delete a style (set inactive)."""
    result = supabase.table("styles").update({"is_active": False}).eq("id", style_id).execute()
    return len(result.data) > 0 if result.data else False


# ========== STRATEGY SELECTION ==========

def get_next_combo() -> Optional[dict]:
    """Get a random unused topic/style combination."""
    result = supabase.rpc("get_next_combo").execute()
    return result.data[0] if result.data else None


def get_weighted_combo() -> Optional[dict]:
    """Get a performance-based topic/style combination."""
    result = supabase.rpc("get_weighted_combo").execute()
    return result.data[0] if result.data else None


def schedule_content(topic_id: str, style_id: str, scheduled_date: str) -> dict:
    """Schedule a topic/style combo for a specific date."""
    result = supabase.table("content_schedule").insert({
        "topic_id": topic_id,
        "style_id": style_id,
        "scheduled_date": scheduled_date
    }).execute()
    return result.data[0] if result.data else {}


def get_schedule(days: int = 30) -> list[dict]:
    """Get upcoming scheduled content."""
    result = supabase.table("content_schedule").select(
        "*, topics(name), styles(name)"
    ).gte("scheduled_date", "now()").order("scheduled_date").limit(days).execute()
    return result.data if result.data else []


# ========== CLI ==========

if __name__ == "__main__":
    import sys
    import json
    from dotenv import load_dotenv
    load_dotenv()
    
    if len(sys.argv) < 2:
        print("Usage: python strategy_manager.py <command>")
        print("Commands: list-topics, list-styles, add-topic, add-style, next-combo, weighted-combo")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list-topics":
        topics = list_topics()
        for t in topics:
            print(f"  [{t['id'][:8]}] {t['name']}: {t.get('description', '')}")
    
    elif command == "list-styles":
        styles = list_styles()
        for s in styles:
            print(f"  [{s['id'][:8]}] {s['name']}")
            print(f"      → {s['instruction'][:80]}...")
    
    elif command == "add-topic" and len(sys.argv) >= 3:
        name = sys.argv[2]
        desc = sys.argv[3] if len(sys.argv) > 3 else ""
        result = add_topic(name, desc)
        print(f"Added: {result}")
    
    elif command == "add-style" and len(sys.argv) >= 4:
        name = sys.argv[2]
        instruction = sys.argv[3]
        result = add_style(name, instruction)
        print(f"Added: {result}")
    
    elif command == "next-combo":
        combo = get_next_combo()
        if combo:
            print(f"Topic: {combo['topic_name']}")
            print(f"Style: {combo['style_name']}")
            print(f"Instruction: {combo['style_instruction']}")
        else:
            print("No unused combinations available!")
    
    elif command == "weighted-combo":
        combo = get_weighted_combo()
        if combo:
            print(f"Topic: {combo['topic_name']}")
            print(f"Style: {combo['style_name']} (Weighted by performance)")
            print(f"Instruction: {combo['style_instruction']}")
        else:
            print("No unused combinations available!")
    
    else:
        print(f"Unknown command: {command}")
