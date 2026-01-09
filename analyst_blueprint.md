# Analyst Agent Blueprint (The "Reflect" Loop)

This agent acts as the objective auditor, closing the feedback loop 24 hours after publication.

## 1. Logic: The Virality Score
We normalize performance data to a single score to determine "Winners" vs "Noise".

**Formula:**
`Score = (Likes * 1) + (Comments * 2) + (Shares * 3) / (Impressions / 1000)`

*   **Benchmark:** >20 is Average. >50 is Viral.
*   **Action:** If Score > 80, tag as "🏆 Evergreen".

---

## 2. Make.com Workflow

### Trigger: Database Watcher
*   **Module:** Notion/Airtable - Search Records.
*   **Filter:** `Status` = "Published" AND `Published Date` is 24-25 hours ago AND `Analysed` != True.

### Step 1: Sense (Data Retrieval)
*   **Module:** Apify - Run Actor (`linkedin-post-scraper`).
*   **Input:** Post URL.
*   **Output:** `likeCount`, `commentCount`, `repostCount`, `impressionCount`.

### Step 2: Reasoning (The "Content Auditor")
*   **Module:** OpenAI - Create Completion (`gpt-4o`).
*   **System Prompt:**
    ```markdown
    ### ROLE
    You are the Lead Data Analyst for a personal brand. You review content performance with brutal honesty.

    ### INPUT DATA
    - **Post Text:** {{Post_Content}}
    - **Virality Score:** {{Virality_Score}} (Benchmark: Average is 20. Viral is 50+).
    - **Engagement:** {{Comments}} comments, {{Likes}} likes.

    ### MISSION
    Analyze WHY this post performed the way it did. Do not just summarize the numbers.

    ### ANALYSIS PROTOCOL
    1. **The Hook Audit:** Did the first sentence stop the scroll? Why/Why not?
    2. **The Formatting:** Was the "whitespace" effective, or did it look like a wall of text?
    3. **The Topic:** Is this topic resonating with the audience based on the comment volume?

    ### OUTPUT FORMAT (JSON ONLY)
    {
      "verdict": "FLOP" | "AVERAGE" | "WINNER",
      "primary_reason": "One sentence explaining the main driver of this result.",
      "improvement_tip": "One specific action to take next time (e.g., 'Hook was too vague', 'Call to Action was weak').",
      "repurpose_recommendation": "Should we turn this into a newsletter? (Yes/No)"
    }
    ```

### Step 3: Memory (Database Update)
*   **Module:** Notion - Update Item.
*   **Map Fields:**
    *   `Likes`: {{likeCount}}
    *   `Virality Score`: {{Calculated_Score}}
    *   `AI Analysis`: {{GPT_Output.primary_reason}} | {{GPT_Output.improvement_tip}}
    *   `Analyzed`: Yes
    *   *(Logic)*: If `verdict` == "WINNER", add tag "🏆 Evergreen".

---

## 3. The Flywheel Effect
*   **Feedback Injection:** The "Improvement Tip" from the last 5 analyzed posts is fed back into the **Ghostwriter Agent's** prompt context to prevent repeating mistakes.
