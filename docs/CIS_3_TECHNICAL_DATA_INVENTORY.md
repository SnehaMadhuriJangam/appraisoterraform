# CIS Controls v8.1 — Technical Data Inventory & Mapping (CIS 3.2, 3.3, 3.4, 3.7)

**Document Purpose:** Connects Appraiso Data Classification IDs (`DC-xx`) directly to live Google Cloud Platform (GCP) resources, Terraform resource addresses, access controls, and retention lifecycle rules.

---

## 1. Technical Data Inventory Table

| Category ID | Data Category | Classification (CIS 3.7) | Actual GCP Resource Name (PROD / DEV) | Terraform Resource Address | Retention Rule (CIS 3.4) | Access & Security Locks (CIS 3.3) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DC-01** | **Video & Photo Evidence** | **Confidential** | `gs://${PROJECT_ID}-appraiso-evidence-${ENV}` | `google_storage_bucket.evidence_bucket` | Delete after 365 days (`days_since_custom_time = 365`) + Version cleanup 30d | `uniform_bucket_level_access = true`<br>`public_access_prevention = "enforced"` |
| **DC-04** | **Appraisal Metadata** | **Confidential** | Cloud SQL: `appraiso-${ENV}-db` (Tables: `Appraisals`, `Jobs`, `Audit Details`) | `google_sql_database_instance.main` | 30 days PITR / Scheduled purge after 1–6 years | Private IP only, Enforced SSL, SQL TDE |
| **DC-05** | **AI Vector Embeddings** | **Confidential** | Compute Engine: `qdrant-${ENV}-vm` (Collections: `smart_audit_collection`, etc.) | `google_compute_instance.qdrant` | Cascade purge via Cloud Run API (Synchronized with audit) | Encrypted Persistent Disk, Internal VPC only |
| **DC-08** | **Runtime Secrets** | **Restricted** | Secret Manager: `appraiso-${ENV}-*` | `google_secret_manager_secret.*` | Destroy on 90-day rotation schedule | Google-managed KMS (AES-256), Least-privilege IAM |
| **DC-12** | **Quarantine Files** | **Confidential** | `gs://${PROJECT_ID}-appraiso-quarantine-${ENV}` | `google_storage_bucket.quarantine_bucket` | Auto-delete after 30 days (`age = 30`) | `uniform_bucket_level_access = true`<br>`public_access_prevention = "enforced"` |
| **DC-21** | **OEM Brand & Program Logos** | **Public** | `gs://${PROJECT_ID}-appraiso-static-assets-${ENV}` | `google_storage_bucket.assets` | Retain during active program lifetime | `uniform_bucket_level_access = true` |

---

## 2. CIS Control Mapping & Safeguard Matrix

| CIS Safeguard | Requirement | How Appraiso Solves It in GCP & Terraform |
| :--- | :--- | :--- |
| **CIS 3.2** | **Establish and Maintain a Data Inventory** | Every storage bucket and database resource is tagged with `labels = { category_id = "dc-xx", managed_by = "terraform" }`. |
| **CIS 3.3** | **Configure Data Access Control Lists** | All buckets strictly enforce `uniform_bucket_level_access = true` and `public_access_prevention = "enforced"` making public internet leakage mathematically impossible. |
| **CIS 3.4** | **Enforce Data Retention** | Automated `lifecycle_rule` blocks enforce exact disposal without manual operator intervention: 365 days for Evidence (DC-01) and 30 days for Quarantine (DC-12). |
| **CIS 3.7** | **Establish a Data Classification Scheme** | Every resource is tagged with `labels = { data_class = "confidential" }` matching the corporate 4-tier classification scheme. |

---

## 3. How to Execute & Prove Compliance to Auditors

### Step 1: Deploy Storage Buckets with Terraform
```bash
cd infra
terraform init
terraform plan -var="project_id=YOUR_PROJECT_ID" -var="environment=dev"
terraform apply -var="project_id=YOUR_PROJECT_ID" -var="environment=dev" -auto-approve
```

### Step 2: Run the Automated Validation Script
- **In Cloud Shell / Linux:**
  ```bash
  chmod +x validate_cis_buckets.sh
  ./validate_cis_buckets.sh YOUR_PROJECT_ID
  ```
- **In Windows PowerShell:**
  ```powershell
  .\validate_cis_buckets.ps1 -ProjectId YOUR_PROJECT_ID
  ```

### Step 3: Auditor Artifact Generated
The script automatically exports a timestamped file:
`CIS_3_Storage_Evidence_YYYYMMDD_HHMMSS.json`

Attach this machine-readable evidence directly to your compliance review tracker to transition from **Planned** to **Pass**.
