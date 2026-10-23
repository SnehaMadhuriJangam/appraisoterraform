#!/usr/bin/env bash
# ==============================================================================
# CIS Controls v8.1 (Safeguards 3.2, 3.3, 3.4, 3.7) Validation Script
# Generates proof of compliance and exports machine-readable JSON evidence.
# ==============================================================================

# Stop on errors
set -e

# Check if Project ID is provided
if [ -z "$1" ]; then
  echo "Usage: ./validate_cis_buckets.sh <GCP_PROJECT_ID>"
  exit 1
fi

PROJECT_ID="$1"
TARGET_BUCKET="${2:-${PROJECT_ID}-appraiso-evidence-dev}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
EVIDENCE_FILE="CIS_3_Storage_Evidence_${TIMESTAMP}.json"
EVIDENCE_CSV="CIS_3_Storage_Evidence_${TIMESTAMP}.csv"

echo "=========================================================="
echo " Starting CIS Control Validation for Project: $PROJECT_ID"
echo "=========================================================="

# 1. Fetching bucket inventory with labels and security settings
echo "[*] Step 1: Generating Inventory & Access Configuration (CIS 3.2, 3.3, 3.7)..."
echo ""

gcloud storage buckets list \
  --project="$PROJECT_ID" \
  --format="table(
    name:label='BUCKET NAME',
    publicAccessPrevention:label='PUBLIC ACCESS PREV (CIS 3.3)',
    labels.public_access:label='PUBLIC ACCESS',
    labels.confidentiality_status:label='CONFIDENTIALITY (PUBLIC DISABLED = CONFIDENTIAL)',
    labels.category_id:label='CATEGORY (CIS 3.2)',
    labels.data_class:label='TIER (CIS 3.7)'
  )"

echo ""
echo "[*] Step 2: Validating Lifecycle Retention Rules (CIS 3.4)..."

# Filter only Appraiso buckets
BUCKETS=$(gcloud storage buckets list --project="$PROJECT_ID" --format="value(name)" | grep "appraiso" || true)

if [ -z "$BUCKETS" ]; then
  echo "[!] No 'appraiso' buckets found in project: $PROJECT_ID"
  exit 1
fi

for BUCKET in $BUCKETS; do
  echo "----------------------------------------------------------"
  echo "Lifecycle Rules for gs://${BUCKET}:"
  gcloud storage buckets describe "gs://${BUCKET}" --format="json(lifecycle.rule)"
done

echo ""
echo "[*] Step 3: Saving Full Machine-Readable JSON & CSV Evidence for Auditor..."
gcloud storage buckets list \
  --project="$PROJECT_ID" \
  --format="json(name, location, publicAccessPrevention, uniformBucketLevelAccess, labels, lifecycle)" > "$EVIDENCE_FILE"

gcloud storage buckets list \
  --project="$PROJECT_ID" \
  --format="csv(name:label='BUCKET_NAME', location:label='LOCATION', publicAccessPrevention:label='PUBLIC_ACCESS_PREVENTION_CIS_3_3', uniformBucketLevelAccess.enabled:label='UBLA_ENABLED_CIS_3_3', labels.category_id:label='CATEGORY_ID_CIS_3_2', labels.data_class:label='DATA_CLASS_CIS_3_7', labels.public_access:label='PUBLIC_ACCESS_TAG', labels.confidentiality_status:label='CONFIDENTIALITY_STATUS', labels.retention_period:label='RETENTION_PERIOD_CIS_3_4', labels.managed_by:label='MANAGED_BY')" > "$EVIDENCE_CSV"

# 4. Uploading Evidence to Secure Cloud Storage Bucket
echo ""
echo "[*] Step 4: Archiving Evidence to gs://${TARGET_BUCKET}/cis-evidence/ ..."
gcloud storage cp "$EVIDENCE_FILE" "$EVIDENCE_CSV" "gs://${TARGET_BUCKET}/cis-evidence/"
if [ -f "CIS_3_TECHNICAL_DATA_INVENTORY.csv" ]; then
  gcloud storage cp "CIS_3_TECHNICAL_DATA_INVENTORY.csv" "gs://${TARGET_BUCKET}/cis-evidence/"
fi

echo "=========================================================="
echo " Evidence files generated and archived successfully:"
echo "   Local JSON: $EVIDENCE_FILE"
echo "   Local CSV:  $EVIDENCE_CSV"
echo "   Cloud GCS:  gs://${TARGET_BUCKET}/cis-evidence/"
echo " You can attach these files directly to Review Items R01 & R03."
echo "=========================================================="
