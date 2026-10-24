# GCP Billing Mini Chatbot

An AI-powered Google Cloud billing and cost optimization
chatbot built with Python, BigQuery, and Gemini.

## Overview

This project explores how generative AI and Google Cloud
services can be combined to analyze cloud billing data,
answer natural-language questions, and identify potential
cost optimization opportunities.

Originally developed as a hands-on GCP learning project.

## Technologies

- Python
- Google Cloud BigQuery
- Google Cloud Vertex AI / Gemini
- Flask
- Google Cloud SDK

## Project Structure

- app.py - Web application entry point
- chatbot.py - Chatbot logic
- cli_chatbot.py - Command-line chatbot
- bigquery_client.py - BigQuery integration
- gemini_client.py - Gemini integration
- config.py - Application configuration
- data/ - Project data files

## Getting Started

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:

   pip install -r requirements.txt

4. Configure Google Cloud authentication and required
   project settings.
5. Configure access to the appropriate BigQuery datasets.
6. Run the application using the appropriate entry point.

## Security

Never commit service account keys, API keys, or .env files.
Use Application Default Credentials or another appropriate
Google Cloud authentication method.

## Background

Inspired by the Whizlabs AI-Powered Cost Optimization
Chatbot hands-on lab.

Lab:
https://www.whizlabs.com/labs/ai-powered-cost-optimization-chatbot
