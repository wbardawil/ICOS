# Housekeeping & Integration Proposal - ICOS 2.0

This proposal outlines the steps to unify the Infinity Content OS (ICOS) into a cohesive system, integrating the missing Notion workflow nodes and aligning all agents.

## User Review Required

> [!IMPORTANT]
> This plan changes how data is synced. Instead of running multiple scripts, we will move to a **Unified Sync Service**. 
> Please ensure your Notion integration has "Internal Integration Token" access to:
> 1. The Branding Page
> 2. The Topics Database
> 3. The Content Ideas Database

## Proposed Changes

### 1. Unified Sync & Research Service
#### [NEW] [researcher_agent.py](file:///c:/Users/Dell/OneDrive%20-%20Ankar%20Group%20SA%20de%20CV%20%281%29/@%20Content%20Agents/researcher_agent.py)
A scraping agent that fetches news/trends and filters them against Wadi's expertise, saving them directly to the Notion "Ideas" database.

#### [NEW] [sync_service.py](file:///c:/Users/Dell/OneDrive%20-%20Ankar%20Group%20SA%20de%20CV%20%281%29/@%20Content%20Agents/sync_service.py)
Unifies `daily_sync.py` and `notion_sync.py`. Handles the full data bridge between Notion, Supabase, and local JSONs.

### 2. Full-Cycle n8n Workflow
#### [MODIFY] [icos_workflow.json](file:///c:/Users/Dell/OneDrive%20-%20Ankar%20Group%20SA%20de%20CV%20%281%29/@%20Content%20Agents/icos_workflow.json)
- **Schedule Expansion**: Update to 3x daily (e.g., 8 AM, 1 PM, 6 PM).
- **Notion Trigger**: Add a node to watch the "Content Ideas" database for status changes.
- **Notion Write-Back**: Ensure generated drafts are pushed back to the Notion page.

### 3. Voice & Impact Alignment
#### [MODIFY] [ghostwriter_agent.py](file:///c:/Users/Dell/OneDrive%20-%20Ankar%20Group%20SA%20de%20CV%20%281%29/@%20Content%20Agents/ghostwriter_agent.py)
Refactor prompt logic to prioritize "Impact Feedback" from the Analyst agent.

#### [MODIFY] [analyst_agent.py](file:///c:/Users/Dell/OneDrive%20-%20Ankar%20Group%20SA%20de%20CV%20%281%29/@%20Content%20Agents/analyst_agent.py)
Enhance scoring to include "Lead Potential" (e.g., call-to-action effectiveness).

### 4. Bilingual Newsletter Engine
#### [NEW] [newsletter_agent.py](file:///c:/Users/Dell/OneDrive%20-%20Ankar%20Group%20SA%20de%20CV%20%281%29/@%20Content%20Agents/newsletter_agent.py)
A long-form agent capable of cross-referencing successful weekly posts to draft a cohesive newsletter in both English and Spanish.

#### [NEW] [newsletter_workflow.json](file:///c:/Users/Dell/OneDrive%20-%20Ankar%20Group%20SA%20de%20CV%20%281%29/@%20Content%20Agents/newsletter_workflow.json)
A dedicated n8n workflow for fetching weekly winners, drafting the newsletter, and pushing it to a distribution platform (e.g., Substack/Beehiiv via API).

## Verification Plan
### Automated Tests
1. Run `python sync_service.py` and verify all Supabase tables and local JSONs are updated.
2. Test n8n trigger by changing a Notion item status.
3. Verify `/generate-post` includes recent analyst feedback in the prompt context.

### Manual Verification
1. Confirm that Slack notifications now include a clickable link back to the Notion Page.
