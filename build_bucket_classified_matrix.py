#!/usr/bin/env python3
"""
Storage Bucket Classified Matrix Generator
Maps every bucket from npd.txt, qa.txt, and prod.txt to:
- CIS Controls v8.1 (Safeguards 3.2, 3.3, 3.4, 3.7, 3.11, 3.13)
- MSXI_Appraiso_Data_Classification_Register_v1.2_updated.docx (Section 6 Data Category Register)
"""

import os
import csv
import zipfile
import xml.etree.ElementTree as ET

DOCX_FILE = "MSXI_Appraiso_Data_Classification_Register_v1.2_updated.docx"
OUTPUT_CSV = "STORAGE_BUCKETS_CLASSIFIED_MATRIX.csv"

# 1. Parse Word Document Section 6 Tables (Table 5 & Table 7)
def extract_docx_categories(docx_path):
    dc_meta = {}
    if not os.path.exists(docx_path):
        return dc_meta

    with zipfile.ZipFile(docx_path) as z:
        xml_content = z.read("word/document.xml")

    root = ET.fromstring(xml_content)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    tables = root.findall(".//w:tbl", ns)
    
    if len(tables) < 8:
        return dc_meta

    # Table 5 is Primary Classification Record
    tbl5 = tables[5]
    for r in tbl5.findall(".//w:tr", ns)[1:]:
        cells = [" ".join("".join(c.itertext()).split()) for c in r.findall(".//w:tc", ns)]
        if cells and len(cells) >= 9:
            cid = cells[0].strip()
            dc_meta[cid] = {
                "Category ID": cid,
                "Data Category": cells[1],
                "Description": cells[2],
                "Storage Location": cells[3],
                "Classification Tier": cells[4],
                "Contains Personal Data": cells[5],
                "Legal Basis": cells[6],
                "Retention Period": cells[7],
                "Retention Trigger": cells[8],
                "Data Owner Decision": cells[9] if len(cells) > 9 else "",
                "ISC Notes": cells[10] if len(cells) > 10 else "",
                "DLP Feasible": "No",
                "DLP Approach": "N/A"
            }

    # Table 7 is DLP Coverage Determination
    tbl7 = tables[7]
    for r in tbl7.findall(".//w:tr", ns)[1:]:
        cells = [" ".join("".join(c.itertext()).split()) for c in r.findall(".//w:tc", ns)]
        if cells and len(cells) >= 4:
            cid = cells[0].strip()
            if cid in dc_meta:
                dc_meta[cid]["DLP Feasible"] = cells[2]
                dc_meta[cid]["DLP Approach"] = cells[3]

    return dc_meta

