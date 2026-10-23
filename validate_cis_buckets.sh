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
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
EVIDENCE_FILE="CIS_3_Storage_Evidence_${TIMESTAMP}.json"

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
    uniformBucketLevelAccess.enabled:label='UBLA ENABLED (CIS 3.3)',
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
echo "[*] Step 3: Saving Full Machine-Readable JSON Evidence for Auditor..."
gcloud storage buckets list \
  --project="$PROJECT_ID" \
  --format="json(name, location, publicAccessPrevention, uniformBucketLevelAccess, labels, lifecycle)" > "$EVIDENCE_FILE"

echo "=========================================================="
echo " Evidence file generated successfully: $EVIDENCE_FILE"
echo " You can attach this file directly to Review Items R01 & R03."
echo "=========================================================="
