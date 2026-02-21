# Alauda Global Legal Agent User Manual

**Version**: 2.0  
**Last Updated**: February 20, 2026  
**For**: Alauda Legal Team

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Agent Persona Configuration](#2-agent-persona-configuration)
3. [Review Dimensions](#3-review-dimensions)
   - 3.1 Sales Contract Dimensions
   - 3.2 Technical Support Contract Dimensions
4. [Redline Knowledge Base](#4-redline-knowledge-base)
5. [User Guide](#5-user-guide)
6. [Output Report Explanation](#6-output-report-explanation)
7. [FAQ](#7-faq)
8. [Appendix](#8-appendix)

---

## 1. Introduction

This manual provides Alauda's legal team with an AI-powered automated contract review solution. By integrating Red Hat's legal logic with strict commercial risk filtering in OpenCode, the initial review time is reduced from hours to **5 minutes**.

### Key Benefits

| Aspect | Traditional | AI Agent |
|--------|-------------|----------|
| Initial Review Time | 2-4 hours | 5 minutes |
| Risk Coverage | Depends on experience | 13 dimensions covered |
| Revision Suggestions | Manual drafting | Auto-generated Legal English |
| Consistency | Varies by reviewer | Unified standards |

---

## 2. Agent Persona Configuration

Create a new role in OpenCode Agent Settings with the following configuration:

### Agent Name
**Alauda Global Legal & Operations Architect**

### Core Logic (Persona)

```
You are a legal expert specializing in global laws and open source software, 
focused on providing contract risk review services for Alauda.

Core Principles:
1. Liability Cap: Maintain 12 months subscription fee cap, reject any 
   liability exceeding 12 months paid amount
2. IP Rights: Distinguish "Custom Deliverables" from "Core Platform". 
   Alauda must retain ownership of core PaaS platform and derivative works
3. Acceptance Terms: Convert "subjective acceptance" to "deemed acceptance" 
   with 10-day buffer period
4. Exclusivity of Remedies: Ensure Fee Reductions are the sole remedy for 
   delays or service deficiencies

Contract Type Recognition:
- Sales Contracts: Focus on liability, IP, acceptance, termination terms
- Technical Support Contracts: Focus on SLA, support scope, training 
  commitments, support duration
```

---

## 3. Review Dimensions

### 3.1 Sales Contract Dimensions (7)

| Dimension | Risk Assessment Criteria |
|-----------|-------------------------|
| **Subscription Metrics** | RED: Enterprise-wide / Unlimited use → GREEN: Unit-based (Node/Core) |
| **Liability** | RED: 3x cap / Unlimited → GREEN: 12 months fees (EULA Free: $50) |
| **IP Rights** | RED: Customer owns all derivatives → GREEN: Alauda retains core |
| **Acceptance** | RED: Written approval required → GREEN: 10-day deemed acceptance |
| **Termination** | RED: Immediate termination / No right → GREEN: 30-90 days notice |
| **Governing Law** | RED: Customer exclusive jurisdiction → GREEN: Neutral forum |
| **Data Protection** | RED: Supplier solely responsible → GREEN: Mutual compliance |

### 3.2 Technical Support Contract Dimensions (7)

| Dimension | Risk Assessment Criteria |
|-----------|-------------------------|
| **SLA Response** | RED: Level 1 < 30 mins → GREEN: Level 1: 30 mins |
| **Support Scope** | RED: Unlimited / Custom dev / On-site → GREEN: Clear exclusions |
| **Exclusion of Liability** | RED: Liable for all losses → GREEN: Exclude indirect damages |
| **Training Commitment** | RED: >100 hrs/year YELLOW: 60-80 hrs → GREEN: <=40 hrs/year |
| **Support Duration** | RED: Lifetime YELLOW: Entire contract → GREEN: 18 months |
| **Access Rights** | RED: Direct production access → GREEN: Screen share only |
| **Support Termination** | RED: No termination right YELLOW: Customer can reject → GREEN: 90 days notice |

---

## 4. Redline Knowledge Base

### 4.1 Sales Contract Redline Matrix

#### Subscription Metrics

| Risk Point | Alauda Standard | Rationale |
|:-----------|:----------------|:----------|
| Enterprise-wide or unlimited usage rights | Strictly Unit-based (Node/Core) metric pricing | Ensure commercial revenue matches consumption |

#### Liability

| Risk Point | Alauda Standard | Rationale |
|:-----------|:----------------|:----------|
| Liability cap at 3x paid amount or unlimited | Cap at 12 months fees (or $50 for EULA free tier) | Aligns with SaaS risk hedging standards (Red Hat/SUSE benchmarks) |

#### Intellectual Property

| Risk Point | Alauda Standard | Rationale |
|:-----------|:----------------|:----------|
| Customer owns all derivative works | Custom parts to Customer, core optimization rights to Alauda | Protect core product distribution rights |

#### Acceptance

| Risk Point | Alauda Standard | Rationale |
|:-----------|:----------------|:----------|
| Written customer confirmation required | Deemed accepted if no written rejection within 10 business days | Resolve cash flow delays |

#### Remedies

| Risk Point | Alauda Standard | Rationale |
|:-----------|:----------------|:----------|
| Fee reductions exclude further claims | Fee Reductions are the sole remedy for delays | Ensure predictable breach costs |

### 4.2 Technical Support Contract Redline Matrix

#### SLA Response Time

| Risk Point | Alauda Standard | Rationale |
|:-----------|:----------------|:----------|
| Level 1 response < 30 mins | 30 mins initial response | Match latest company operational standards |
| Level 2 response < 2 hours | 2 hours initial response | Same as above |
| Level 3/4 response < 4/8 hours | 4 hours / 8 hours initial response | Same as above |
| 24/7 support | Negotiable hours | Consider operational costs |

#### Support Scope

| Risk Point | Alauda Standard | Rationale |
|:-----------|:----------------|:----------|
| Custom code development or on-site support included | Explicitly exclude custom development and on-site support | Match Alauda standard SLA and avoid uncontrolled scope |
| Support for all third-party software | Limit to Alauda explicitly certified environments | Reduce operational burden |

#### Training Commitment

| Risk Point | Alauda Standard | Rationale |
|:-----------|:----------------|:----------|
| 72 hours/year | 40 hours/year | Avoid training cost overrun |
| Any software-related topic | Limited topic list | Control scope creep |

#### Support Duration

| Risk Point | Alauda Standard | Rationale |
|:-----------|:----------------|:----------|
| Entire contract period | 18 months (current + previous major version) | Control long-term maintenance costs |
| All historical versions | Current and one prior major version only | Avoid "zombie version" maintenance burden |

#### Support Termination

| Risk Point | Alauda Standard | Rationale |
|:-----------|:----------------|:----------|
| Customer can reject termination | Either party may terminate with 90 days notice | Maintain business flexibility |

---

## 5. User Guide

### 5.1 Installation

```bash
# Script location
/Users/rootwang/opencode/Legal/alauda_legal_agent.py

# Run permission (first time only)
chmod +x /Users/rootwang/opencode/Legal/alauda_legal_agent.py
```

### 5.2 Basic Usage

#### Option 1: Direct text input

```bash
python3 /Users/rootwang/opencode/Legal/alauda_legal_agent.py -t "contract text..."
```

#### Option 2: Read from file

```bash
# Supports .txt, .md, .json formats
python3 /Users/rootwang/opencode/Legal/alauda_legal_agent.py -f contract.txt
```

#### Option 3: Save report to file

```bash
python3 /Users/rootwang/opencode/Legal/alauda_legal_agent.py -f contract.txt --output report.md
```

### 5.3 Output Format Options

| Parameter | Description |
|-----------|-------------|
| `-o markdown` | Output Markdown format (default) |
| `-o json` | Output JSON format (for system integration) |
| `--no-mode-b` | Output Mode A only, exclude revision suggestions |

### 5.4 Complete Command Examples

```bash
# Generate full report (Mode A + Mode B)
python3 alauda_legal_agent.py -f contract.txt --output review_report.md

# Generate risk comparison table only
python3 alauda_legal_agent.py -f contract.txt --no-mode-b --output risk_table.md

# Generate JSON format (for system integration)
python3 alauda_legal_agent.py -f contract.txt -o json --output report.json
```

---

## 6. Output Report Explanation

### 6.1 Mode A: Risk Comparison Table

Mode A provides a structured risk overview for quick identification of problematic clauses:

```
| Dimension | Clause Summary | Risk Level | Alauda Standard | Risk Reason |
| :--- | :--- | :---: | :--- | :--- |
| Liability | ... | RED HIGH | 12 months fees | Cap too high (3x) |
```

**Risk Level Icons**:
- **RED HIGH** - Requires immediate modification, not acceptable
- **YELLOW MEDIUM** - Suggest modification, negotiable
- **GREEN LOW** - Meets Alauda standards
- **WHITE N/A** - Relevant clause not detected

### 6.2 Mode B: Suggested Revision Text

Mode B provides ready-to-use Legal English revision suggestions:

```
### Liability

**Risk**: Liability cap too high (3x)

**Suggested Revision**:
```
Supplier's total aggregate liability shall not exceed the total fees 
paid by Customer in the 12 months preceding the claim.
```
```

### 6.3 Review Summary

The report ends with statistical data:

```
| Risk Level | Count |
| :---: | :---: |
| RED High | 1 |
| YELLOW Medium | 3 |
| GREEN Low | 9 |
```

---

## 7. FAQ

### Q1: What if the governing law is from a new jurisdiction?

The Agent automatically detects the **Governing Law** clause and alerts legal counsel to jurisdiction-specific considerations. Review standards may need adjustment for different jurisdictions.

### Q2: What if the Agent misses a clause?

Click **"Add to Knowledge"** and it will be recognized next time when reviewing similar contracts (e.g., UOB or OCBC). You can also add new rules to the `benchmark` configuration in the script.

### Q3: How to handle Russian/English mixed contracts?

The script supports multilingual contract recognition and automatically handles Russian (e.g., "поддержк", "обучен") and English mixed text.

### Q4: Can risk levels be adjusted?

Yes. Modify the regex rules in the `risk_rules` configuration in the script. You can move rules from `high` to `medium` or vice versa.

### Q5: How to add new review dimensions?

Add a new category to the `benchmark` dictionary in the script:

```python
"new_category": {
    "keywords": [r"keyword1", r"keyword2"],
    "redline": "Alauda standard requirement",
    "standard_clause": "Standard clause text",
    "rationale": "Reason explanation",
    "risk_rules": {
        "high": [(r"pattern", "Risk reason")],
        "medium": [(r"pattern", "Risk reason")]
    }
}
```

### Q6: How to handle Word/PDF format contracts?

**Method 1**: Use macOS built-in tool
```bash
textutil -convert txt contract.docx -output contract.txt
```

**Method 2**: Copy and paste directly
```bash
python3 alauda_legal_agent.py -t "$(pbpaste)"
```

---

## 8. Appendix

### 8.1 Complete Review Dimension List

| No. | Dimension Code | Name | Contract Type |
|:----:|:---------------|:-----|:--------------|
| 1 | liability | Liability | Sales Contract |
| 2 | ipr | Intellectual Property | Sales Contract |
| 3 | acceptance | Acceptance | Sales Contract |
| 4 | termination | Termination | Sales Contract |
| 5 | governing_law | Governing Law | Sales Contract |
| 6 | data_protection | Data Protection | Sales Contract |
| 7 | sla_response | SLA Response | Technical Support |
| 8 | support_scope | Support Scope | Technical Support |
| 9 | exclusion_liability | Exclusion of Liability | Technical Support |
| 10 | training_commitment | Training Commitment | Technical Support |
| 11 | support_duration | Support Duration | Technical Support |
| 12 | access_rights | Access Rights | Technical Support |
| 13 | termination_support | Support Termination | Technical Support |

### 8.2 Standard Clause Templates

#### Liability
```
Supplier's total aggregate liability shall not exceed the total fees 
paid by Customer in the 12 months preceding the claim.
```

#### Intellectual Property
```
Alauda retains all rights to the pre-existing platform (PaaS) and any 
derivative works based on its core technology. Customer owns only custom 
components developed specifically for Customer.
```

#### Acceptance
```
Deliverables are deemed accepted if no written rejection is received 
within 10 business days of delivery.
```

#### SLA Response
```
Response times: P1 (Critical): 30 minutes initial response; P2 (High): 2 hours; 
P3 (Medium): 4 hours; P4 (Low): 8 hours. Resolution times 
to be determined on a best-effort basis.
```

#### Training Commitment
```
Alauda will provide up to 40 hours of online training per year. Additional 
training may be purchased at agreed rates. Training content and schedule 
to be mutually agreed.
```

#### Support Duration
```
Warranty support is provided for the current major version and one prior 
major version, for a maximum of 18 months from general availability of 
the new major version.
```

#### Exclusion of Liability
```
In no event shall Alauda be liable for any indirect, incidental, special, 
consequential, or punitive damages, including without limitation loss of 
profits, data, use, or goodwill, regardless of the form of action.
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-03-03 | Initial version, 6 sales contract dimensions |
| 2.0 | 2026-02-20 | Added 7 technical support dimensions, multilingual support |

---

## Support

For questions or suggestions, please contact the legal team or submit an Issue to the script repository.

---

*This manual was created with assistance from Alauda Global Legal Agent*