# 2. Comprehensive Bucket Raw Catalog from npd.txt, qa.txt, prod.txt + CIS Deployed
RAW_BUCKET_ENTRIES = [
    # ==================== NPD ENVIRONMENT (npd.txt) ====================
    {
        "env": "NPD",
        "bucket": "action-item-narratives",
        "cid": "DC-34",
        "alt_cid": "DC-37",
        "user_purpose": "action item evidences (media, images)",
        "scope_status": "Active Data Store",
        "formats": "media, images, notes",
        "link": "Referenced by Cloud SQL AI Analysis Details and Action Item tables",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "appraiso_audit_reports",
        "cid": "DC-21",
        "alt_cid": "DC-17",
        "user_purpose": "programme based logos & official reports",
        "scope_status": "Active Data Store",
        "formats": "images, png, jpg, pdf",
        "link": "Referenced by Dealer Portal header and PDF report compilation",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "appraiso_dev_reference_documents",
        "cid": "DC-14",
        "alt_cid": "DC-15",
        "user_purpose": "programme based guided docs (all extensions)",
        "scope_status": "Active Data Store",
        "formats": "pdf, docx, xlsx, txt",
        "link": "Source origin for appraiso_dev_reference_collection in Qdrant Vector DB",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "audit_signed_bucket",
        "cid": "DC-17",
        "alt_cid": "DC-37",
        "user_purpose": "digital signatures, audit reports of an audit",
        "scope_status": "Active Data Store",
        "formats": "images, pdfs, digital signatures",
        "link": "Compiled from Cloud SQL audit details and signed by dealership auditor",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "daf_documents",
        "cid": "DC-14",
        "alt_cid": "DC-15",
        "user_purpose": "poc - guided docs of daf programme",
        "scope_status": "Active Data Store",
        "formats": "pdfs, criteria documents",
        "link": "Metadata indexed in Cloud SQL reference_metadata and Qdrant DAF collection",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "ford_italy_documents",
        "cid": "DC-14",
        "alt_cid": "DC-15",
        "user_purpose": "poc - guided docs of ford italy",
        "scope_status": "Active Data Store",
        "formats": "pdfs, standards checklists",
        "link": "Source origin for Ford_Italy_Collection in Qdrant Vector DB",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "pre_audit_document_zone_files",
        "cid": "DC-37",
        "alt_cid": "DC-27",
        "user_purpose": "R1 - storing documents for pre audit zones",
        "scope_status": "Active Data Store",
        "formats": "all extensions, pdfs, images",
        "link": "Linked to Cloud SQL Zones Table and Instruction checklists",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "smart-audit-multimedia-dev",
        "cid": "DC-01",
        "alt_cid": "DC-33",
        "user_purpose": "poc + r1 - evidences under zonal instructions (all extensions)",
        "scope_status": "Active Data Store",
        "formats": "mp4, mov, jpg, png, audio",
        "link": "Direct gs:// URLs stored in Cloud SQL Bucket Evidence URLs Table and Qdrant smart_audit_collection",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "smart-audit-report",
        "cid": "DC-17",
        "alt_cid": "DC-16",
        "user_purpose": "poc - pdf, excel -poc - reports",
        "scope_status": "Active Data Store",
        "formats": "pdfs, excels, scorecards",
        "link": "Generated from Cloud SQL audit evaluations for MSX dealer scoring",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "volvo_documents",
        "cid": "DC-14",
        "alt_cid": "DC-15",
        "user_purpose": "poc - guided docs for volvo",
        "scope_status": "Active Data Store",
        "formats": "pdfs, OEM criteria",
        "link": "Volvo OEM audit criteria repository indexed in Cloud SQL",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "volvo_documents_new",
        "cid": "DC-14",
        "alt_cid": "DC-15",
        "user_purpose": "poc - updated guided docs for volvo",
        "scope_status": "Active Data Store",
        "formats": "pdfs, updated criteria",
        "link": "Source origin for volvo_collection_new in Qdrant Vector DB",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "amiimport",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "AMI import staging (ignore)",
        "scope_status": "System Buffer / Migration Staging",
        "formats": "disk images, tar.gz",
        "link": "Used by GCP Compute Engine migration service",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "appraiso-npd-logs",
        "cid": "DC-09",
        "alt_cid": "DC-09",
        "user_purpose": "NPD logging bucket (ignore)",
        "scope_status": "Audit Telemetry Store",
        "formats": "log files, json telemetry",
        "link": "Google Cloud Logging export sink for NPD infrastructure",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "asset-report-smart-audit-engine-npd",
        "cid": "DC-16",
        "alt_cid": "DC-16",
        "user_purpose": "Asset inventory report export (ignore)",
        "scope_status": "Operational Staging",
        "formats": "json, csv reports",
        "link": "Cloud Asset Inventory periodic report dumps",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "assetsinventory",
        "cid": "DC-16",
        "alt_cid": "DC-16",
        "user_purpose": "Asset inventory temp files (ignore)",
        "scope_status": "Operational Staging",
        "formats": "data, json",
        "link": "Internal inventory staging buffer",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "classificationdocuments",
        "cid": "DC-14",
        "alt_cid": "DC-37",
        "user_purpose": "Deprecated classification store (delete)",
        "scope_status": "Decommissioned / Pending Purge",
        "formats": "docs, legacy templates",
        "link": "Scheduled for removal per decommissioning procedure",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "cloud-ai-platform-71842770-be8c-4e6c-89be-583387782044",
        "cid": "DC-06",
        "alt_cid": "DC-06",
        "user_purpose": "Managed Vertex AI temp bucket (ignore)",
        "scope_status": "System Staging Buffer",
        "formats": "temp artifacts, model checkpoints",
        "link": "Managed by Google Vertex AI training & pipeline service",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "npdqdrant-backup",
        "cid": "DC-11",
        "alt_cid": "DC-11",
        "user_purpose": "Qdrant vector backup snapshots (ignore)",
        "scope_status": "Backup & Disaster Recovery",
        "formats": "snapshots, tar.gz",
        "link": "Automated snapshot backup store for NPD Qdrant Vector DB VM",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "qdrant-migration-bucket",
        "cid": "DC-11",
        "alt_cid": "DC-11",
        "user_purpose": "Qdrant migration staging (ignore)",
        "scope_status": "System Staging Buffer",
        "formats": "migration chunks, tar.gz",
        "link": "Vector collection point migration buffer",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "r1appraisosql",
        "cid": "DC-10",
        "alt_cid": "DC-10",
        "user_purpose": "SQL export staging (ignore)",
        "scope_status": "Database Export Staging",
        "formats": "bak, sql exports",
        "link": "Manual database migration exports from Cloud SQL",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "run-sources-smart-audit-engine-npd-europe-west1",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "Cloud Run build source artifacts (ignore)",
        "scope_status": "Build Pipeline Artifacts",
        "formats": "tar.gz source code",
        "link": "Injected by Google Cloud Build during NPD container compilation",
        "residency": "europe-west1"
    },
    {
        "env": "NPD",
        "bucket": "run-sources-smart-audit-engine-npd-us-east1",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "Cloud Run build source artifacts (ignore)",
        "scope_status": "Build Pipeline Artifacts",
        "formats": "tar.gz source code",
        "link": "Injected by Google Cloud Build during NPD container compilation",
        "residency": "us-east1"
    },
    {
        "env": "NPD",
        "bucket": "smart-audit-engine-npd-cloud-asset-inventory",
        "cid": "DC-16",
        "alt_cid": "DC-16",
        "user_purpose": "Cloud Asset Inventory exports (ignore)",
        "scope_status": "Operational Staging",
        "formats": "cai json dumps",
        "link": "GCP Cloud Asset Inventory scheduled export destination",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "smart-audit-engine-npd-daisy-bkt-europe-west3",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "Daisy image build worker bucket (ignore)",
        "scope_status": "Build Pipeline Artifacts",
        "formats": "daisy scratch files",
        "link": "Used by GCP Compute Engine Daisy disk imaging workflow",
        "residency": "europe-west3"
    },
    {
        "env": "NPD",
        "bucket": "smart-audit-engine-npd-daisy-bkt-us",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "Daisy image build worker bucket (ignore)",
        "scope_status": "Build Pipeline Artifacts",
        "formats": "daisy scratch files",
        "link": "Used by GCP Compute Engine Daisy disk imaging workflow",
        "residency": "us"
    },
    {
        "env": "NPD",
        "bucket": "smart-audit-engine-npd-sql-bucket",
        "cid": "DC-10",
        "alt_cid": "DC-10",
        "user_purpose": "SQL backup bucket (ignore)",
        "scope_status": "Backup & Disaster Recovery",
        "formats": "bak, sql dumps",
        "link": "Automated Cloud SQL instance backup staging destination",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "smart-audit-engine-npd_cloudbuild",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "Cloud Build artifacts (ignore)",
        "scope_status": "Build Pipeline Artifacts",
        "formats": "build logs, tar.gz",
        "link": "Managed by Google Cloud Build CI/CD service",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "sql-server-audit-files",
        "cid": "DC-09",
        "alt_cid": "DC-09",
        "user_purpose": "SQL Server native audit logs (ignore)",
        "scope_status": "Audit Telemetry Store",
        "formats": "sqlaudit binary log files",
        "link": "Destination for Cloud SQL Server Server Audit Specifications",
        "residency": "us-central1"
    },
    {
        "env": "NPD",
        "bucket": "testnew_bucket",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "Testing bucket (ignore)",
        "scope_status": "Temporary Scratch Store",
        "formats": "test files",
        "link": "Dev testing scratch space",
        "residency": "us-central1"
    },

    # ==================== QA ENVIRONMENT (qa.txt) ====================
    {
        "env": "QA",
        "bucket": "action-item-narratives-qa",
        "cid": "DC-34",
        "alt_cid": "DC-37",
        "user_purpose": "store files under actionitems (img, doc extensions)",
        "scope_status": "Active Data Store",
        "formats": "img, doc extensions, media",
        "link": "Referenced by QA Cloud SQL AI Analysis Details and Action Item tables",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "appraiso-msxi-eu-archive-bucket-qa",
        "cid": "DC-17",
        "alt_cid": "DC-37",
        "user_purpose": "EU archive bucket for QA (ignore)",
        "scope_status": "Archive Store",
        "formats": "archived audit bundles",
        "link": "Staging for European audit historical archiving test cases",
        "residency": "europe-west3"
    },
    {
        "env": "QA",
        "bucket": "appraiso-qa-cloud-sql-data-01-10-2026",
        "cid": "DC-10",
        "alt_cid": "DC-10",
        "user_purpose": "Cloud SQL data snapshot (ignore)",
        "scope_status": "Backup & Disaster Recovery",
        "formats": "sql dump, bak",
        "link": "Baseline data seed snapshot for QA database restoration",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "appraiso_audit_reports_qa",
        "cid": "DC-21",
        "alt_cid": "DC-17",
        "user_purpose": "logos for a program (img extensions)",
        "scope_status": "Active Data Store",
        "formats": "img extensions, logos, png",
        "link": "QA static assets displayed in dealer portal and scorecards",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "appraiso_qa_reference_documents",
        "cid": "DC-14",
        "alt_cid": "DC-15",
        "user_purpose": "guided doc of a specified program (doc extensions)",
        "scope_status": "Active Data Store",
        "formats": "doc extensions, pdf, docx",
        "link": "Source origin for QA reference document evaluation in Qdrant",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "audit_signed_bucket_qa",
        "cid": "DC-17",
        "alt_cid": "DC-37",
        "user_purpose": "storing digital signatures and report for an audit (pdf, img)",
        "scope_status": "Active Data Store",
        "formats": "pdf, image extensions, signatures",
        "link": "QA signed audit certificates and auditor signatures",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "daf_documents_qa",
        "cid": "DC-14",
        "alt_cid": "DC-15",
        "user_purpose": "poc - guided doc of DAF program (pdfs)",
        "scope_status": "Active Data Store",
        "formats": "pdfs, criteria documents",
        "link": "DAF QA standards repository linked to QA Cloud SQL",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "ford_italy_documents_qa",
        "cid": "DC-14",
        "alt_cid": "DC-15",
        "user_purpose": "poc - guided doc of ford italy (pdfs)",
        "scope_status": "Active Data Store",
        "formats": "pdfs, checklists",
        "link": "Source origin for Ford_Italy_qa_Collection in Qdrant Vector DB",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "pre_audit_document_zone_files_qa",
        "cid": "DC-37",
        "alt_cid": "DC-27",
        "user_purpose": "audit files that are under doc zone (all extensions)",
        "scope_status": "Active Data Store",
        "formats": "all extensions, pdfs, images",
        "link": "Pre-audit zonal document verification files for QA audits",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "qa_qdrantbackupfiles",
        "cid": "DC-11",
        "alt_cid": "DC-11",
        "user_purpose": "Qdrant vector backup files (ignore)",
        "scope_status": "Backup & Disaster Recovery",
        "formats": "snapshots, tar.gz",
        "link": "QA Qdrant snapshot backup archive",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "qdrant-migration-bucket-qa",
        "cid": "DC-11",
        "alt_cid": "DC-11",
        "user_purpose": "Qdrant migration bucket for QA (ignore)",
        "scope_status": "System Staging Buffer",
        "formats": "migration chunks",
        "link": "QA vector migration staging",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "run-sources-smart-audit-engine-qa-us-east1",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "Cloud Run build source artifacts (ignore)",
        "scope_status": "Build Pipeline Artifacts",
        "formats": "tar.gz source code",
        "link": "Injected by Google Cloud Build during QA container deployment",
        "residency": "us-east1"
    },
    {
        "env": "QA",
        "bucket": "smart-audit-engine-dev-sql-backup-files",
        "cid": "DC-10",
        "alt_cid": "DC-10",
        "user_purpose": "SQL backup files for dev/qa (ignore)",
        "scope_status": "Backup & Disaster Recovery",
        "formats": "bak, sql dumps",
        "link": "Cross-environment database restore staging",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "smart-audit-engine-qa-daisy-bkt-europe-west3",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "Daisy image build worker bucket (ignore)",
        "scope_status": "Build Pipeline Artifacts",
        "formats": "daisy scratch files",
        "link": "Used by GCP Compute Engine Daisy disk imaging workflow",
        "residency": "europe-west3"
    },
    {
        "env": "QA",
        "bucket": "smart-audit-multimedia-qa",
        "cid": "DC-01",
        "alt_cid": "DC-33",
        "user_purpose": "evidences under zone based instructions (all extensions)",
        "scope_status": "Active Data Store",
        "formats": "mp4, mov, jpg, png, audio",
        "link": "QA audit inspection evidence linked to QA Cloud SQL and Qdrant smart_audit_collection",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "smart-audit-qa-sqlfiles-export",
        "cid": "DC-10",
        "alt_cid": "DC-10",
        "user_purpose": "SQL files export bucket (ignore)",
        "scope_status": "Database Export Staging",
        "formats": "bak, bcp, sql",
        "link": "Automated data export staging for QA testing",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "smart-audit-report-qa",
        "cid": "DC-17",
        "alt_cid": "DC-16",
        "user_purpose": "reports - pdfs - report of audits",
        "scope_status": "Active Data Store",
        "formats": "pdfs, excels",
        "link": "QA compiled final audit reports",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "sql-server-audit-files-qa",
        "cid": "DC-09",
        "alt_cid": "DC-09",
        "user_purpose": "SQL Server audit log files (ignore)",
        "scope_status": "Audit Telemetry Store",
        "formats": "sqlaudit log files",
        "link": "QA Cloud SQL Server security audit trail",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "test_new_qa",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "QA test bucket (ignore)",
        "scope_status": "Temporary Scratch Store",
        "formats": "test data",
        "link": "QA engineer testing scratch buffer",
        "residency": "us-central1"
    },
    {
        "env": "QA",
        "bucket": "volvo_documents_qa",
        "cid": "DC-14",
        "alt_cid": "DC-15",
        "user_purpose": "poc - guided doc under volvo (pdfs)",
        "scope_status": "Active Data Store",
        "formats": "pdfs, guidelines",
        "link": "Source origin for volvo_qa_collection in Qdrant Vector DB",
        "residency": "us-central1"
    },

    # ==================== PROD ENVIRONMENT (prod.txt) ====================
    {
        "env": "PROD",
        "bucket": "audit_signed_bucket_prd",
        "cid": "DC-17",
        "alt_cid": "DC-37",
        "user_purpose": "storing audit reports and digital signature for an audit",
        "scope_status": "Active Data Store",
        "formats": "pdfs, img extensions, signatures",
        "link": "Official production signed audit certificates and compliance records",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "daf_documents_prod",
        "cid": "DC-14",
        "alt_cid": "DC-15",
        "user_purpose": "guided doc of DAF program (pdf)",
        "scope_status": "Active Data Store",
        "formats": "pdf, criteria documents",
        "link": "Authoritative production DAF inspection criteria store",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "ford_italy_documents_prod",
        "cid": "DC-14",
        "alt_cid": "DC-15",
        "user_purpose": "guided doc of ford italy (pdf)",
        "scope_status": "Active Data Store",
        "formats": "pdf, standard manuals",
        "link": "Source origin for Ford_Italy_Collection in production Qdrant Vector DB",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "smart-audit-multimedia-prod",
        "cid": "DC-01",
        "alt_cid": "DC-33",
        "user_purpose": "stored evidences under a zone based instruction (all extensions)",
        "scope_status": "Active Data Store",
        "formats": "mp4, mov, jpg, png, audio",
        "link": "Production audit multimedia evidence linked to Cloud SQL Bucket Evidence URLs Table and Qdrant smart_audit_collection",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "smart-audit-report-prod",
        "cid": "DC-17",
        "alt_cid": "DC-16",
        "user_purpose": "used to store audit reports (pdf | excels)",
        "scope_status": "Active Data Store",
        "formats": "pdf, excels, scorecards",
        "link": "Production certified audit scorecards and dealer compliance reports",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "volvo_documents_prod",
        "cid": "DC-14",
        "alt_cid": "DC-15",
        "user_purpose": "guided doc of volvo program (pdf)",
        "scope_status": "Active Data Store",
        "formats": "pdf, standard manuals",
        "link": "Source origin for volvo_collection_new in production Qdrant Vector DB",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "assist-prod-backup-audit-responses",
        "cid": "DC-10",
        "alt_cid": "DC-04",
        "user_purpose": "Backup audit responses (ignore)",
        "scope_status": "Backup & Disaster Recovery",
        "formats": "backup archives, json",
        "link": "Secondary backup snapshot store for completed audit responses",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "classificationdocuments-prod",
        "cid": "DC-14",
        "alt_cid": "DC-37",
        "user_purpose": "Deprecated classification store (ignore)",
        "scope_status": "Decommissioned / Pending Purge",
        "formats": "docs, legacy templates",
        "link": "Scheduled for removal per decommissioning procedure",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "cloud-ai-platform-bbcb2060-4678-4a38-93fe-57bf255d425f",
        "cid": "DC-06",
        "alt_cid": "DC-06",
        "user_purpose": "Managed Vertex AI temp bucket (ignore)",
        "scope_status": "System Staging Buffer",
        "formats": "temp artifacts, model checkpoints",
        "link": "Managed by Google Vertex AI production service",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "prod-qdrant-backup",
        "cid": "DC-11",
        "alt_cid": "DC-11",
        "user_purpose": "Qdrant production backup (ignore)",
        "scope_status": "Backup & Disaster Recovery",
        "formats": "snapshots, tar.gz",
        "link": "Automated snapshot backup store for production Qdrant Vector DB VM",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "smart-audit-engine-prd-daisy-bkt-europe-west3",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "Daisy build worker bucket (ignore)",
        "scope_status": "Build Pipeline Artifacts",
        "formats": "daisy scratch files",
        "link": "Used by GCP Compute Engine Daisy disk imaging workflow",
        "residency": "europe-west3"
    },
    {
        "env": "PROD",
        "bucket": "smart-audit-engine-prd-daisy-bkt-us-west1",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "Daisy build worker bucket (ignore)",
        "scope_status": "Build Pipeline Artifacts",
        "formats": "daisy scratch files",
        "link": "Used by GCP Compute Engine Daisy disk imaging workflow",
        "residency": "us-west1"
    },
    {
        "env": "PROD",
        "bucket": "smart-audit-prod-sql-backup-bucket",
        "cid": "DC-10",
        "alt_cid": "DC-10",
        "user_purpose": "SQL backup bucket (ignore)",
        "scope_status": "Backup & Disaster Recovery",
        "formats": "bak, sql dumps",
        "link": "Automated production Cloud SQL Server backup destination",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "smart-audit-prod-sql-files-us",
        "cid": "DC-10",
        "alt_cid": "DC-10",
        "user_purpose": "SQL files export bucket (ignore)",
        "scope_status": "Database Export Staging",
        "formats": "bak, sql dumps",
        "link": "Production database dump and disaster recovery staging",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "testnew_bucket_prod",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "Test bucket (ignore)",
        "scope_status": "Temporary Scratch Store",
        "formats": "test data",
        "link": "Production verification scratch space",
        "residency": "us-central1"
    },

    # ==================== CIS MANDATED DEPLOYED BUCKETS ====================
    {
        "env": "DEV",
        "bucket": "newaiproject-510015-appraiso-evidence-dev",
        "cid": "DC-01",
        "alt_cid": "DC-33",
        "user_purpose": "CIS 3.2/3.4 Video & Photo Evidence Bucket (1-year retention)",
        "scope_status": "Active Data Store (CIS-Compliant)",
        "formats": "video, photo, media (mp4, mov, jpg)",
        "link": "Referenced by Cloud SQL Evidence Table and Qdrant smart_audit_collection",
        "residency": "us-central1"
    },
    {
        "env": "DEV",
        "bucket": "newaiproject-510015-appraiso-quarantine-dev",
        "cid": "DC-12",
        "alt_cid": "DC-12",
        "user_purpose": "CIS 3.2/3.4 Upload Quarantine Bucket (30-day auto-delete)",
        "scope_status": "Active Quarantine Store (CIS-Compliant)",
        "formats": "all extensions (unverified uploads)",
        "link": "Staging isolation buffer prior to antivirus/DLP clearance",
        "residency": "us-central1"
    },
    {
        "env": "DEV",
        "bucket": "newaiproject-510015-tfstate",
        "cid": "DC-13",
        "alt_cid": "DC-13",
        "user_purpose": "Terraform remote state backend store (CIS 3.3 locked)",
        "scope_status": "Infrastructure State Store",
        "formats": "tfstate (JSON)",
        "link": "Stores Terraform remote state backend for automated CI/CD deployments",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "appraiso-prod-evidence",
        "cid": "DC-01",
        "alt_cid": "DC-33",
        "user_purpose": "Production CIS 3.2/3.4 Evidence Bucket (1-year / 6-year retention)",
        "scope_status": "Active Data Store (CIS-Compliant)",
        "formats": "video, photo, media",
        "link": "Production primary evidence store referenced by Cloud SQL",
        "residency": "us-central1"
    },
    {
        "env": "PROD",
        "bucket": "appraiso-prod-quarantine",
        "cid": "DC-12",
        "alt_cid": "DC-12",
        "user_purpose": "Production CIS 3.2/3.4 Quarantine Bucket (30-day auto-delete)",
        "scope_status": "Active Quarantine Store (CIS-Compliant)",
        "formats": "all extensions (unverified uploads)",
        "link": "Production upload inspection buffer",
        "residency": "us-central1"
    }
]

