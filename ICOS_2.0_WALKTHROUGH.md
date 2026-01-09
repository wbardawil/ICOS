# ICOS 2.0: Full Lifecycle Content OS - Walkthrough

Welcome to your new **Infinity Content OS (ICOS) 2.0**. This system is now a bridge between your Notion strategy hub and your LinkedIn audience, managing everything from raw research to bilingual newsletters.

## 🚀 What's New?

### 1. The Autonomous Researcher
The `researcher_agent.py` now runs daily, scans the web for trends, and populates your **Notion Content Ideas** database with fresh topics. It focuses on your pillars: *SaaS Growth, Solopreneurship, and Autonomous Systems*.

### 2. High-Impact Writing Loop
The Ghostwriter now listens to the Analyst. If a post gets scored, the **Improvement Tips** are automatically injected into the next draft's prompt context. Your voice literally gets smarter with every post.

### 3. Bilingual Newsletter Engine
Every Friday, the `newsletter_agent.py` fetches your winners and drafts a long-form deep dive in both **English and Spanish**.
- **Location:** Artifacts or pushed to Slack `#newsletter-drafts`.

### 4. 3x Daily Multi-Platform n8n
Your n8n workflow is now upgraded to:
- **Schedule:** 8 AM, 1 PM, and 6 PM.
- **Notion Sync:** Any idea you move to "Generate" in Notion will be drafted *immediately*.

---

## 🛠️ How to Manage the OS

### In Notion:
- **Idea Stage:** The Researcher adds ideas here.
- **Generate Stage:** Move an idea to "Generate" to trigger a draft.
- **Draft Review:** The draft content will automatically sync back to the Notion page for your final polish.

### In Slack:
- **#content-review:** Approve or reject daily posts.
- **#newsletter-drafts:** Review and copy your bilingual weekly editions.

### On your Server:
- Ensure `python api_wrapper.py` is running.
- The `SyncService` handles all the "heavy lifting" between Notion, Supabase, and local JSONs.

---

## 🚦 Final Steps
1. **Update .env:** Ensure `NOTION_TOPICS_DB_ID` and other database IDs are filled.
2. **Import n8n:** Import [icos_workflow.json](file:///c:/Users/Dell/OneDrive%20-%20Ankar%20Group%20SA%20de%20CV%20%281%29/@%20Content%20Agents/icos_workflow.json) and [newsletter_workflow.json](file:///c:/Users/Dell/OneDrive%20-%20Ankar%20Group%20SA%20de%20CV%20%281%29/@%20Content%20Agents/newsletter_workflow.json) into your n8n instance.
3. **Activate:** Set the workflows to "Active".

Enjoy your autonomous personal brand engine!
