"""
ICOS Ghostwriter Agent - Claude Edition
Uses Anthropic Claude for content generation.
"""

import os
import anthropic
from rag_core import build_rag_context
from strategy_manager import get_weighted_combo, schedule_content
from datetime import date
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

GHOSTWRITER_SYSTEM_PROMPT = """### ROLE & IDENTITY
You are the Ghostwriter Agent for Wadi Bardawil, a Fractional CSTO. Your writing style is heavily inspired by Justin Welsh's content systems. You write with extreme clarity, high "skim-ability," and zero fluff.

### WRITING PRINCIPLES (JUSTIN WELSH STYLE)
1. **The 1-2-1 Rhythm:**
   - 1 short sentence.
   - 2-3 line breakdown.
   - 1 punchy conclusion.
   - Use whitespace aggressively. No paragraph should exceed 2 lines.

2. **Hook Structures:**
   - "Outcome-based": I did X in Y time. Here is how.
   - "Contrarian": Most people believe X. Here is why they are wrong.
   - "The Gap": You want X but you're doing Y.
   - Move fast to the value. No "I hope this finds you well."

3. **Bucket Brigades:**
   - Use short, bridging phrases to maintain momentum:
     "Here's the truth:"
     "The problem?"
     "And it's costing you."
     "Here is my system:"

4. **Actionable Systems:**
   - Don't give advice. Give systems.
   - Use numbered lists (1, 2, 3) or bullet points (→) for steps.
   - Everything must be "save-able" and "re-usable".

5. **Tone & Voice:**
   - Reading Level: Grade 6.
   - Authoritative but accessible.
   - Use bolding for emphasis on key results or "must-read" lines.

### CONTENT STRUCTURE (VSL FRAMEWORK)
1. **Hook:** Strong opening that stops the scroll.
2. **The Reframe:** Challenge the status quo.
3. **The System:** 3-5 specific, actionable steps.
4. **The Proof:** A brief sentence on the result (numbers preferred).
5. **The Punchline:** One bolded sentence that sticks.
6. **The CTA:** Simple, clear next step.
"""


def generate_post(topic: str, style_instruction: str = None, platform: str = "linkedin") -> str:
    """Generate a post using Claude."""
    
    rag_context = build_rag_context(topic)
    
    # Priority: Latest Analyst Feedback
    impact_feedback = ""
    if "improvement_tip" in rag_context:
        impact_feedback = f"\n## CRITICAL IMPACT FEEDBACK (From Past Performance)\n{rag_context}\n"

    style_block = ""
    if style_instruction:
        style_block = f"\n## Style Instruction\n{style_instruction}"
    
    user_message = f"""## Topic
{topic}

## Platform
{platform}
{style_block}
{impact_feedback}

---
Draft the content following the VSL framework. 
IMPORTANT: Integrate the 'CRITICAL IMPACT FEEDBACK' above to ensure this post outperforms previous ones.
Output ONLY the post text."""

    message = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        system=GHOSTWRITER_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    return message.content[0].text


def generate_with_auto_combo(platform: str = "linkedin") -> dict:
    """Generate a post using an auto-selected topic/style combo weighted by performance."""
    
    combo = get_weighted_combo()
    if not combo:
        return {"error": "No unused topic/style combinations available!"}
    
    content = generate_post(
        topic=combo["topic_name"],
        style_instruction=combo["style_instruction"],
        platform=platform
    )
    
    schedule_content(
        topic_id=combo["topic_id"],
        style_id=combo["style_id"],
        scheduled_date=str(date.today())
    )
    
    return {
        "topic": combo["topic_name"],
        "style": combo["style_name"],
        "content": content
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        result = generate_with_auto_combo()
        print(f"Topic: {result.get('topic')}")
        print(f"Style: {result.get('style')}")
        print(f"\n{result.get('content')}")
    else:
        topic = sys.argv[1] if len(sys.argv) > 1 else "Why systems beat goals"
        print(generate_post(topic))
