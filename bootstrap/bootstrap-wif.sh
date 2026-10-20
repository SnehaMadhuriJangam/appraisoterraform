#!/usr/bin/env bash
# =============================================================================
# Appraiso WIF Bootstrap Script (Bash)
# Sets up GCP Workload Identity Federation (WIF) for GitHub Actions & Terraform
# =============================================================================
set -euo pipefail

PROJECT_ID="newaiproject-510015"
REGION="us-central1"
GITHUB_REPO="SnehaMadhuriJangam/appraisoterraform"
POOL_ID="appraiso-msxi-wif"
PROVIDER_ID="github-oidc"
SA_NAME="appraiso-deployer"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
STATE_BUCKET="${PROJECT_ID}-tfstate"

echo "================================================================="
echo " Setting up GCP Workload Identity Federation for: ${GITHUB_REPO}"
echo " Target Project: ${PROJECT_ID} | Region: ${REGION}"
echo " Pool: ${POOL_ID} | SA: ${SA_EMAIL}"
echo "================================================================="

# 1. Set gcloud project
echo -e "\n>> [1/7] Setting active gcloud project to ${PROJECT_ID}..."
gcloud config set project "${PROJECT_ID}" >/dev/null
PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
echo "Project Number: ${PROJECT_NUMBER}"

# 2. Enable Required APIs
echo -e "\n>> [2/7] Enabling necessary GCP APIs..."
gcloud services enable \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  cloudresourcemanager.googleapis.com \
  serviceusage.googleapis.com \
  storage.googleapis.com \
  run.googleapis.com

# 3. Create Terraform State Bucket
echo -e "\n>> [3/7] Ensuring Terraform remote state bucket exists (gs://${STATE_BUCKET})..."
if ! gcloud storage buckets describe "gs://${STATE_BUCKET}" >/dev/null 2>&1; then
  gcloud storage buckets create "gs://${STATE_BUCKET}" --location="${REGION}" --uniform-bucket-level-access --public-access-prevention
  echo "Bucket created."
else
  echo "Bucket already exists."
fi
gcloud storage buckets update "gs://${STATE_BUCKET}" --versioning >/dev/null

# 4. Create Service Account
echo -e "\n>> [4/7] Ensuring Service Account exists (${SA_EMAIL})..."
gcloud iam service-accounts describe "${SA_EMAIL}" >/dev/null 2>&1 \
  || gcloud iam service-accounts create "${SA_NAME}" --display-name="Appraiso GitHub Actions Deployer"

# 5. Grant Roles to Service Account
echo -e "\n>> [5/7] Granting permissions to ${SA_EMAIL}..."
ROLES=(
  "roles/run.admin"
  "roles/iam.serviceAccountUser"
  "roles/storage.admin"
  "roles/serviceusage.serviceUsageAdmin"
)
for r in "${ROLES[@]}"; do
  echo "  Assigning role: ${r}"
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" --member="serviceAccount:${SA_EMAIL}" --role="${r}" --condition=None --quiet >/dev/null
done

gcloud storage buckets add-iam-policy-binding "gs://${STATE_BUCKET}" --member="serviceAccount:${SA_EMAIL}" --role="roles/storage.objectAdmin" --quiet >/dev/null

# 6. Create Workload Identity Pool & OIDC Provider
echo -e "\n>> [6/7] Creating Workload Identity Pool & GitHub OIDC Provider..."
gcloud iam workload-identity-pools describe "${POOL_ID}" --location=global >/dev/null 2>&1 \
  || gcloud iam workload-identity-pools create "${POOL_ID}" --location=global --display-name="Appraiso MSXI WIF"

ATTR_MAPPING="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner"
ATTR_CONDITION="assertion.repository == '${GITHUB_REPO}'"

if gcloud iam workload-identity-pools providers describe "${PROVIDER_ID}" --location=global --workload-identity-pool="${POOL_ID}" >/dev/null 2>&1; then
  gcloud iam workload-identity-pools providers update-oidc "${PROVIDER_ID}" \
    --location=global --workload-identity-pool="${POOL_ID}" \
    --attribute-mapping="${ATTR_MAPPING}" \
    --attribute-condition="${ATTR_CONDITION}" >/dev/null
else
  gcloud iam workload-identity-pools providers create-oidc "${PROVIDER_ID}" \
    --location=global --workload-identity-pool="${POOL_ID}" \
    --display-name="GitHub OIDC Provider" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="${ATTR_MAPPING}" \
    --attribute-condition="${ATTR_CONDITION}"
fi

# 7. Bind Service Account to GitHub Repo via WIF
echo -e "\n>> [7/7] Authorizing GitHub repo (${GITHUB_REPO}) to impersonate ${SA_EMAIL}..."
PRINCIPAL="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${GITHUB_REPO}"

gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="${PRINCIPAL}" \
  --quiet >/dev/null

WIF_PROVIDER_NAME="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"

echo
echo "================================================================================"
echo " SUCCESS! WIF Bootstrap Complete."
echo
echo " Add these 4 Variables in GitHub:"
echo " Repo -> Settings -> Secrets and variables -> Actions -> Variables"
echo "--------------------------------------------------------------------------------"
echo "GCP_PROJECT_ID         : ${PROJECT_ID}"
echo "GCP_REGION             : ${REGION}"
echo "GCP_WIF_PROVIDER       : ${WIF_PROVIDER_NAME}"
echo "GCP_SERVICE_ACCOUNT    : ${SA_EMAIL}"
echo "TF_STATE_BUCKET        : ${STATE_BUCKET}"
echo "--------------------------------------------------------------------------------"
echo "================================================================================"
