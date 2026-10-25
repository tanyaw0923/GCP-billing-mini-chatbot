import os
import re
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()
IDENT = re.compile(r'^[A-Za-z0-9_-]+$')

@dataclass(frozen=True)
class Settings:
    project_id: str = os.getenv('PROJECT_ID', '')
    billing_project_id: str = os.getenv('BILLING_PROJECT_ID', '')
    dataset: str = os.getenv('BIGQUERY_DATASET', '')
    table: str = os.getenv('BIGQUERY_TABLE', '')
    billing_account_id: str = os.getenv('BILLING_ACCOUNT_ID', '')
    target_project_id: str = os.getenv('TARGET_PROJECT_ID', '')
    invoice_month: str = os.getenv('INVOICE_MONTH', '')
    credit_start_amount: float = float(os.getenv('CREDIT_START_AMOUNT', '400'))
    credit_name: str = os.getenv('CREDIT_NAME', '')
    gemini_model: str = os.getenv('GEMINI_MODEL', 'gemini-3-flash-preview')
    location: str = os.getenv('GOOGLE_CLOUD_LOCATION', 'global')
    enable_gemini: bool = os.getenv('ENABLE_GEMINI', 'false').lower() == 'true'

    def validate(self):
        for label, value in [('PROJECT_ID', self.project_id), ('BIGQUERY_DATASET', self.dataset), ('BIGQUERY_TABLE', self.table)]:
            if not value or not IDENT.fullmatch(value):
                raise ValueError(f'{label} must be a nonempty Google Cloud identifier')
        if self.billing_project_id and not IDENT.fullmatch(self.billing_project_id):
            raise ValueError('Invalid BILLING_PROJECT_ID')
        if self.invoice_month and not re.fullmatch(r'\d{6}', self.invoice_month):
            raise ValueError('INVOICE_MONTH must be YYYYMM or blank')
        if self.credit_start_amount < 0:
            raise ValueError('CREDIT_START_AMOUNT cannot be negative')
        return self

    @property
    def table_id(self):
        return f'`{self.billing_project_id or self.project_id}.{self.dataset}.{self.table}`'
