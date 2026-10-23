# ==============================================================================
# CIS Controls v8.1 (Safeguards 3.2, 3.3, 3.4, 3.7) Validation Script (PowerShell)
# Generates proof of compliance and exports machine-readable JSON evidence.
# ==============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$ProjectId = ""
)

if (-not $ProjectId) {
    $ProjectId = (gcloud config get-value project 2>$null).Trim()
}

if (-not $ProjectId) {
    Write-Host "Usage: .\validate_cis_buckets.ps1 -ProjectId <GCP_PROJECT_ID>" -ForegroundColor Red
    exit 1
}

$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$EVIDENCE_FILE = "CIS_3_Storage_Evidence_${TIMESTAMP}.json"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting CIS Control Validation for Project: $ProjectId" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Fetching bucket inventory with labels and security settings
Write-Host "`n[*] Step 1: Generating Inventory & Access Configuration (CIS 3.2, 3.3, 3.7)..." -ForegroundColor Yellow
gcloud storage buckets list `
  --project="$ProjectId" `
  --format="table(name:label='BUCKET NAME', publicAccessPrevention:label='PUBLIC ACCESS PREV (CIS 3.3)', uniformBucketLevelAccess.enabled:label='UBLA ENABLED (CIS 3.3)', labels.category_id:label='CATEGORY (CIS 3.2)', labels.data_class:label='TIER (CIS 3.7)')"

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

# 3. Saving JSON Evidence
Write-Host "`n[*] Step 3: Saving Full Machine-Readable JSON Evidence for Auditor..." -ForegroundColor Yellow
gcloud storage buckets list `
  --project="$ProjectId" `
  --format="json(name, location, publicAccessPrevention, uniformBucketLevelAccess, labels, lifecycle)" | Out-File -FilePath "$EVIDENCE_FILE" -Encoding utf8

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " Evidence file generated successfully: $EVIDENCE_FILE" -ForegroundColor Green
Write-Host " You can attach this file directly to Review Items R01 & R03." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
