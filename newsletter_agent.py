"""
ICOS Bilingual Newsletter Agent
Synthesizes weekly content and drafts newsletters in English and Spanish.
"""

import os
import json
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class NewsletterAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.voice_profile = "Justin Welsh style: Clear, minimalist, actionable, VSL-driven."

    def generate_newsletter(self, weekly_posts: list[dict], language: str = "english") -> str:
        """Drafts a newsletter based on a summary of weekly posts."""
        posts_context = "\n".join([f"- Topic: {p['topic']}\n  Content: {p['content']}" for p in weekly_posts])
        
        system_prompt = f"""You are a High-Performance Newsletter Ghostwriter for Wadi Bardawil.
Your goal is to synthesize the week's best content into a cohesive, high-impact weekly newsletter.

Voice Profile: {self.voice_profile}
Target Language: {language}

Structure:
1. Hook: A punchy opening that validates a common pain point.
2. The Core Philosophy: Explain the 'Why'.
3. The 'How-To': 3-5 actionable steps.
4. The CTA: Encourage joining a specific program or booking a call.

Rules:
- If language is Spanish, ensure the tone is professional but aggressive (Matt Gray style).
- No fluff. Use whitespace for readability.
"""

        user_message = f"""Here are the top posts from this week:
{posts_context}

Draft a 500-word newsletter deep-dive based on these themes. Output ONLY the newsletter text."""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        return response.content[0].text

    def create_bilingual_edition(self, weekly_posts: list[dict]):
        """Generates both English and Spanish versions."""
        print(f"[{datetime.now()}] Generating Bilingual Newsletter...")
        
        english_ver = self.generate_newsletter(weekly_posts, "english")
        spanish_ver = self.generate_newsletter(weekly_posts, "spanish")
        
        return {
            "english": english_ver,
            "spanish": spanish_ver,
            "generated_at": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Mock data for testing
    mock_posts = [
        {"topic": "The Delegation Paradox", "content": "Hiring is a trap if you don't have systems..."},
        {"topic": "Deep Work", "content": "Focus is the only leverage that matters in 2026..."}
    ]
    agent = NewsletterAgent()
    edition = agent.create_bilingual_edition(mock_posts)
    print("--- ENGLISH ---")
    print(edition["english"][:200] + "...")
    print("\n--- SPANISH ---")
    print(edition["spanish"][:200] + "...")
