import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from config import Config
import json
from typing import Dict

class GeminiClient:
    """Handle Gemini AI interactions."""

    def __init__(self):
        """Initialize Gemini."""
        Config.validate()
        vertexai.init(project=Config.PROJECT_ID, location=Config.LOCATION)
        self.model = GenerativeModel(Config.GEMINI_MODEL)

    def analyze_costs(self, user_query: str, billing_data: Dict) -> str:
        """Analyze billing data with AI."""
        prompt = self._create_prompt(user_query, billing_data)

        config = GenerationConfig(
            temperature=Config.TEMPERATURE,
            max_output_tokens=Config.MAX_OUTPUT_TOKENS
        )

        try:
            response = self.model.generate_content(prompt, generation_config=config)
            return response.text
        except Exception as e:
            return f"AI Error: {str(e)}"

    def _create_prompt(self, query: str, data: Dict) -> str:
        """Create analysis prompt."""
        total = data.get("total_cost", 0)
        top = data.get("top_drivers", [])[:5]
        projects = data.get("projects", [])
        waste = data.get("waste", [])

        return f"""You are a GCP cost optimization expert. Analyze this billing data.

**BILLING DATA:**

Total Cost: ${total:,.2f}
Projects: {len(projects)}

Top Cost Drivers:
{json.dumps(top, indent=2, default=str)}

Projects:
{json.dumps(projects, indent=2, default=str)}

Waste Analysis:
{json.dumps(waste, indent=2, default=str)}

**USER QUERY:** {query}

**PROVIDE:**

## Cost Summary
Brief overview

## Top Cost Drivers
List top 3-5 items

## Optimization Recommendations
### High Impact (>15% savings)
### Medium Impact (5-15% savings)
### Quick Wins

## GCP Features to Use
- Committed Use Discounts
- Preemptible VMs
- Storage optimization
- Resource scheduling

## Estimated Savings
Calculate potential monthly savings

## Action Items
Numbered next steps

Use markdown formatting.
"""

if __name__ == "__main__":
    Config.validate()
    client = GeminiClient()
    test_data = {
        "total_cost": 3000,
        "top_drivers": [],
        "projects": [],
        "waste": []
    }
    result = client.analyze_costs("Test query", test_data)
    print(result[:200])
    print("Gemini client working!")
