# Infinity Content OS - Deployment Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ICOS PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [Notion Sync]  →  [Ghostwriter]  →  [Visualist]  →  [Review]  │
│        ↓                 ↓                ↓              ↓      │
│   user_profile      Post Draft      Image Prompt    Slack/You   │
│                                                          ↓      │
│                                                      [Publish]  │
│                                                          ↓      │
│   ←←←←←←←←←←←←←←←  [Analyst]  ←←←←←←←←←←←←←  (24h later)        │
│        ↓                                                        │
│   RAG Updated (learns from performance)                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Files

| Agent | File | Purpose |
|-------|------|---------|
| Ghostwriter | `ghostwriter_agent.py` | Writes posts using RAG context |
| Visualist | `visualist_agent.py` | Creates image concepts + DALL-E |
| Analyst | `analyst_agent.py` | Scores performance, stores learnings |
| Notion Sync | `notion_sync.py` | Pulls branding from Notion |
| Daily Sync | `daily_sync.py` | Scheduled profile refresh |
| Strategy | `strategy_manager.py` | CRUD for topics/styles |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up .env (copy from .env.example)

# 3. Run database schema in Supabase

# 4. Generate a post with visual
python ghostwriter_agent.py "Your topic here"
python visualist_agent.py "Your topic here" --generate
```

## Make.com Workflow

See `make_blueprint.md` for the full automation setup.
