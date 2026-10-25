from bigquery_client import BigQueryClient
from gemini_client import GeminiClient
from config import Config
from typing import Dict

class CostOptimizerChatbot:
    """GCP Cost Optimization Chatbot."""

    def __init__(self):
        """Initialize chatbot."""
        Config.validate()
        self.bq_client = BigQueryClient()
        self.gemini_client = GeminiClient()

    def process_query(self, user_query: str) -> Dict:
        """Process user query."""
        print("\\nFetching billing data...")
        billing_data = self.bq_client.get_all_billing_data()

        if not billing_data.get("summary"):
            return {
                "status": "error",
                "message": "No billing data found in BigQuery"
            }

        print("Analyzing with Gemini AI...")
        ai_response = self.gemini_client.analyze_costs(user_query, billing_data)
        total_cost = billing_data.get("total_cost", 0)

        return {
            "status": "success",
            "query": user_query,
            "analysis": ai_response,
            "metadata": {
                "total_cost": total_cost,
                "total_projects": len(billing_data.get("projects", [])),
                "total_services": len(
                    {
                        item["service_description"]
                        for item in billing_data.get("summary", [])
                    }
                )
            },
            "top_services": [
                {
                    "service": item["service_description"],
                    "cost": float(item["total_cost"]),
                    "location": item.get("location_region", "N/A")
                }
                for item in billing_data.get("top_drivers", [])[:5]
            ],
            "projects": [
                {
                    "project": item["project_id"],
                    "cost": float(item["total_cost"])
                }
                for item in billing_data.get("projects", [])
            ]
        }

if __name__ == "__main__":
    print("\nTesting Chatbot...\n")
    chatbot = CostOptimizerChatbot()
    result = chatbot.process_query("What are my top cost drivers?")

    if result["status"] == "success":
        print(f"Total: ${result['metadata']['total_cost']:,.2f}")
        print(f"Projects: {result['metadata']['total_projects']}")
        print("\n" + result["analysis"][:300] + "...")
        print("\nChatbot working!")
    else:
        print(result["message"])
