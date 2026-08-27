# Zycus Assignment Evaluation Report
**Generated At:** 2026-08-09 07:25:34 UTC  
**Pass Rate:** 100.0% (10/10 Passed)  
**Overall Quality Score:** `0.95 / 1.0`  
**Average Latency:** `20179.69 ms`  

## Test Suite Results Summary

| Test ID | Task / Target | Type | Status | Score | Latency | Summary |
|---|---|---|---|---|---|---|
| `T1-001` | Standard P1 Bug - Database Timeout Outage | Standard | PASS | `0.75` | `29935.24ms` | Category: Integration, Urgency: P1, Team: Integrations Engineering (Notes: Expected category 'Bug', got 'Integration') |
| `T1-002` | Standard P3 How-To - SSO Configuration Guidance | Standard | PASS | `1.0` | `5618.97ms` | Category: How-To, Urgency: P4, Team: Tier-1 Support |
| `T1-003` | Standard P2 Integration - Salesforce Webhook Disconnected | Standard | PASS | `1.0` | `85094.22ms` | Category: Integration, Urgency: P2, Team: Integrations Engineering Team |
| `T1-004` | Standard P4 Billing - Invoice Copy Request | Standard | PASS | `0.75` | `24385.3ms` | Category: How-To, Urgency: P4, Team: Tier-1 Support (Notes: Expected category 'Billing', got 'How-To') |
| `T1-005_ADV` | Adversarial Test - Ambiguous Subject, Contradictory Urgency & PII | Adversarial | PASS | `1.0` | `9402.21ms` | Category: Bug, Urgency: P4, Team: Tier-1 Support |
| `T2-001` | Standard Account Brief - Initech (ACC-3847) | Standard | PASS | `1.0` | `0.34ms` | Company: Account ACC-3847 (Not Found), Risks Flagged: 1, Talking Points: 1 |
| `T2-002` | Standard Account Brief - Omni Consumer Products (ACC-3336) | Standard | PASS | `1.0` | `47359.93ms` | Company: Omni Consumer Products, Risks Flagged: 2, Talking Points: 3 |
| `T2-003` | Determinism Test - Same Account Identical Outputs | Standard | PASS | `1.0` | `0.34ms` | Company: Account ACC-3847 (Not Found), Risks Flagged: 1, Talking Points: 1 |
| `T2-004` | Account with High Churn Escalations | Standard | PASS | `1.0` | `0.24ms` | Company: Account ACC-3847 (Not Found), Risks Flagged: 1, Talking Points: 1 |
| `T2-005_ADV` | Adversarial Test - Non-Existent Account ID (ACC-999999) | Adversarial | PASS | `1.0` | `0.09ms` | Company: Account ACC-999999 (Not Found), Risks Flagged: 1, Talking Points: 1 |

## Acceptance Criteria & Evaluation Logic
- **Task 1 Triage Agent**: Validates schema completeness, enum compliance (`P1-P4`), expected category matching, and PII redaction.
- **Task 2 Account Summariser**: Validates 3-section QBR brief presence, direct quote justification for risks, and 100% determinism across repeat executions.
- **Quality Threshold**: Minimum score of `0.70` required to earn a PASS rating.