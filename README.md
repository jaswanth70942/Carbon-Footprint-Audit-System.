# Carbon-Footprint-Audit-System.
SDG 13: Industrial Climate Intelligence Platform
An enterprise-grade carbon auditing system designed to automate operational decarbonization roadmaps. This platform leverages the Llama-4 Maverick reasoning model to transform raw operational logs into verified carbon intelligence.

📊 Project Overview
This project addresses United Nations Sustainable Development Goal 13 (Climate Action) by providing organizations with a dual-input tool to monitor, verify, and mitigate their environmental footprint.

Key Features
Dual-Input Ingestion: Supports both unstructured operational narratives (text) and structured system logs (CSV).

Verified Calculations: Integrates with the Climatiq 30.30 database for grid-accurate emission factors.

Categorical Aggregation: Automatically groups repetitive data entries to provide a clean, high-level strategic overview.

Strategic Action Plan: Generates a point-based decarbonization roadmap across three pillars: Efficiency, Technical Retrofitting, and Governance.

🛠️ Tech Stack
Core Model: Llama-4-Maverick-17B (via IBM Watsonx.ai).

Interface: Gradio (Custom Emerald & White UI).

Data Processing: Pandas & NumPy.

Document Parsing: Docling (for PDF/Markdown conversion).

Verification Engine: Climatiq API.

🚀 Getting Started
1. Prerequisites
You will need API keys for the following services:

IBM Watsonx: For the Maverick LLM reasoning.

Climatiq: For verified emission calculations.

2. Environment Setup (Google Colab)
Store your credentials in the Secrets (🔑) tab of your Colab notebook:

WATSONX_APIKEY

WATSONX_PROJECT_ID

CLIMATIQ_API_KEY

3. Usage
Run the script: The dashboard will launch on a public .gradio.live URL.

Upload/Enter Data: Paste a narration like "Used 500 kWh of electricity" or upload your logs.csv.

Analyze: View the aggregated bar charts and the point-based Strategic Action Plan generated specifically for your highest impact area.

📍 Strategic Roadmap Pillars
The auditor breaks down suggestions into three actionable categories:

Efficiency & Load Management: Focusing on sub-metering and demand response.

Technical Decarbonization: Including infrastructure retrofitting and fleet electrification.

Strategic Governance: Managing supply chain emissions and green procurement.
