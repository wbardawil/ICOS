"""
ICOS API Wrapper
Exposes Ghostwriter and Visualist agents via HTTP for n8n integration.
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from sync_service import SyncService
from ghostwriter_agent import generate_post, generate_with_auto_combo
from visualist_agent import create_visual_for_post

app = FastAPI(title="ICOS API")
service = SyncService()

class PostRequest(BaseModel):
    topic: str
    style_instruction: Optional[str] = None
    platform: Optional[str] = "linkedin"

class VisualRequest(BaseModel):
    topic: str
    post_content: str
    style: Optional[str] = None

@app.post("/sync-profile")
def trigger_sync():
    """Sync Notion branding and strategy to local/Supabase"""
    try:
        results = {}
        results["branding"] = service.sync_branding()
        results["strategy"] = service.sync_strategy()
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class NotionUpdateRequest(BaseModel):
    page_id: str
    status: str
    draft: Optional[str] = None

@app.post("/notion-update")
def notion_update_page(req: NotionUpdateRequest):
    """Update a Notion page status and/or add a draft"""
    try:
        service.update_idea_status(req.page_id, req.status, req.draft)
        return {"status": "success", "message": f"Updated Notion page {req.page_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/next-combo")
def get_combo():
    """Get the next weighted topic/style combo"""
    from strategy_manager import get_weighted_combo
    combo = get_weighted_combo()
    if not combo:
        raise HTTPException(status_code=404, detail="No unused combinations available")
    return combo

@app.post("/generate-post")
def generate(req: PostRequest):
    """Generate a post for a specific topic"""
    try:
        content = generate_post(req.topic, req.style_instruction, req.platform)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-visual")
def generate_visual(req: VisualRequest):
    """Generate a visual concept for a post"""
    try:
        concept = create_visual_for_post(req.topic, req.post_content, req.style)
        return concept
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auto-run")
def auto_run():
    """Run the full auto combo generation"""
    try:
        result = generate_with_auto_combo()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
