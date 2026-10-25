import os
import sys
import unittest
from unittest.mock import MagicMock
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import types
if 'google.cloud.bigquery' not in sys.modules:
    google = sys.modules.setdefault('google', types.ModuleType('google'))
    google.__path__ = []
    cloud = sys.modules.setdefault('google.cloud', types.ModuleType('google.cloud'))
    cloud.__path__ = []
    bq = types.ModuleType('google.cloud.bigquery')
    bq.ScalarQueryParameter = lambda *args: args
    bq.QueryJobConfig = lambda **kwargs: kwargs
    cloud.bigquery = bq
    sys.modules['google.cloud.bigquery'] = bq
if 'dotenv' not in sys.modules:
    dotenv = types.ModuleType('dotenv')
    dotenv.load_dotenv = lambda: None
    sys.modules['dotenv'] = dotenv
from config import Settings
from billing import BillingAnalyzer
from chatbot import CreditChatbot

class BillingTests(unittest.TestCase):
    def setUp(self):
        self.settings = Settings(project_id='my-project', billing_project_id='billing-project', dataset='billing_export', table='gcp_billing_export_v1_ABC', credit_start_amount=400)
        self.client = MagicMock()
        self.client.query.return_value.result.return_value = []
        self.analyzer = BillingAnalyzer(self.settings, self.client)

    def test_safe_table_identifier_and_nested_schema(self):
        self.analyzer.overview()
        sql = self.client.query.call_args.args[0]
        self.assertIn('`billing-project.billing_export.gcp_billing_export_v1_ABC`', sql)
        self.assertIn('UNNEST(credits)', sql)
        self.assertIn("c.type = 'PROMOTION'", sql)
        self.assertIn('SUM(cost + all_credits)', sql)

    def test_invalid_breakdown_rejected(self):
        with self.assertRaises(ValueError):
            self.analyzer.breakdown('service; DROP TABLE')

    def test_amount_not_claimed_as_balance(self):
        report = {'overview':[], 'by_service':[], 'by_sku':[]}
        output = CreditChatbot.format_report(report, 400, 37)
        self.assertIn('$37.00', output)
        self.assertIn('NOT a verified remaining', output)

if __name__ == '__main__':
    unittest.main()
