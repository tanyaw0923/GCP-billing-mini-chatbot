import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""

    PROJECT_ID = os.getenv("PROJECT_ID")
    LOCATION = os.getenv("LOCATION", "global")
    BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "billing_analysis")
    BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE", "gcp_cost_data")

    GEMINI_MODEL = "gemini-3.5-flash"
    TEMPERATURE = 0.2
    MAX_OUTPUT_TOKENS = 2048

    @classmethod
    def get_table_id(cls):
        """Get fully qualified BigQuery table ID."""
        return f"`{cls.PROJECT_ID}.{cls.BIGQUERY_DATASET}.{cls.BIGQUERY_TABLE}`"

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.PROJECT_ID:
            raise ValueError("PROJECT_ID not set")
        return True

if __name__ == "__main__":
    Config.validate()
    print("Configuration validated")
    print(f"Project: {Config.PROJECT_ID}")
    print(f"Table: {Config.get_table_id()}")
