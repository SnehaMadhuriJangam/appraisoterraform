# =============================================================================
# Appraiso WIF Bootstrap Script (PowerShell)
# Sets up GCP Workload Identity Federation (WIF) for GitHub Actions & Terraform
# =============================================================================

# Configuration
$PROJECT_ID    = "newaiproject-510015"
$REGION        = "us-central1"
$GITHUB_REPO   = "SnehaMadhuriJangam/appraisoterraform"
$POOL_ID       = "appraiso-msxi-wif"
$PROVIDER_ID   = "github-oidc"
$SA_NAME       = "appraiso-deployer"
$SA_EMAIL      = "${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
$STATE_BUCKET  = "${PROJECT_ID}-tfstate"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " Setting up GCP Workload Identity Federation for: $GITHUB_REPO" -ForegroundColor Cyan
Write-Host " Target Project: $PROJECT_ID | Region: $REGION" -ForegroundColor Cyan
Write-Host " Pool: $POOL_ID | SA: $SA_EMAIL" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Set gcloud project
Write-Host "`n>> [1/7] Setting active gcloud project to $PROJECT_ID..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

$PROJECT_NUMBER = (gcloud projects describe $PROJECT_ID --format="value(projectNumber)").Trim()
Write-Host "Project Number: $PROJECT_NUMBER" -ForegroundColor Green

# 2. Enable Required APIs
Write-Host "`n>> [2/7] Enabling necessary GCP APIs..." -ForegroundColor Yellow
gcloud services enable `
    iam.googleapis.com `
    iamcredentials.googleapis.com `
    sts.googleapis.com `
    cloudresourcemanager.googleapis.com `
    serviceusage.googleapis.com `
    storage.googleapis.com `
    run.googleapis.com

# 3. Create Terraform State Bucket
Write-Host "`n>> [3/7] Ensuring Terraform remote state bucket exists (gs://$STATE_BUCKET)..." -ForegroundColor Yellow
$bucketCheck = (gcloud storage buckets list --filter="name:$STATE_BUCKET" --format="value(name)")
if (-not $bucketCheck) {
    Write-Host "Creating bucket gs://$STATE_BUCKET..."
    gcloud storage buckets create "gs://$STATE_BUCKET" --location=$REGION --uniform-bucket-level-access --public-access-prevention
    Write-Host "Bucket created." -ForegroundColor Green
} else {
    Write-Host "Bucket already exists." -ForegroundColor Green
}
gcloud storage buckets update "gs://$STATE_BUCKET" --versioning | Out-Null

# 4. Create Service Account
Write-Host "`n>> [4/7] Ensuring Service Account exists ($SA_EMAIL)..." -ForegroundColor Yellow
$saCheck = (gcloud iam service-accounts list --filter="email:$SA_EMAIL" --format="value(email)")
if (-not $saCheck) {
    Write-Host "Creating service account $SA_NAME..."
    gcloud iam service-accounts create $SA_NAME --display-name="Appraiso GitHub Actions Deployer"
    Write-Host "Service account created." -ForegroundColor Green
} else {
    Write-Host "Service account already exists." -ForegroundColor Green
}

# 5. Grant Roles to Service Account
Write-Host "`n>> [5/7] Granting permissions to $SA_EMAIL..." -ForegroundColor Yellow
$ROLES = @(
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/storage.admin",
    "roles/serviceusage.serviceUsageAdmin"
)

foreach ($r in $ROLES) {
    Write-Host "  Assigning role: $r"
    gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="$r" --condition=None --quiet | Out-Null
}

# Grant storage object admin to the state bucket specifically
gcloud storage buckets add-iam-policy-binding "gs://$STATE_BUCKET" --member="serviceAccount:$SA_EMAIL" --role="roles/storage.objectAdmin" --quiet | Out-Null

# 6. Create Workload Identity Pool & OIDC Provider
Write-Host "`n>> [6/7] Creating Workload Identity Pool & GitHub OIDC Provider..." -ForegroundColor Yellow
$poolCheck = (gcloud iam workload-identity-pools list --location="global" --filter="name:$POOL_ID" --format="value(name)")
if (-not $poolCheck) {
    Write-Host "Creating WIF pool $POOL_ID..."
    gcloud iam workload-identity-pools create $POOL_ID `
        --location="global" `
        --display-name="Appraiso MSXI WIF"
    Write-Host "WIF Pool '$POOL_ID' created." -ForegroundColor Green
} else {
    Write-Host "WIF Pool '$POOL_ID' already exists." -ForegroundColor Green
}

$ATTR_MAPPING = "google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner"
$ATTR_CONDITION = "assertion.repository == '$GITHUB_REPO'"

$providerCheck = (gcloud iam workload-identity-pools providers list --location="global" --workload-identity-pool=$POOL_ID --filter="name:$PROVIDER_ID" --format="value(name)")
if (-not $providerCheck) {
    Write-Host "Creating OIDC provider $PROVIDER_ID..."
    gcloud iam workload-identity-pools providers create-oidc $PROVIDER_ID `
        --location="global" `
        --workload-identity-pool=$POOL_ID `
        --display-name="GitHub OIDC Provider" `
        --issuer-uri="https://token.actions.githubusercontent.com" `
        --attribute-mapping=$ATTR_MAPPING `
        --attribute-condition=$ATTR_CONDITION
    Write-Host "WIF Provider '$PROVIDER_ID' created." -ForegroundColor Green
} else {
    Write-Host "Updating OIDC provider $PROVIDER_ID..."
    gcloud iam workload-identity-pools providers update-oidc $PROVIDER_ID `
        --location="global" `
        --workload-identity-pool=$POOL_ID `
        --attribute-mapping=$ATTR_MAPPING `
        --attribute-condition=$ATTR_CONDITION
    Write-Host "WIF Provider '$PROVIDER_ID' updated." -ForegroundColor Green
}

# 7. Bind Service Account to GitHub Repo via WIF
Write-Host "`n>> [7/7] Authorizing GitHub repo ($GITHUB_REPO) to impersonate $SA_EMAIL..." -ForegroundColor Yellow
$PRINCIPAL = "principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_ID/attribute.repository/$GITHUB_REPO"

gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL `
    --role="roles/iam.workloadIdentityUser" `
    --member="$PRINCIPAL" `
    --quiet | Out-Null

# Retrieve outputs
$WIF_PROVIDER_NAME = "projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_ID/providers/$PROVIDER_ID"

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host " SUCCESS! WIF Bootstrap Complete." -ForegroundColor Green
Write-Host "`n Add these 5 Variables in GitHub:" -ForegroundColor Yellow
Write-Host " Repo -> Settings -> Secrets and variables -> Actions -> Variables" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "GCP_PROJECT_ID         : $PROJECT_ID"
Write-Host "GCP_REGION             : $REGION"
Write-Host "GCP_WIF_PROVIDER       : $WIF_PROVIDER_NAME"
Write-Host "GCP_SERVICE_ACCOUNT    : $SA_EMAIL"
Write-Host "TF_STATE_BUCKET        : $STATE_BUCKET"
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
