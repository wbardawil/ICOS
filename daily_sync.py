"""
ICOS Daily Sync Script
Runs daily to sync your Notion profile to the local user_profile.json

Schedule this with:
- Windows Task Scheduler
- Linux/Mac cron: 0 6 * * * python /path/to/daily_sync.py
- Make.com scheduled webhook
"""

import os
import json
from datetime import datetime
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.environ.get("NOTION_API_KEY", ""))

# Your CMBA Notion page ID (extracted from URL)
NOTION_PAGE_ID = os.environ.get("NOTION_BRANDING_PAGE_ID", "1be03013ad1e80a6a996ea7ee43e6c41")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "user_profile.json")
STRATEGY_PATH = os.path.join(os.path.dirname(__file__), "strategy_matrix.json")


def extract_page_content(page_id: str) -> str:
    """Extract text from a Notion page."""
    blocks = notion.blocks.children.list(block_id=page_id)
    text_parts = []
    
    for block in blocks.get("results", []):
        block_type = block.get("type")
        if block_type in ["paragraph", "heading_1", "heading_2", "heading_3", 
                          "bulleted_list_item", "numbered_list_item", "callout"]:
            rich_text = block.get(block_type, {}).get("rich_text", [])
            for text in rich_text:
                text_parts.append(text.get("plain_text", ""))
    
    return "\n".join(text_parts)


def extract_child_pages(page_id: str) -> dict:
    """Extract content from child pages."""
    blocks = notion.blocks.children.list(block_id=page_id)
    child_content = {}
    
    for block in blocks.get("results", []):
        if block.get("type") == "child_page":
            child_id = block["id"]
            child_title = block.get("child_page", {}).get("title", "Untitled")
            child_content[child_title] = extract_page_content(child_id)
    
    return child_content


def sync_profile():
    """Main sync function."""
    print(f"[{datetime.now()}] Starting Notion sync...")
    
    # Extract main page
    main_content = extract_page_content(NOTION_PAGE_ID)
    child_pages = extract_child_pages(NOTION_PAGE_ID)
    
    # Load existing profile or create new
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            profile = json.load(f)
    else:
        profile = {}
    
    # Update with fresh content
    profile["last_synced"] = datetime.now().isoformat()
    profile["raw_content"] = main_content
    profile["child_pages"] = child_pages
    
    # Save updated profile
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    
    print(f"[{datetime.now()}] Sync complete. Profile saved to {OUTPUT_PATH}")
    return profile


if __name__ == "__main__":
    sync_profile()