# Business Owner and Custodian Lookup based on Category
OWNER_LOOKUP = {
    "DC-01": ("MSXI Audit Operations Lead [DATA OWNER]", "Miracle / Appraiso Engineering", "Appraiso Cloud Run Backend, Vertex AI Vision, Qdrant Multimodal Embedder"),
    "DC-06": ("Appraiso AI Systems Architect [DATA OWNER]", "Miracle / Appraiso Engineering", "Vertex AI Gemini 1.5/2.0, Cloud Run Backend"),
    "DC-09": ("MSXI InfoSec & Compliance Lead [DATA OWNER]", "Miracle / Appraiso DevOps", "Google Cloud Logging, Cloud Monitoring, LevelBlue USM"),
    "DC-10": ("Appraiso Lead Database Administrator [DATA OWNER]", "Miracle / Appraiso DevOps", "Google Cloud SQL Managed Service, Cloud Run Backend"),
    "DC-11": ("Appraiso Lead AI Engineer [DATA OWNER]", "Miracle / Appraiso DevOps", "Compute Engine Qdrant Docker Engine, Cloud Run VPC Connector"),
    "DC-12": ("Appraiso Information Security Team [DATA OWNER]", "Miracle / Appraiso DevOps", "Quarantine Processing Pipeline, ClamAV, Cloud DLP"),
    "DC-13": ("Appraiso DevOps & CI/CD Lead [DATA OWNER]", "Miracle / Appraiso DevOps", "Google Cloud Build, Artifact Registry, Compute Engine Daisy"),
    "DC-14": ("MSXI OEM Program Lead [DATA OWNER]", "Miracle / Appraiso Engineering", "Appraiso Cloud Run Backend, Vertex AI RAG Ingestion"),
    "DC-15": ("MSXI Lead Auditor & Methodology Owner [DATA OWNER]", "Miracle / Appraiso Engineering", "Appraiso Cloud Run Backend, Auditor Mobile App"),
    "DC-16": ("MSXI Operations & Reporting Team [DATA OWNER]", "Miracle / Appraiso Engineering", "Cloud Run Reporting Engine, BigQuery Analytics"),
    "DC-17": ("MSXI Compliance & Legal Officer [DATA OWNER]", "Miracle / Appraiso Engineering", "Cloud Run Backend, PDF Export Service, Dealer Portal"),
    "DC-21": ("MSXI OEM Program Lead [DATA OWNER]", "Miracle / Appraiso Engineering", "Appraiso Dealer Portal, PDF Report Generator"),
    "DC-33": ("MSXI Audit Operations Lead [DATA OWNER]", "Miracle / Appraiso Engineering", "Appraiso Cloud Run Backend, Vertex AI Vision"),
    "DC-34": ("MSXI Audit Operations Lead [DATA OWNER]", "Miracle / Appraiso Engineering", "Appraiso Cloud Run Backend, Vertex AI Vision"),
    "DC-37": ("MSXI Audit Operations Lead [DATA OWNER]", "Miracle / Appraiso Engineering", "Appraiso Cloud Run Backend, Cloud DLP Text Inspector")
}

