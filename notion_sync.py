"""
ICOS Notion Integration
Syncs branding, topics, and content ideas from Notion into the RAG system.
"""

import os
from notion_client import Client
from rag_core import ingest_user_profile, get_embedding
from supabase import create_client

# Initialize clients
notion = Client(auth=os.environ.get("NOTION_API_KEY", ""))
supabase = create_client(
    os.environ.get("SUPABASE_URL", ""),
    os.environ.get("SUPABASE_KEY", "")
)


def get_page_content(page_id: str) -> str:
    """Extract text content from a Notion page."""
    blocks = notion.blocks.children.list(block_id=page_id)
    text_parts = []
    
    for block in blocks.get("results", []):
        block_type = block.get("type")
        if block_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item"]:
            rich_text = block.get(block_type, {}).get("rich_text", [])
            for text in rich_text:
                text_parts.append(text.get("plain_text", ""))
    
    return "\n".join(text_parts)


def sync_branding_page(page_id: str) -> dict:
    """
    Sync a Notion page containing branding info into the RAG user_profile.
    
    Expected page structure:
    - Bio section
    - Values section
    - Expertise section
    - Voice samples section
    """
    content = get_page_content(page_id)
    
    # Chunk the content and ingest
    chunks = content.split("\n\n")
    ingested = []
    
    for chunk in chunks:
        if len(chunk.strip()) > 50:  # Only meaningful chunks
            result = ingest_user_profile(chunk, category="voice_sample")
            ingested.append(result)
    
    return {"ingested_chunks": len(ingested)}


def sync_topics_database(database_id: str) -> dict:
    """
    Sync topics from a Notion database into Supabase.
    
    Expected database properties:
    - Name (title)
    - Description (rich_text)
    - Active (checkbox)
    """
    results = notion.databases.query(database_id=database_id)
    synced = 0
    
    for page in results.get("results", []):
        props = page.get("properties", {})
        
        # Extract name
        name_prop = props.get("Name", {}).get("title", [])
        name = name_prop[0].get("plain_text", "") if name_prop else ""
        
        # Extract description
        desc_prop = props.get("Description", {}).get("rich_text", [])
        description = desc_prop[0].get("plain_text", "") if desc_prop else ""
        
        # Extract active status
        is_active = props.get("Active", {}).get("checkbox", True)
        
        if name:
            # Upsert into Supabase
            supabase.table("topics").upsert({
                "name": name,
                "description": description,
                "is_active": is_active
            }, on_conflict="name").execute()
            synced += 1
    
    return {"synced_topics": synced}


def sync_styles_database(database_id: str) -> dict:
    """
    Sync styles from a Notion database into Supabase.
    
    Expected database properties:
    - Name (title)
    - Instruction (rich_text)
    - Active (checkbox)
    """
    results = notion.databases.query(database_id=database_id)
    synced = 0
    
    for page in results.get("results", []):
        props = page.get("properties", {})
        
        name_prop = props.get("Name", {}).get("title", [])
        name = name_prop[0].get("plain_text", "") if name_prop else ""
        
        instr_prop = props.get("Instruction", {}).get("rich_text", [])
        instruction = instr_prop[0].get("plain_text", "") if instr_prop else ""
        
        is_active = props.get("Active", {}).get("checkbox", True)
        
        if name and instruction:
            supabase.table("styles").upsert({
                "name": name,
                "instruction": instruction,
                "is_active": is_active
            }, on_conflict="name").execute()
            synced += 1
    
    return {"synced_styles": synced}


def sync_content_ideas_database(database_id: str) -> list[dict]:
    """
    Get pending content ideas from Notion.
    
    Expected database properties:
    - Name (title) - The idea/topic
    - Status (select) - "Idea", "Drafted", "Scheduled"
    - Platform (select) - "LinkedIn", "Twitter"
    """
    results = notion.databases.query(
        database_id=database_id,
        filter={"property": "Status", "select": {"equals": "Idea"}}
    )
    
    ideas = []
    for page in results.get("results", []):
        props = page.get("properties", {})
        
        name_prop = props.get("Name", {}).get("title", [])
        name = name_prop[0].get("plain_text", "") if name_prop else ""
        
        platform_prop = props.get("Platform", {}).get("select", {})
        platform = platform_prop.get("name", "linkedin").lower()
        
        if name:
            ideas.append({
                "page_id": page["id"],
                "topic": name,
                "platform": platform
            })
    
    return ideas


def update_notion_with_draft(page_id: str, draft_content: str) -> None:
    """Update a Notion page with the generated draft."""
    notion.pages.update(
        page_id=page_id,
        properties={
            "Status": {"select": {"name": "Drafted"}}
        }
    )
    
    # Add draft as a child block
    notion.blocks.children.append(
        block_id=page_id,
        children=[{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": draft_content}}]
            }
        }]
    )


# CLI
if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv()
    
    if len(sys.argv) < 2:
        print("Usage: python notion_sync.py <command> [args]")
        print("Commands:")
        print("  sync-branding <page_id>     - Sync branding page to RAG")
        print("  sync-topics <database_id>   - Sync topics database")
        print("  sync-styles <database_id>   - Sync styles database")
        print("  get-ideas <database_id>     - Get pending content ideas")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "sync-branding" and len(sys.argv) > 2:
        result = sync_branding_page(sys.argv[2])
        print(f"Synced: {result}")
    
    elif command == "sync-topics" and len(sys.argv) > 2:
        result = sync_topics_database(sys.argv[2])
        print(f"Synced: {result}")
    
    elif command == "sync-styles" and len(sys.argv) > 2:
        result = sync_styles_database(sys.argv[2])
        print(f"Synced: {result}")
    
    elif command == "get-ideas" and len(sys.argv) > 2:
        ideas = sync_content_ideas_database(sys.argv[2])
        for idea in ideas:
            print(f"  - {idea['topic']} ({idea['platform']})")
    
    else:
        print(f"Unknown command: {command}")
