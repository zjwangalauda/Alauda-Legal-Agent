# 🚀 Alauda Global Legal Agent (V6.1) User Manual

**Version**: 6.2.1 (Security & Quality Hardening Edition)
**Last Updated**: March 2, 2026
**Target Audience**: Alauda Legal, Delivery, Commercial, and CXO Executive Teams

---

## Cloud Access

- **Streamlit Cloud URL**: [Alauda Global Legal Agent](https://alauda-legal-agent.streamlit.app/)
*(Bookmark this link for instant access from any device — no installation required)*

---

## Table of Contents

1. [Core Vision & Architectural Evolution](#1-core-vision--architectural-evolution)
2. [V5 Exclusive Feature: Multi-Role Copilot](#2-v5-exclusive-feature-multi-role-copilot)
3. [Multi-Doc Dependency Graph Auditing](#3-multi-doc-dependency-graph-auditing)
4. [SaaS Commercial & Legal Baselines](#4-saas-commercial--legal-baselines)
5. [Operational Guide (Web App, CLI, Docker & Testing)](#5-operational-guide-web-app--cli)
6. [Output Report Case Study](#6-output-report-case-study)

---

## 1. Core Vision & Architectural Evolution

This manual provides guidance for the **Alauda Global Legal Agent**, an automated contract review system powered by an end-to-end Large Language Model (LLM). Our vision is to combine the commercial acumen of a senior legal partner with the panoramic reading capabilities of AI to seal fatal loopholes in B2B contracts within seconds.

Following rapid architectural iterations, the system has now evolved to the **V6.2.1 (Security & Quality Hardening Edition)**:
- **Built-in Free AI Engine**: The system now ships with an embedded Claude Haiku inference engine. Users can access all core features immediately — **no API key required**. Power users may still switch to OpenAI/Anthropic/Google models via the sidebar.
- **Agnostic LLM Engine**: Decoupled from a single provider, dynamically supporting Google Gemini, OpenAI, Claude, or internal private model gateways.
- **Structured Defense (Pydantic)**: Utilizes strict JSON data contracts to force the LLM to adaptively output idiomatic legal revision suggestions based on the original language (English/Chinese) of the contract.
- **Modern Web UI**: Features an advanced visual dashboard built with Streamlit, incorporating Alauda's corporate design system, leaving behind the tedious command line.
- **Redline Engine Overhaul**: Completely rebuilt Word Track Changes engine with 80-character precision matching, DOM caching, and visual strikethrough markup.
- **CI/CD & Containerization (V6.2)**: Added GitHub Actions pipeline (ruff lint + pytest), Docker containerized deployment, and 12 core unit tests.

---

## 2. V5 Exclusive Feature: Multi-Role Copilot

The greatest breakthrough in V5 is that the system is no longer a simple "spell checker," but has transformed into an advanced commercial strategist with a "triple persona." For every uploaded dossier, the system deconstructs it into a three-tier pyramid perspective:

1. 👨‍💼 **CXO Executive Decision Desk (The Apex)**:
   - Provides an unequivocal approval recommendation (e.g., [Sign Directly] / [Conditional Approval] / [Reject]).
   - Distills fatal impediments ("Deal Breakers").
   - Authors a "Strategic Playbook" containing trade-off strategies and redline boundaries for executives.
2. 📈 **Commercial & Operations Dashboard (The Middle)**:
   - Automatically extracts critical commercial metrics hidden in voluminous texts—such as total contract value, payment terms, service periods, and penalty clauses—specifically for PMO and Finance.
   - Calculates and highlights the real operational and cash flow impact of these terms.
3. ⚖️ **Legal & Compliance Defense Matrix (The Foundation)**:
   - Itemizes all high/medium risk clauses that violate company SaaS policies.
   - Provides legal rationale and ready-to-use Redline revisions.

---

## 3. Multi-Doc Dependency Graph Auditing

In large B2B procurements, clients often employ a "Trojan Horse" strategy: agreeing to all baselines in the strict Master Agreement (GFA), only to secretly insert an overriding clause into a Statement of Work (SOW) signed by a delivery team, claiming: *"This SOW holds the highest priority, and the supplier assumes unlimited data liability."*

**The Agent's Cross-Document Graph Workflow:**
1. **Topology Construction**: Automatically extracts the `Order of Precedence` from all files, constructing a hierarchical tree of authority.
2. **Backdoor Detection**: Utilizing a million-token context, it cross-references high-priority appendices against the protective redlines of the low-priority master contract. If lower-level protections are overridden, it triggers a red alert and provides a targeted demolition clause.

---

## 4. SaaS Commercial & Legal Baselines

The Agent strictly defends the following 6 SaaS commercial lifelines:

| Monitoring Dimension | Risk Baseline & Business Logic |
|------|-----------------|
| **Subscription Metrics** | 🔴 Reject perpetual/unlimited use → 🟢 Must be measured by specific Units (Node/Core).<br>*Prevents customers from duplicating a single license enterprise-wide.* |
| **Liability Cap** | 🔴 Reject unlimited liability or data loss inclusion → 🟢 Capped at 12 months subscription fees (EULA free tier capped at $50).<br>*Enforces strict dual-track risk control, explicitly excluding indirect losses.* |
| **IP Rights** | 🔴 Reject derivatives owned by customer (Work for Hire) → 🟢 Retain ownership of core PaaS foundation.<br>*Prevents single-customer buyout leading to closed-sourcing of core code.* |
| **Acceptance** | 🔴 Reject unilateral written confirmation or infinite rejection loops → 🟢 Must include a 10-business-day Deemed Acceptance mechanism.<br>*Prevents customers from delaying the FAC to secure prompt SaaS payment settlement.* |
| **SLA Response** | 🔴 Reject <30 min / 24x7 unlimited support → 🟢 Match operational caps of P1 30mins, P2 2hrs.<br>*Rejects commitments that exceed the frontline Operations Center's (ROTC) capacity.* |
| **Support Scope** | 🔴 Reject on-site or third-party software catch-alls → 🟢 Remote support only within Alauda certified environments.<br>*Explicitly excludes custom code development to control fulfillment costs.* |

---

## 5. Operational Guide (Web App & CLI)

### 5.1 Cloud Access (Recommended)
Visit [Alauda Global Legal Agent](https://alauda-legal-agent.streamlit.app/) to start immediately — no installation required.

The system ships with a built-in free AI engine (Claude Haiku). **No API key is needed.**
- **Single-Doc Mode**: Upload a PDF/Word (.docx) document directly.
- **Multi-Doc Mode**: Package the entire dossier into a `.zip` file for a breathtaking topology and backdoor radar experience.
- **Bring Your Own Model (Optional)**: Power users may switch to OpenAI/Anthropic/Google via the left sidebar and input their own API Key.

### 5.2 Local Deployment (Developers)
```bash
# Activate the virtual environment
source .venv/bin/activate
# Launch the enterprise-grade Web Dashboard
streamlit run web_app.py
```
Once launched, navigate to `http://localhost:8501`.

### 5.3 CLI Geek Mode
For technical users handling batch tasks, the native command line is available:
```bash
# Review a single file
python3 alauda_legal_agent.py -f contract.txt -o report.md

# Review a multi-document directory
python3 alauda_legal_agent.py -d ./customer_bundle/ -o report.md
```

### 5.4 Docker Deployment
```bash
docker build -t legal-agent .
docker run -p 8501:8501 legal-agent
```
Once launched, navigate to `http://localhost:8501`.

### 5.5 Testing & Code Quality
```bash
pip install pytest ruff
# Run unit tests (38 test cases)
python -m pytest tests/ -v
# Code quality check
ruff check .
```

---

## 6. Output Report Case Study

*(The following is an excerpt from a V5 Multi-Role output based on a real dossier from a major financial institution)*

### 👨‍💼 CXO Executive Decision Desk
- **Final Decision**: 🔴 **[Conditional Approval (Must dismantle backdoors)]**
- **Deal Breakers**: The SOW appendix uses precedence rules to override the GFA's liability cap, introducing an unlimited data claim exposure; additionally, it lacks a deemed acceptance mechanism.
- **Strategic Playbook**: This is a strategic benchmark client, and the 40% upfront payment significantly eases cash flow. It is advised not to reject outright. Instead, the VP of Legal should step in to mandate an overriding protection clause in the highest-priority Order Form. Simultaneously, assign senior architects to the delivery end to mitigate acceptance delay risks.

### 📈 Commercial & Operations Dashboard
| Core Metric | Contract Extract | Operational Impact Analysis |
| :--- | :--- | :--- |
| **Total Contract Value** | 3 Million RMB | Major deal, high revenue, high strategic significance. |
| **Payment Terms** | 20% - 40% - 40% (Over 3 years) | Low upfront payment creates significant working capital pressure during a two-year delivery phase. |
| **Warranty Period** | 36 months post-acceptance | Extremely high maintenance labor costs; warranty margin requires separate accounting. |

### ⚖️ Legal Risk Matrix

**💥 Backdoor #1: IP Rights - Forced Customer Ownership of Platform Derivatives 🔴 HIGH**
- **🏰 Master Clause Defense**:
  > GFA 11.1(3): MegaBank owns all rights, title and interest in and to Intellectual Property Rights developed during the course of providing Services... including enhancements, modifications or derivative works of materials...

- **🗡️ Overriding Clause in `General Terms.docx`**:
  > Software Module 5.2 reinforcement: Ownership of the Intellectual Property Rights in any customisations... will be governed by the relevant Service Module.

**💡 Risk Trace Analysis**:
The customer stipulates in the master framework that regardless of original IP ownership (including Alauda's core foundation), any enhancements or derivative works generated during service provision belong entirely to the customer. This means any peripheral plugins or architectural optimization scripts written by the Alauda delivery team on-site are legally confiscated by the bank, severely hindering Alauda's right to standardize these practices into the next product iteration.

**✅ Suggested Counter-Measure**:
```text
Delete 'enhancements, modifications or derivative works...' from GFA 11.1(3) and add a special protection utilizing the highest priority in the Order Form:
'Notwithstanding General Terms 11.1, Supplier retains all ownership to its pre-existing core platform and any derivative works thereof. MegaBank only owns custom deliverables explicitly stated as Work for Hire.'
```

---
*Alauda Global Legal Agent - Your intelligent legal and commercial command center.*