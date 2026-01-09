# n8n Workflow Blueprint for ICOS

## Webhook Setup (The "Trigger")

To trigger your content system from an external source (like a button in Notion or a simple URL), follow these steps:

1.  **Add a "Webhook" Node** in n8n.
2.  **HTTP Method:** Set to `POST`.
3.  **Path:** Set to `run-icos` (or anything you like).
4.  **URL Types:**
    *   **Test URL:** Use this while building. It only stays active while the n8n editor is open.
    *   **Production URL:** Use this for the final setup. You must **Activate** the workflow for this to work.
5.  **Exposing Localhost:** If you are running n8n and the agents on your local machine, use **ngrok** to get a public URL:
    ```bash
    ngrok http 8000
    ```
    Then use the ngrok URL in your n8n configuration.

---

## Workflow 1: Daily Content Generation

### Trigger
- **Type:** Schedule Trigger
- **Cron:** `0 6 * * *` (Daily at 6 AM)

### Nodes

```
[Schedule] → [HTTP: Sync Profile] → [HTTP: Get Topic] → [Claude: Draft] → [Gemini: Visual] → [Slack: Review]
```

#### Node 1: Schedule Trigger
- Type: `Schedule Trigger`
- Expression: `0 6 * * *`

#### Node 2: HTTP Request - Sync Profile
- Type: `HTTP Request`
- Method: `POST`
- URL: `http://localhost:5000/sync-profile` (or your server)
- Body: `{}`

#### Node 3: HTTP Request - Get Next Topic
- Type: `HTTP Request`
- Method: `GET`
- URL: `http://localhost:5000/next-combo`
- Output: `{{ $json.topic_name }}`, `{{ $json.style_instruction }}`

#### Node 4: Anthropic Claude
- Type: `Anthropic` (or HTTP to API)
- Model: `claude-sonnet-4-20250514`
- System Prompt: (use ghostwriter system prompt)
- User Message: 
```
Topic: {{ $node["Get Topic"].json.topic_name }}
Style: {{ $node["Get Topic"].json.style_instruction }}
Draft a LinkedIn post following the VSL framework.
```

#### Node 5: Google Gemini (Visual Concept)
- Type: `HTTP Request` (to Gemini API) or `Google AI`
- Model: `gemini-2.0-flash`
- Prompt:
```
Create a visual concept for this post:
{{ $node["Claude"].json.content }}

Return JSON with: visual_type, description, imagen_prompt
Include WB branding.
```

#### Node 6: Slack
- Type: `Slack`
- Channel: `#content-review`
- Message:
```
🆕 New Content Draft

*Topic:* {{ $node["Get Topic"].json.topic_name }}
*Style:* {{ $node["Get Topic"].json.style_name }}

*Post:*
{{ $node["Claude"].json.content }}

*Visual Concept:*
{{ $node["Gemini"].json.description }}

*Imagen Prompt:*
{{ $node["Gemini"].json.imagen_prompt }}
```
- Interactive: Add "Approve" and "Reject" buttons

---

## Workflow 2: Publish on Approval

### Trigger
- **Type:** Slack Trigger (Button Click)
- **Event:** `button_action`

### Nodes

```
[Slack Trigger] → [IF: Approved?] → [Buffer/LinkedIn: Post] → [Supabase: Log]
```

#### Node 1: Slack Trigger
- Type: `Slack Trigger`
- Event: `Interactive Message`

#### Node 2: IF
- Condition: `{{ $json.actions[0].value }} === "approve"`

#### Node 3: Buffer (or LinkedIn API)
- Type: `HTTP Request`
- Method: `POST`
- URL: `https://api.bufferapp.com/1/updates/create.json`
- Body: Post content from previous workflow (stored in Supabase or passed via Slack)

#### Node 4: Supabase - Log Published
- Type: `Supabase`
- Operation: `Insert`
- Table: `content_library`
- Data: Topic, Style, Content, Published Date

---

## Workflow 3: Analyst Feedback (24h Later)

### Trigger
- **Type:** Schedule Trigger
- **Cron:** `0 10 * * *` (Daily at 10 AM, checks yesterday's posts)

### Nodes

```
[Schedule] → [Supabase: Get Yesterday's Posts] → [LinkedIn: Get Metrics] → [Claude: Analyze] → [Supabase: Update]
```

#### Node 1: Supabase - Get Posts
- Operation: `Select`
- Table: `content_library`
- Filter: `published_at = yesterday AND virality_score IS NULL`

#### Node 2: HTTP - LinkedIn Metrics
- Use Apify LinkedIn Scraper or official API
- Get: Impressions, Likes, Comments, Shares

#### Node 3: Claude - Analyze
- System: "You are a content analyst. Score this post and provide feedback."
- Calculate: Virality Score = `(Likes*1 + Comments*2 + Shares*3) / (Impressions/1000)`
- Output: Verdict (FLOP/AVERAGE/WINNER), Improvement Tip

#### Node 4: Supabase - Update
- Operation: `Update`
- Table: `content_library`
- Set: `virality_score`, `verdict`, `improvement_tip`

---

## n8n Setup Instructions

1. **Install n8n:**
   ```bash
   npm install n8n -g
   n8n start
   ```

2. **Or use Docker:**
   ```bash
   docker run -it --rm -p 5678:5678 n8nio/n8n
   ```

3. **Access:** http://localhost:5678

4. **Import Workflow:** Copy nodes above or create manually

5. **Set Credentials:**
   - Anthropic API Key
   - Google AI API Key
   - Slack OAuth Token
   - Supabase URL + Key

---

## Environment Variables for n8n

```
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=...
SLACK_TOKEN=xoxb-...
```
