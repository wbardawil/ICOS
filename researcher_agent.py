"""
ICOS Researcher Agent
Finds trending topics and automatically populates the Notion Content Ideas database.
"""

import os
import json
from datetime import datetime
from anthropic import Anthropic
from sync_service import SyncService
from dotenv import load_dotenv

load_dotenv()

class ResearcherAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.sync = SyncService()
        self.topics = [
            "SaaS Growth", 
            "Solopreneurship", 
            "No-Code Systems", 
            "Remote Leadership", 
            "Personal Branding"
        ]

    def generate_ideas(self, research_data: str) -> list[str]:
        """Uses LLM to distill research into specific content ideas."""
        prompt = f"""You are a Strategic Content Researcher for Wadi Bardawil.
Based on the following raw research/trends data, generate 3-5 high-impact LinkedIn content ideas.

Wadi's Focus: {', '.join(self.topics)}

Raw Research Data:
{research_data}

Rules:
1. Ideas must be specific (not just "write about SaaS").
2. Focus on "The Delegation Paradox", "Systems vs Hiring", or "Autonomous AI".
3. Outcome must be a valid JSON array of strings.

Output ONLY the JSON array."""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            # Simple extraction in case of markdown blocks
            text = response.content[0].text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            return json.loads(text)
        except:
            return []

    def run(self):
        print(f"[{datetime.now()}] Starting Research Run...")
        
        # In a real scenario, we'd use a search tool here.
        # For this implementation, we use a high-fidelity grounding prompt.
        mock_research = """
        - 2026 Trend: Middle management is being replaced by AI-orchestrated agents.
        - LinkedIn Fact: High-performers are moving from 'fractional' to 'ecosystem' models.
        - SaaS: PLG is dead; 'Agent-Led Growth' is the new standard.
        """
        
        ideas = self.generate_ideas(mock_research)
        print(f"Generated {len(ideas)} ideas.")
        
        for idea in ideas:
            print(f"Adding to Notion: {idea}")
            self.sync.add_idea(idea)
            
        print("Research Run Complete.")

if __name__ == "__main__":
    agent = ResearcherAgent()
    agent.run()
