# ==============================================================================
# CIS Controls v8.1 (Safeguards 3.2, 3.3, 3.4, 3.7) Validation Script (PowerShell)
# Generates proof of compliance and exports machine-readable JSON evidence.
# ==============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$ProjectId = "",

    [Parameter(Mandatory=$false)]
    [string]$TargetBucket = ""
)

if (-not $ProjectId) {
    $ProjectId = (gcloud config get-value project 2>$null).Trim()
}

if (-not $TargetBucket) {
    $TargetBucket = "${ProjectId}-appraiso-evidence-dev"
}

if (-not $ProjectId) {
    Write-Host "Usage: .\validate_cis_buckets.ps1 -ProjectId <GCP_PROJECT_ID>" -ForegroundColor Red
    exit 1
}

$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$EVIDENCE_FILE = "CIS_3_Storage_Evidence_${TIMESTAMP}.json"
$EVIDENCE_CSV = "CIS_3_Storage_Evidence_${TIMESTAMP}.csv"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting CIS Control Validation for Project: $ProjectId" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Fetching bucket inventory with labels and security settings
Write-Host "`n[*] Step 1: Generating Inventory & Access Configuration (CIS 3.2, 3.3, 3.7)..." -ForegroundColor Yellow
gcloud storage buckets list `
  --project="$ProjectId" `
  --format="table(name:label='BUCKET NAME', publicAccessPrevention:label='PUBLIC ACCESS PREV (CIS 3.3)', labels.public_access:label='PUBLIC ACCESS', labels.confidentiality_status:label='CONFIDENTIALITY (PUBLIC DISABLED = CONFIDENTIAL)', labels.category_id:label='CATEGORY (CIS 3.2)', labels.data_class:label='TIER (CIS 3.7)')"

# 2. Validating Lifecycle Retention Rules
Write-Host "`n[*] Step 2: Validating Lifecycle Retention Rules (CIS 3.4)..." -ForegroundColor Yellow

$BUCKETS = (gcloud storage buckets list --project="$ProjectId" --format="value(name)" | Select-String "appraiso")

if (-not $BUCKETS) {
    Write-Host "[!] No 'appraiso' buckets found in project: $ProjectId" -ForegroundColor Red
    exit 1
}

foreach ($b in $BUCKETS) {
    $bucketName = $b.ToString().Trim()
    Write-Host "----------------------------------------------------------" -ForegroundColor Gray
    Write-Host "Lifecycle Rules for gs://${bucketName}:" -ForegroundColor Green
    gcloud storage buckets describe "gs://${bucketName}" --format="json(lifecycle.rule)"
}

# 3. Saving JSON & CSV Evidence
Write-Host "`n[*] Step 3: Saving Full Machine-Readable JSON & CSV Evidence for Auditor..." -ForegroundColor Yellow
gcloud storage buckets list `
  --project="$ProjectId" `
  --format="json(name, location, publicAccessPrevention, uniformBucketLevelAccess, labels, lifecycle)" | Out-File -FilePath "$EVIDENCE_FILE" -Encoding utf8

gcloud storage buckets list `
  --project="$ProjectId" `
  --format="csv(name:label='BUCKET_NAME', location:label='LOCATION', publicAccessPrevention:label='PUBLIC_ACCESS_PREVENTION_CIS_3_3', uniformBucketLevelAccess.enabled:label='UBLA_ENABLED_CIS_3_3', labels.category_id:label='CATEGORY_ID_CIS_3_2', labels.data_class:label='DATA_CLASS_CIS_3_7', labels.public_access:label='PUBLIC_ACCESS_TAG', labels.confidentiality_status:label='CONFIDENTIALITY_STATUS', labels.retention_period:label='RETENTION_PERIOD_CIS_3_4', labels.managed_by:label='MANAGED_BY')" | Out-File -FilePath "$EVIDENCE_CSV" -Encoding utf8

# 4. Uploading Evidence to Secure Cloud Storage Bucket
Write-Host "`n[*] Step 4: Archiving Evidence to gs://${TargetBucket}/cis-evidence/ ..." -ForegroundColor Yellow
gcloud storage cp "$EVIDENCE_FILE" "$EVIDENCE_CSV" "gs://${TargetBucket}/cis-evidence/"
if (Test-Path "CIS_3_TECHNICAL_DATA_INVENTORY.csv") {
    gcloud storage cp "CIS_3_TECHNICAL_DATA_INVENTORY.csv" "gs://${TargetBucket}/cis-evidence/"
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " Evidence files generated and archived successfully:" -ForegroundColor Green
Write-Host "   Local JSON: $EVIDENCE_FILE" -ForegroundColor Green
Write-Host "   Local CSV:  $EVIDENCE_CSV" -ForegroundColor Green
Write-Host "   Cloud GCS:  gs://${TargetBucket}/cis-evidence/" -ForegroundColor Green
Write-Host " You can attach these files directly to Review Items R01 & R03." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