def build_matrix():
    print(f">> Parsing document '{DOCX_FILE}'...")
    dc_meta = extract_docx_categories(DOCX_FILE)
    print(f">> Loaded {len(dc_meta)} categories from Section 6 Data Category Register.")

    matrix_rows = []

    for entry in RAW_BUCKET_ENTRIES:
        cid = entry["cid"]
        meta = dc_meta.get(cid, {})

        data_category = meta.get("Data Category", "Cloud Storage Data Store")
        class_tier = meta.get("Classification Tier", "Confidential")
        personal_data = meta.get("Contains Personal Data", "No")
        legal_basis = meta.get("Legal Basis", "Legitimate Interests (GDPR Art. 6(1)(f))")
        retention = meta.get("Retention Period", "6 Years (2190 Days)")
        retention_trigger = meta.get("Retention Trigger", "Audit Completion Date")
        dlp_feasible = meta.get("DLP Feasible", "Partial")
        dlp_approach = meta.get("DLP Approach", "Cloud DLP where technically applicable")

        owner_info = OWNER_LOOKUP.get(cid, ("MSXI Business Owner [DATA OWNER]", "Miracle / Appraiso Engineering", "Cloud Run Backend"))
        record_owner = owner_info[0]
        technical_custodian = owner_info[1]
        approved_processors = owner_info[2]

        # Determine Disposal Method
        if "30 days" in retention.lower() or "quarantine" in entry["bucket"].lower():
            disposal_method = "Automated GCS Lifecycle Deletion (Age: 30 Days)"
        elif "active for duration" in retention.lower() or "program" in entry["bucket"].lower():
            disposal_method = "Automated GCS Lifecycle Deletion / Manual Program Decommissioning"
        elif "6 years" in retention.lower() or "audit" in entry["bucket"].lower():
            disposal_method = "Automated GCS Object Lifecycle Management (Age: 2190 Days / 6 Years)"
        elif "1 year" in retention.lower() or "365" in retention.lower() or "evidence" in entry["bucket"].lower():
            disposal_method = "Automated GCS Object Lifecycle Rule (custom_time = 365 days + 30d noncurrent versions)"
        else:
            disposal_method = "Automated GCS Lifecycle Rule (Age: 30-90 Days)"

        # Security locks
        # Security locks & Confidentiality determination based on Public Access
        is_public = (cid == "DC-21" or "logo" in entry["bucket"].lower() or "public" in entry["bucket"].lower())
        
        if is_public:
            public_access_enforced = "No (Public Assets Permitted)"
            confidentiality_status = "Not Confidential (Public Asset)"
            pap = "inherited (Public Access Allowed for Brand Assets)"
            ubla = "True (Uniform Bucket-Level Access Enforced)"
        else:
            public_access_enforced = "Yes (Public Access Blocked / Enforced)"
            confidentiality_status = "Confidential (Private Bucket)"
            pap = "enforced (Public Access Prevention Locked)"
            ubla = "True (Uniform Bucket-Level Access Enforced)"

        row = {
            "Category ID": cid,
            "Data Category": data_category,
            "Bucket Name": entry["bucket"],
            "Storage Environment": entry["env"],
            "Is Publicly Accessed": "Yes" if is_public else "No",
            "Confidentiality Tag (Based on Public Access)": confidentiality_status,
            "Scope / Purpose in Appraiso": entry["user_purpose"],
            "Classification Tier (CIS 3.7)": class_tier,
            "Contains Personal Data (PII)": personal_data,
            "GDPR / LGPD Legal Basis": legal_basis,
            "Record Owner": record_owner,
            "Technical Custodian": technical_custodian,
            "System of Record": f"Google Cloud Storage ({entry['bucket']})",
            "Retention Min / Max": retention,
            "Retention Trigger Event": retention_trigger,
            "Disposal Method (CIS 3.4)": disposal_method,
            "Residency": f"{entry['residency']} (Google Cloud)",
            "Encryption / Key Model (CIS 3.11)": "Google-Managed Default KMS (AES-256)",
            "Approved Processors": approved_processors,
            "DLP Feasibility & Approach (CIS 3.13)": f"{dlp_feasible} - {dlp_approach}",
            "Public Access Prevention (CIS 3.3)": pap,
            "UBLA Enabled (CIS 3.3)": ubla,
            "Cross-System Link & Association": entry["link"],
            "Operational Scope Status": entry["scope_status"]
        }
        matrix_rows.append(row)

    # Sort rows by Environment (PROD, QA, NPD, DEV) and then Category ID
    env_order = {"PROD": 1, "QA": 2, "NPD": 3, "DEV": 4}
    matrix_rows.sort(key=lambda x: (env_order.get(x["Storage Environment"], 99), x["Category ID"], x["Bucket Name"]))

    # Write CSV with strict quote all and utf-8-sig
    fieldnames = list(matrix_rows[0].keys())
    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for r in matrix_rows:
            clean_r = {k: ("N/A" if r.get(k) is None or str(r.get(k)).strip() == "" else str(r[k]).strip()) for k in fieldnames}
            writer.writerow(clean_r)

    print(f"\n[+] Successfully generated '{OUTPUT_CSV}' with {len(matrix_rows)} classified storage buckets!")
    return len(matrix_rows)

if __name__ == "__main__":
    build_matrix()
