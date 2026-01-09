# Make.com Blueprint: Infinity Content OS (ICOS)

This blueprint orchestrates the flow from raw idea to scheduled content.

## Prerequisites
*   **Notion**: A database named "Content Ideas" with properties: `Name` (Title), `Status` (Select: Idea, Drafted, Scheduled), `Platform` (Select: LinkedIn, Twitter).
*   **OpenAI**: API Key with access to GPT-4o.
*   **Slack**: A channel named `#content-approval`.
*   **Buffer/Taplio**: API access for scheduling.

## Scenario Workflow

### Trigger: Notion - Watch Database Items
*   **Connection**: Your Notion Account.
*   **Database ID**: [Select 'Content Ideas' DB].
*   **Trigger Condition**: Watch for new items where `Status` = "Idea".

### Step 1: OpenAI - Create a Completion (Ghostwriter Agent)
*   **Model**: `gpt-4o`.
*   **System Message**: [Paste contents of `ghostwriter_prompt.md` here].
*   **User Message**: 
    > Topic: {{1.properties.Name.title[].plain_text}}
    > Platform: {{1.properties.Platform.select.name}}
    > 
    > Draft the content now.

### Step 2: Tools - Set Variable (Formatting)
*   **Variable Name**: `draft_content`.
*   **Value**: {{2.choices[].message.content}}.

### Step 3: Slack - Create a Message (Human Loop)
*   **Channel**: `#content-approval`.
*   **Text**: 
    > *New Draft Ready for Review*
    > **Topic**: {{1.properties.Name.title[].plain_text}}
    > **Draft**:
    > ```
    > {{draft_content}}
    > ```
*   **Buttons (Block Kit)**:
    *   [Approve] (Value: `approve_{{1.id}}`)
    *   [Reject/Refine] (Value: `reject_{{1.id}}`)

### Step 4: Notion - Update Database Item
*   **Database Item ID**: {{1.id}}.
*   **Fields**:
    *   `Status`: "Drafted"
    *   `Draft Body`: {{draft_content}}

---

## Branch: Approval Handling (Separate Scenario)
*This second scenario listens for the Slack button click.*

### Trigger: Slack - New Interactive Event
*   **Connection**: Your Slack App.

### Router
*   **Route 1 (Approve)**: 
    *   **Filter**: `payload.actions[].value` contains "approve".
    *   **Action (Buffer/Taplio)**: Create Update.
        *   **Text**: {{fetch_from_notion.draft_body}}.
        *   **Profile**: [Your LinkedIn Profile].
    *   **Action (Notion)**: Update Status to "Scheduled".
    *   **Action (Slack)**: Reply "✅ Content scheduled!"

*   **Route 2 (Reject)**:
    *   **Filter**: `payload.actions[].value` contains "reject".
    *   **Action (Notion)**: Update Status to "Needs Refinement".
    *   **Action (Slack)**: Reply "❌ Sent back to Notion for manual review."
