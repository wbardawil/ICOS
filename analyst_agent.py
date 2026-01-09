"""
ICOS Analyst Agent - Feedback Loop
Scores content and stores learnings back into the RAG system.
"""

from openai import OpenAI
from rag_core import ingest_content, ContentRecord
import os
import json
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

ANALYST_SYSTEM_PROMPT = """### ROLE
You are the Lead Data Analyst for a personal brand. You review content performance with brutal honesty.

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
  "improvement_tip": "One specific action to take next time.",
  "repurpose_recommendation": "Yes" | "No"
}
"""


def calculate_virality_score(likes: int, comments: int, shares: int, impressions: int) -> float:
    """Calculate normalized virality score."""
    if impressions == 0:
        return 0.0
    weighted = (likes * 1) + (comments * 2) + (shares * 3)
    return round(weighted / (impressions / 1000), 2)


def analyze_and_store(
    content: str,
    topic: str,
    style: str,
    likes: int,
    comments: int,
    shares: int,
    impressions: int,
    platform: str = "linkedin"
) -> dict:
    """Analyze content performance and store in RAG system."""
    
    # Calculate score
    score = calculate_virality_score(likes, comments, shares, impressions)
    
    # Get AI analysis
    user_message = f"""## Post Text
{content}

## Metrics
- Impressions: {impressions}
- Likes: {likes}
- Comments: {comments}
- Shares: {shares}
- Virality Score: {score} (Benchmark: 20 = Average, 50+ = Viral)

Analyze this post now."""

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ANALYST_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    # Parse JSON response
    try:
        analysis = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        analysis = {
            "verdict": "AVERAGE",
            "primary_reason": "Could not parse analysis.",
            "improvement_tip": "Review manually.",
            "repurpose_recommendation": "No"
        }
    
    # Store in RAG
    record = ContentRecord(
        content=content,
        topic=topic,
        style=style,
        platform=platform,
        virality_score=score,
        verdict=analysis["verdict"],
        improvement_tip=analysis["improvement_tip"]
    )
    
    stored = ingest_content(record)
    
    return {
        "score": score,
        "analysis": analysis,
        "stored_id": stored.get("id")
    }


# CLI for testing
if __name__ == "__main__":
    result = analyze_and_store(
        content="Test post about systems thinking.",
        topic="Systems",
        style="Contrarian",
        likes=85,
        comments=22,
        shares=5,
        impressions=4500
    )
    print(json.dumps(result, indent=2))
