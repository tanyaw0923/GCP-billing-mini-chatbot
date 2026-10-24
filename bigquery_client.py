from google.cloud import bigquery
from config import Config
from typing import List, Dict

class BigQueryClient:
    """Handle all BigQuery operations."""

    def __init__(self):
        """Initialize BigQuery client."""
        self.client = bigquery.Client(project=Config.PROJECT_ID)
        self.table_id = Config.get_table_id()

    def get_cost_summary(self) -> List[Dict]:
        """Get overall cost summary."""
        query = f"""
        SELECT
            service_description,
            project_id,
            SUM(cost) AS total_cost,
            SUM(credits_amount) AS total_credits,
            COUNT(*) AS line_items
        FROM {self.table_id}
        GROUP BY service_description, project_id
        ORDER BY total_cost DESC
        LIMIT 20
        """
        return self._execute_query(query)

    def get_top_cost_drivers(self, limit: int = 10) -> List[Dict]:
        """Get top cost drivers."""
        query = f"""
        SELECT
            service_description,
            sku_description,
            location_region,
            SUM(cost) AS total_cost,
            COUNT(*) AS usage_count
        FROM {self.table_id}
        GROUP BY service_description, sku_description, location_region
        ORDER BY total_cost DESC
        LIMIT {limit}
        """
        return self._execute_query(query)

    def get_project_breakdown(self) -> List[Dict]:
        """Get cost by project."""
        query = f"""
        SELECT
            project_id,
            project_name,
            SUM(cost) AS total_cost,
            COUNT(DISTINCT service_description) AS services_count
        FROM {self.table_id}
        GROUP BY project_id, project_name
        ORDER BY total_cost DESC
        """
        return self._execute_query(query)

    def get_regional_costs(self) -> List[Dict]:
        """Get costs by region."""
        query = f"""
        SELECT
            location_region,
            SUM(cost) AS total_cost,
            COUNT(*) AS items
        FROM {self.table_id}
        WHERE location_region IS NOT NULL
        GROUP BY location_region
        ORDER BY total_cost DESC
        """
        return self._execute_query(query)

    def get_waste_analysis(self) -> List[Dict]:
        """Identify potential waste."""
        query = f"""
        SELECT
            'Dev After Hours' AS waste_type,
            COUNT(*) AS occurrences,
            SUM(cost) AS potential_savings
        FROM {self.table_id}
        WHERE project_id LIKE '%dev%'
          AND EXTRACT(HOUR FROM usage_start_time) NOT BETWEEN 9 AND 18

        UNION ALL

        SELECT
            'High-Cost Non-Prod' AS waste_type,
            COUNT(*) AS occurrences,
            SUM(cost) AS potential_savings
        FROM {self.table_id}
        WHERE project_id IN ('dev-environment', 'staging-test')
          AND cost > 100
        """
        return self._execute_query(query)

    def get_total_cost(self) -> float:
        """Get total cost."""
        query = f"SELECT SUM(cost) AS total FROM {self.table_id}"
        result = self._execute_query(query)
        return float(result[0]["total"]) if result else 0.0

    def _execute_query(self, query: str, job_config=None) -> List[Dict]:
        """Execute query and return results."""
        try:
            results = self.client.query(query, job_config=job_config).result()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Query error: {e}")
            return []

    def get_all_billing_data(self) -> Dict:
        """Get all data for analysis."""
        return {
            "summary": self.get_cost_summary(),
            "top_drivers": self.get_top_cost_drivers(),
            "projects": self.get_project_breakdown(),
            "regions": self.get_regional_costs(),
            "waste": self.get_waste_analysis(),
            "total_cost": self.get_total_cost()
        }

if __name__ == "__main__":
    Config.validate()
    client = BigQueryClient()
    total = client.get_total_cost()
    print(f"Total Cost: ${total:,.2f}")
    print("BigQuery client working!")
