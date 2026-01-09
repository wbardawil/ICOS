"""
ICOS Visualist Agent - Gemini/Imagen Edition
Uses Google's Gemini for concept generation and Imagen for image creation.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))

BRAND_STAMP = "Include a small 'WB' monogram stamp in the bottom right corner as a subtle watermark."

VISUAL_STYLES = """
## MATT GRAY STYLES
1. **Napkin Sketch** - Hand-drawn on white napkin, black pen, thick lines
2. **Notebook Page** - Open Moleskine with handwritten notes, pen beside
3. **Whiteboard** - Marker drawings, boxes and arrows

## CHRIS DONNELLY STYLES
4. **3D Floating Objects** - Clean 3D renders on gradient background
5. **Data Hero Card** - Bold statistic, modern typography
6. **Icon Grid** - 4-6 icons in clean grid layout

## DAN MARTELL STYLES
7. **Playbook Framework** - "THE [X] PLAYBOOK", numbered steps
8. **ROI Calculator** - Before/after numbers, $X → $Y format
9. **Quote + Headshot** - Powerful quote, clean background

## UNIVERSAL
10. **Comparison Table** - Old Way vs New Way
11. **Pyramid** - 3-5 tier hierarchy
12. **Timeline** - Horizontal progression
"""


def generate_visual_concept(topic: str, post_content: str, style_preference: str = None) -> dict:
    """Generate a visual concept using Gemini."""
    
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    style_hint = f"\nPreferred style: {style_preference}" if style_preference else ""
    
    prompt = f"""You are a visual content designer. Given this topic and post, create a visual concept.

{VISUAL_STYLES}

## Topic
{topic}

## Post Content
{post_content}
{style_hint}

## BRANDING
All images must include: WB monogram stamp in bottom right corner.

Return ONLY valid JSON:
{{
    "visual_type": "napkin_sketch | notebook_page | 3d_objects | data_card | playbook | etc",
    "style_reference": "Matt Gray | Chris Donnelly | Dan Martell",
    "description": "What the image shows",
    "elements": ["list", "of", "elements"],
    "text_on_image": "Text to include",
    "imagen_prompt": "Detailed prompt for Google Imagen API with WB branding"
}}"""

    response = model.generate_content(prompt)
    
    try:
        # Clean response and parse JSON
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except:
        return {"error": "Failed to parse", "raw": response.text}


def generate_image_with_imagen(prompt: str) -> str:
    """
    Generate image using Google Imagen.
    Note: Requires Vertex AI setup for production use.
    """
    # Add branding if not present
    if "WB" not in prompt:
        prompt += " " + BRAND_STAMP
    
    # For now, return the prompt - actual Imagen API requires Vertex AI
    return {
        "status": "prompt_ready",
        "prompt": prompt,
        "note": "Use this prompt with Vertex AI Imagen or Google AI Studio"
    }


def create_visual_for_post(topic: str, post_content: str, style: str = None) -> dict:
    """Full pipeline: generate concept."""
    concept = generate_visual_concept(topic, post_content, style)
    
    if "imagen_prompt" in concept:
        concept["imagen_ready"] = generate_image_with_imagen(concept["imagen_prompt"])
    
    return concept


if __name__ == "__main__":
    import sys
    
    print("ICOS Visualist Agent (Gemini Edition)")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("Usage: python visualist_agent.py <topic> [--style matt|chris|dan]")
        sys.exit(0)
    
    topic = sys.argv[1]
    style = None
    
    if "--style" in sys.argv:
        idx = sys.argv.index("--style") + 1
        if idx < len(sys.argv):
            styles = {
                "matt": "Matt Gray - napkin sketch or notebook",
                "chris": "Chris Donnelly - 3D objects or data card",
                "dan": "Dan Martell - playbook or ROI calculator"
            }
            style = styles.get(sys.argv[idx].lower())
    
    sample = "Your processes are either making money or costing money."
    result = create_visual_for_post(topic, sample, style)
    print(json.dumps(result, indent=2))
