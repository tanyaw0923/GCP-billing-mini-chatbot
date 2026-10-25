# GCP Credit Tracker Chatbot

Analyzes **your own Google Cloud Billing standard usage export** in BigQuery to explain which services, billed activities (SKUs), and projects used promotional credits. Includes a browser chatbot and CLI. Does not need Gemini for basic analysis; Gemini is optional.

## Setup

1. In Cloud Billing, choose your billing account → **Billing export** → enable **Standard usage cost export** to BigQuery. An export is not necessarily retroactive and data can arrive late.
2. In BigQuery Explorer, find the export table named `gcp_billing_export_v1_...`. Use the full project ID, dataset, and table names.
3. Use Cloud Shell or local Python 3.10+:

   ```bash
   cd chatbot
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

4. Edit `.env` with your own GCP project ID, billing export dataset and exact table name (without backticks). `BILLING_PROJECT_ID` identifies the project containing the export. `PROJECT_ID` identifies the project that runs queries. You can leave `INVOICE_MONTH` blank for all exported rows, or set e.g. `202610` to select an invoice month.
5. Authenticate with **Application Default Credentials** (`gcloud auth application-default login` for an ordinary local session), and grant the identity BigQuery job creation permission on the query project and data viewing permission on the export dataset. Follow your environment's existing authentication procedures in managed labs.
6. Run `python cli.py` or `python app.py` then use Cloud Shell Web Preview on port 8080 (Cloud Shell's preview proxies localhost). Run tests with `python -m unittest discover -s tests -v`.

## What it calculates

- Gross cost = `SUM(cost)`.
- All credits applied = negative of sums of **all** nested credit entries.
- Net cost = `SUM(cost + all_credits)`, including promotional credits and other discount types.
- Promotional credits used = negative of sums of credit entries with `credits.type='PROMOTION'`.
- Breakdowns by **service, SKU, project, usage day**, with currency kept separate.
- Set `CREDIT_NAME` to a specific credit name after finding it with `BillingAnalyzer().credit_names()` if multiple promotional grants exist.

**Important:** The configured `$400` is a starting reference, not a confirmed balance. The export shows applied credits for available exported rows, not an authoritative promotional-credit balance. The account's **Billing → Credits** page is the source of truth for grant balance/expiration. Don't subtract exported credit totals from $400 to assert a live remaining balance unless coverage, timing, currency and credit identity are independently verified. Standard export doesn't identify individual compute actions like particular user commands or VM resources; SKU and service are the most specific fields available without more detailed logs/data. Some credit attribution may not match the underlying operational cause. Invoice month and usage dates can differ.

## Optional Gemini responses

Set `ENABLE_GEMINI=true`, `GEMINI_MODEL` to a model enabled in your account, and `GOOGLE_CLOUD_LOCATION=global` if supported. This uses the current `google-genai` SDK with Vertex AI; model access can vary by project/location. Errors fall back to a deterministic billing summary.

## Cost and security

BigQuery queries incur charges; to limit scans the app sets a 1 GB maximum billed bytes per query (change only if needed). The app is intended for a private/local environment; don't expose its Flask service publicly without authentication. `.env`, private keys, and credentials are ignored by Git. Enable only the minimum required permissions. Never upload raw billing exports to a public GitHub repository.
