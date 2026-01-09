# ICOS 2.0: Data Architecture & Notion Schema

The Infinity Content OS uses a "Hybrid Storage" model. **Notion** is your Strategic Command Center (where you interact), while **Supabase** is the Intelligence Engine (where the AI learns).

---

## 1. Required Notion Databases

To make the code work, you need to create three databases in Notion and share them with your internal integration.

### 📊 Database: `Content Ideas`
*This is where the Researcher adds ideas and you trigger drafts.*

| Property Name | Property Type | Description |
| :--- | :--- | :--- |
| **Name** | Title | The core topic or hook idea. |
| **Status** | Select | Options: `Idea`, `Generate`, `Drafted`, `Scheduled`, `Published`. |
| **Draft** | Text / Rich Text | Where the Ghostwriter writes the post. |
| **Visual Concept** | Text / Rich Text | The image description and Imagen prompt. |
| **Platform** | Select | Options: `LinkedIn`, `Newsletter`. |
| **Scheduled Date** | Date | When the post is intended to go live. |

### 🎯 Database: `Topics`
*Synced to Supabase for RAG weighting.*

| Property Name | Property Type | Description |
| :--- | :--- | :--- |
| **Name** | Title | e.g., "SaaS Systems", "Fractional Leadership". |
| **Description** | Text | Context for the AI. |
| **Is Active** | Checkbox | Toggle to pause certain content pillars. |

### 🎨 Database: `Styles`
*Synced to Supabase to define writing tones.*

| Property Name | Property Type | Description |
| :--- | :--- | :--- |
| **Name** | Title | e.g., "Justin Welsh", "Contrarian", "Matt Gray". |
| **Instruction** | Text | The specific rules for the AI (skimmability, whitespace, etc.). |
| **Is Active** | Checkbox | Toggle to swap writing styles in/out. |

---

## 2. Data Storage Hierarchy

| Data Type | Primary Source (Read/Write) | Long-term Archive | Purpose |
| :--- | :--- | :--- | :--- |
| **Content Strategy** | Notion | Supabase (`topics`, `styles`) | Human editing + AI retrieval. |
| **Draft Posts** | Notion (`Draft`) | Supabase (`content_library`) | Real-time review + historical analysis. |
| **Visual Concepts** | Notion | Supabase (`content_library`) | Instructions for Imagen. |
| **Performance Metrics** | Buffer / LinkedIn | Supabase (`content_library`) | Calculating virality scores. |
| **Branding Data** | Notion (`Branding` Page) | `user_profile.json` | High-fidelity voice identity. |

---

## 3. The Lifecycle Flow

1.  **Ideation**: `researcher_agent.py` adds a row to **Content Ideas** (Status: `Idea`).
2.  **Trigger**: You move the status to `Generate`.
3.  **Generation**: n8n triggers the Ghostwriter → Writes to Notion `Draft` property.
4.  **Audit**: After 7 days, the `analyst_agent.py` fetches the post metrics from LinkedIn, calculates the **Virality Score**, and stores it permanently in **Supabase**.
5.  **Refinement**: The next time you generate a post on that topic, the Ghostwriter pulls the performance "Winners" and "Improvement Tips" from **Supabase** using RAG.
