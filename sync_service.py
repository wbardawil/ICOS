"""
ICOS Unified Sync Service
Unifies branding sync, strategy matrix sync, and content idea fetching.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from notion_client import Client
from supabase import create_client, Client as SupabaseClient
from dotenv import load_dotenv
from rag_core import ingest_user_profile

load_dotenv()

class SyncService:
    def __init__(self):
        self.notion = Client(auth=os.environ.get("NOTION_API_KEY", ""))
        self.supabase: SupabaseClient = create_client(
            os.environ.get("SUPABASE_URL", ""),
            os.environ.get("SUPABASE_KEY", "")
        )
        self.branding_page_id = os.environ.get("NOTION_BRANDING_PAGE_ID")
        self.topics_db_id = os.environ.get("NOTION_TOPICS_DB_ID")
        self.styles_db_id = os.environ.get("NOTION_STYLES_DB_ID")
        self.ideas_db_id = os.environ.get("NOTION_IDEAS_DB_ID")
        
        self.profile_path = os.path.join(os.path.dirname(__file__), "user_profile.json")

    def _get_page_text(self, page_id: str) -> str:
        """Helper to extract text from a Notion page."""
        blocks = self.notion.blocks.children.list(block_id=page_id)
        text_parts = []
        for block in blocks.get("results", []):
            block_type = block.get("type")
            if block_type in ["paragraph", "heading_1", "heading_2", "heading_3", 
                              "bulleted_list_item", "numbered_list_item", "callout"]:
                rich_text = block.get(block_type, {}).get("rich_text", [])
                text_parts.append(" ".join([t.get("plain_text", "") for t in rich_text]))
        return "\n".join(text_parts)

    def sync_branding(self) -> Dict[str, Any]:
        """Syncs the branding page to local JSON and Supabase RAG."""
        if not self.branding_page_id:
            return {"error": "NOTION_BRANDING_PAGE_ID not set"}
            
        print(f"Syncing Branding: {self.branding_page_id}")
        content = self._get_page_text(self.branding_page_id)
        
        # 1. Update local JSON
        profile = {
            "last_synced": datetime.now().isoformat(),
            "raw_content": content
        }
        with open(self.profile_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
            
        # 2. Ingest into RAG (Supabase)
        # We split by double newlines for chunking
        chunks = [c for c in content.split("\n\n") if len(c.strip()) > 50]
        for chunk in chunks:
            ingest_user_profile(chunk, category="bio") # Defaulting to bio for now
            
        return {"status": "success", "chunks_ingested": len(chunks)}

    def sync_strategy(self) -> Dict[str, Any]:
        """Syncs Topics and Styles databases to Supabase."""
        results = {"topics": 0, "styles": 0}
        
        if self.topics_db_id:
            topics = self.notion.databases.query(database_id=self.topics_db_id).get("results", [])
            for page in topics:
                name = page["properties"]["Name"]["title"][0]["plain_text"]
                desc_obj = page["properties"].get("Description", {}).get("rich_text", [])
                description = desc_obj[0]["plain_text"] if desc_obj else ""
                
                self.supabase.table("topics").upsert({
                    "name": name,
                    "description": description,
                    "is_active": True
                }, on_conflict="name").execute()
                results["topics"] += 1
                
        if self.styles_db_id:
            styles = self.notion.databases.query(database_id=self.styles_db_id).get("results", [])
            for page in styles:
                name = page["properties"]["Name"]["title"][0]["plain_text"]
                instr_obj = page["properties"].get("Instruction", {}).get("rich_text", [])
                instruction = instr_obj[0]["plain_text"] if instr_obj else ""
                
                self.supabase.table("styles").upsert({
                    "name": name,
                    "instruction": instruction,
                    "is_active": True
                }, on_conflict="name").execute()
                results["styles"] += 1
                
        return results

    def get_pending_ideas(self) -> List[Dict[str, Any]]:
        """Fetches ideas with status 'Generate' or 'New'."""
        if not self.ideas_db_id:
            return []
            
        query = {
            "database_id": self.ideas_db_id,
            "filter": {
                "or": [
                    {"property": "Status", "select": {"equals": "Generate"}},
                    {"property": "Status", "select": {"equals": "Idea"}}
                ]
            }
        }
        results = self.notion.databases.query(**query).get("results", [])
        
        ideas = []
        for page in results:
            name = page["properties"]["Name"]["title"][0]["plain_text"]
            ideas.append({
                "id": page["id"],
                "topic": name,
                "platform": "linkedin" # Default
            })
        return ideas

    def add_idea(self, topic: str, platform: str = "linkedin", source: str = "Research Agent"):
        """Adds a new idea to the Notion database."""
        if not self.ideas_db_id:
            return
            
        self.notion.pages.create(
            parent={"database_id": self.ideas_db_id},
            properties={
                "Name": {"title": [{"text": {"content": topic}}]},
                "Status": {"select": {"name": "Idea"}},
                "Platform": {"select": {"name": platform.capitalize()}},
                "Source": {"rich_text": [{"text": {"content": source}}]}
            }
        )

    def update_idea_status(self, page_id: str, status: str, draft: str = None):
        """Updates the status and adds draft content to a Notion page."""
        properties = {"Status": {"select": {"name": status}}}
        self.notion.pages.update(page_id=page_id, properties=properties)
        
        if draft:
            self.notion.blocks.children.append(
                block_id=page_id,
                children=[{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": draft}}]
                    }
                }]
            )

if __name__ == "__main__":
    service = SyncService()
    print("Running Full Sync...")
    print(service.sync_branding())
    print(service.sync_strategy())
    print(f"Pending Ideas: {len(service.get_pending_ideas())}")
