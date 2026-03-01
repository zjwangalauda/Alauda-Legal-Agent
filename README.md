# Alauda Global Legal Agent — AI Contract Review Copilot

AI-powered contract review copilot built on Streamlit, designed for Alauda's enterprise SaaS/PaaS business. Combines senior legal partner acumen with LLM panoramic reading to seal fatal loopholes in B2B contracts within seconds.

## Core Capabilities

| Feature | Description |
|---------|-------------|
| Single-Doc Review | Upload a single contract (PDF/DOCX/TXT) for comprehensive AI audit |
| Multi-Doc Graph Audit | Upload a ZIP bundle of related contracts for cross-document backdoor detection |
| Three-Role Copilot | CXO decision desk + Commercial operations dashboard + Legal compliance matrix |
| Native Word Redlining | Auto-generate Track Changes (.docx) with strikethrough + insertion markup |
| Agnostic LLM Engine | Google Gemini, OpenAI, Anthropic Claude, or custom OpenAI-compatible endpoints |

## Quick Start

```bash
# 1. Install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the app (built-in free AI engine, no API key required)
streamlit run web_app.py
```

Optional environment variables:
- `GEMINI_API_KEY` — Google Gemini API key (for Google engine)
- `OPENAI_API_KEY` / `OPENAI_API_BASE` — OpenAI-compatible endpoint
- `ANTHROPIC_API_KEY` — Anthropic Claude API key

## Project Structure

```
├── web_app.py                 # Streamlit entrypoint (Web dashboard)
├── alauda_legal_agent.py      # Core LLM agent (inference, schemas, prompts)
├── docx_redline_engine.py     # Native Word Track Changes engine
├── assets/                    # Static assets (CSS theme)
├── Alauda brand/              # Brand assets (favicon, logo)
├── 参考文档库/                  # Reference document library
├── tests/                     # Pytest test suite
├── .streamlit/                # Streamlit config
├── Dockerfile                 # Container deployment
└── .github/workflows/         # CI/CD pipeline
```

## Running Tests

```bash
pip install pytest ruff
python -m pytest tests/ -v
ruff check .
```

## Docker

```bash
docker build -t legal-agent .
docker run -p 8501:8501 legal-agent
```

## CLI Mode

```bash
# Single document review
python3 alauda_legal_agent.py -f contract.pdf -o report.md

# Multi-document directory review
python3 alauda_legal_agent.py -d ./contract_bundle/ -o report.md
```
