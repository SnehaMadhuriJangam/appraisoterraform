# CIS Controls v8.1 — Safeguard 3.1: Data Management Standard & Classification Report

**Document Title:** Appraiso Cloud Storage Classification & Governance Specification  
**Framework:** CIS Controls v8.1 (Safeguard 3.1, IG1)  
**Target Environment:** DEV / UAT / PROD  
**Target GCP Project:** `newaiproject-510015`  
**Region / Residency:** `us-central1`  
**Business Owner:** MSXI Data Governance / InfoSec  
**Technical Custodian:** Miracle / Appraiso Engineering  

---

## 1. Executive Summary
This document fulfills **CIS Controls v8.1 Safeguard 3.1 (Establish and Maintain a Data Management Process)** by classifying, inventorying, and establishing explicit retention, residency, encryption, and disposal controls for the three primary storage buckets in the Appraiso audit ecosystem:
1. `action-item-narratives`
2. `appraiso-audit-reports`
3. `smart-audit-multimedia`

---

## 2. CIS 3.1 Data Classification Matrix

| Governance Attribute | Bucket 1: `action-item-narratives` | Bucket 2: `appraiso-audit-reports` | Bucket 3: `smart-audit-multimedia` |
| :--- | :--- | :--- | :--- |
| **Full Bucket Name** | `newaiproject-510015-action-item-narratives` | `newaiproject-510015-appraiso-audit-reports` | `newaiproject-510015-smart-audit-multimedia` |
| **Data Description** | Corrective action plans, audit finding narratives, auditor notes, AI-generated action summaries | Official compiled audit reports, executive scorecards, compliance certificates, summary sheets | Dealership inspection photos, facility evidence images, audio/video walkthrough recordings |
| **Object File Types** | `.txt`, `.json`, `.md`, `.docx`, `.pdf` | `.pdf`, `.xlsx`, `.csv` | `.jpg`, `.jpeg`, `.png`, `.mp4`, `.wav` |
| **Data Sensitivity** | **Confidential** | **Confidential** | **Confidential / Restricted** (PII potential) |
| **1. Record Owner** | **MSXI Data Governance** (Business Owner)<br>**Miracle** (Technical Custodian) | **MSXI Data Governance** (Business Owner)<br>**Miracle** (Technical Custodian) | **MSXI Data Governance** (Business Owner)<br>**Miracle** (Technical Custodian) |
| **2. System of Record** | `appraiso-narratives-store` | `appraiso-reports-store` | `appraiso-multimedia-evidence` |
| **3. Retention (Min / Max)** | **Min:** 6 Years (2,190 Days)<br>**Max:** 6.5 Years (2,372 Days) | **Min:** 6 Years (2,190 Days)<br>**Max:** 7.0 Years (2,555 Days) | **Min:** 6 Years (2,190 Days)<br>**Max:** 6.5 Years (2,372 Days) |
| **4. Disposal Method** | Automated GCS Object Lifecycle Deletion (`age = 2190`) | Automated GCS Object Lifecycle Deletion (`age = 2190`) | Automated GCS Object Lifecycle Deletion (`age = 2190`) |
| **5. Data Residency** | `us-central1` (Iowa, USA) | `us-central1` (Iowa, USA) | `us-central1` (Iowa, USA) |
| **6. Encryption / Key Model** | Google-Managed Default KMS (AES-256 at rest) *(CMEK ready)* | Google-Managed Default KMS (AES-256 at rest) *(CMEK ready)* | Google-Managed Default KMS (AES-256 at rest) *(CMEK ready)* |
| **7. Approved Processors** | • Appraiso Cloud Run Backend<br>• Vertex AI Gemini (Summarization & QA) | • Appraiso Cloud Run Backend<br>• BigQuery Data Warehouse<br>• MSXI Dealer Reporting Portal | • Appraiso Cloud Run Backend<br>• Vertex AI Multimodal Gemini (Inspection analysis)<br>• Ingestion Worker |

---

## 3. Technical Security Controls Enforced (GCP Benchmarks)

Each bucket is provisioned with the following mandatory security controls:

1. **Uniform Bucket-Level Access (CIS GCP 5.2):**
   - **Status:** `ENFORCED` (`true`)
   - **Rationale:** Disables legacy Object ACLs and centralizes permissions strictly under Google Cloud IAM.
2. **Public Access Prevention (CIS GCP 5.1):**
   - **Status:** `ENFORCED`
   - **Rationale:** Blocks any accidental or intentional exposure of bucket objects to `allUsers` or `allAuthenticatedUsers`.
3. **Automated Lifecycle Purge (CIS 3.1 Disposal):**
   - **Rule:** `Action: Delete` upon reaching `Age: 2190 Days` (6-year working assumption).
   - **Rationale:** Ensures automated data disposal without requiring manual auditor intervention.
4. **Metadata Labeling (CIS 3.1 Traceability):**
   - Each bucket is tagged with:
     ```yaml
     record_owner: "msxi-data-governance"
     technical_custodian: "miracle"
     system_of_record: "<bucket-system-id>"
     data_classification: "confidential"
     retention_policy: "6-years"
     environment: "dev"
     ```

---

## 4. Formal Approval & Sign-Off Block

| Role | Name | Title | Date | Signature / Status |
| :--- | :--- | :--- | :--- | :--- |
| **Technical Implementation Lead** | Miracle | Appraiso Lead Cloud Engineer | 2026-10-22 | Verified & Implemented |
| **MSXI Data Governance Approver** | *[Pending]* | MSXI InfoSec / Data Protection Officer | *[Date]* | **Pending MSXI Decision** |
