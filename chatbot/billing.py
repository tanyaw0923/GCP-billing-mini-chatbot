"""Read-only analysis of Google Cloud's standard BigQuery billing export."""
from google.cloud import bigquery
from config import Settings

class BillingAnalyzer:
    def __init__(self, settings=None, client=None):
        self.settings = (settings or Settings()).validate()
        self.client = client or bigquery.Client(project=self.settings.project_id)

    def _filters(self):
        conditions = []
        params = []
        s = self.settings
        for name, value, field in [
            ('account_id', s.billing_account_id, 'billing_account_id'),
            ('project_id', s.target_project_id, 'project.id'),
            ('month', s.invoice_month, 'invoice.month'),
        ]:
            if value:
                conditions.append(f'{field} = @{name}')
                params.append(bigquery.ScalarQueryParameter(name, 'STRING', value))
        return (' WHERE ' + ' AND '.join(conditions)) if conditions else '', params

    def _base(self):
        where, params = self._filters()
        credit_filter = "AND c.type = 'PROMOTION'"
        if self.settings.credit_name:
            credit_filter += ' AND c.name = @credit_name'
            params.append(bigquery.ScalarQueryParameter('credit_name', 'STRING', self.settings.credit_name))
        sql = f"""
        WITH source AS (
          SELECT
            billing_account_id AS account_id,
            COALESCE(project.id, '(unassigned)') AS project_id,
            COALESCE(service.description, '(unknown)') AS service,
            COALESCE(sku.description, '(unknown)') AS sku,
            DATE(usage_start_time) AS usage_day,
            invoice.month AS invoice_month,
            currency,
            cost,
            COALESCE((SELECT SUM(c.amount) FROM UNNEST(credits) AS c), 0) AS all_credits,
            COALESCE((SELECT SUM(c.amount) FROM UNNEST(credits) AS c WHERE TRUE {credit_filter}), 0) AS promo_credits
          FROM {self.settings.table_id}
          {where}
        )
        """
        return sql, params

    def _run(self, select, params=None):
        base, base_params = self._base()
        job_config = bigquery.QueryJobConfig(query_parameters=base_params + (params or []), maximum_bytes_billed=1_000_000_000)
        rows = self.client.query(base + select, job_config=job_config).result()
        return [dict(row) for row in rows]

    @staticmethod
    def _metrics():
        return "ROUND(SUM(cost), 2) AS gross_cost, ROUND(-SUM(all_credits), 2) AS all_credits_applied, ROUND(-SUM(promo_credits), 2) AS promotional_credits_used, ROUND(SUM(cost + all_credits), 2) AS net_cost"

    def overview(self):
        sql = f'SELECT currency, {self._metrics()}, COUNT(*) AS line_items FROM source GROUP BY currency ORDER BY promotional_credits_used DESC'
        return self._run(sql)

    def breakdown(self, dimension='service', limit=20):
        allowed = {'service':'service', 'sku':'service, sku', 'project':'project_id', 'day':'usage_day', 'month':'invoice_month', 'account':'account_id'}
        if dimension not in allowed:
            raise ValueError('Unsupported breakdown dimension')
        fields = allowed[dimension]
        limit = min(max(int(limit), 1), 100)
        sql = (f'SELECT {fields}, currency, {self._metrics()} FROM source '
               f'GROUP BY {fields}, currency ORDER BY promotional_credits_used DESC LIMIT @row_limit')
        return self._run(sql, [bigquery.ScalarQueryParameter('row_limit', 'INT64', limit)])

    def credit_names(self):
        """List all credit types/names, enabling identification of the $400 grant."""
        where, params = self._filters()
        sql = f"""SELECT c.type AS credit_type, c.name AS credit_name, t.currency,
                    ROUND(-SUM(c.amount),2) AS amount_applied
                  FROM {self.settings.table_id} AS t CROSS JOIN UNNEST(t.credits) AS c
                  {where}
                  GROUP BY credit_type, credit_name, currency
                  ORDER BY amount_applied DESC"""
        return [dict(r) for r in self.client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params, maximum_bytes_billed=1_000_000_000)).result()]

    def report(self):
        return {'overview': self.overview(), 'by_service': self.breakdown('service'),
                'by_sku': self.breakdown('sku'), 'by_project': self.breakdown('project'),
                'by_day': self.breakdown('day', 60)}
