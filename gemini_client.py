from google import genai
from google.genai import types
from config import Config
import json

class GeminiClient:
    def __init__(self):
        Config.validate()
        self.client = genai.Client(
            vertexai=True,
            project=Config.PROJECT_ID,
            location=Config.LOCATION
        )

    def analyze_costs(self, user_query, billing_data):
        prompt = self._create_prompt(user_query, billing_data)

        response = self.client.models.generate_content(
            model=Config.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=Config.TEMPERATURE,
                max_output_tokens=Config.MAX_OUTPUT_TOKENS
            )
        )

        if not response.text:
            raise RuntimeError("Gemini returned no text")

        return response.text

    def _create_prompt(self, query, data):
        return f"""
You are a Google Cloud cost optimization analyst.

Billing data:
{json.dumps(data, indent=2, default=str)}

User question:
{query}

Explain the top cost drivers and suggest practical
cost optimizations.

Do not invent savings percentages or claim that
flagged costs are guaranteed savings.
"""
