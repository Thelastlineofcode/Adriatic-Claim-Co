# Planned Issues / Backlog for Adriatic Claim Co

This document contains a prioritized list of issues (user stories) for the full buildout of the Adriatic Claim Co product. You can copy/paste each section into GitHub Issues when you're ready.

### 1) DB schema & migrations

- `backend/models.py` (SQLAlchemy) contains models: users, claims, claim_documents, kyc_checks, payouts, audit_logs.
- Alembic is configured with an initial migration that creates the schema.
- Local dev uses SQLite by default; documentation shows how to switch to Postgres.

## Backlog progress

Use the checklist below to track high-level progress inside this repository. When an issue is completed, mark its checkbox with an `x` and update the timestamp.

- [ ] 1. DB schema & migrations
- [ ] 2. Object storage for PII (S3/MinIO)
- [ ] 3. Admin auth & RBAC
- [ ] 4. KYC provider integration (sandbox)
- [ ] 5. PDF generation & e-sign flow
- [ ] 6. Payment / escrow integration (sandbox)
- [ ] 7. Claim discovery & state lookup worker
- [ ] 8. Admin reconciliation UI & workflows
- [ ] 9. CI / tests / GitHub Actions
- [ ] 10. Containerize services & deployment manifest
- [ ] 11. Monitoring, logs, and error tracking
- [ ] 12. Security hardening & encryption
- [ ] 13. Legal review & documentation
- [ ] 14. Spanish translation & bilingual UX
- [ ] 15. Tests & QA for payout flows

Last updated: 2025-10-30

---

### 2) Object storage for PII (S3/MinIO)

- Title: Object storage for PII uploads
- User story: As a system operator I need secure object storage for uploaded identity documents so that PII is stored separately from the DB and encrypted at rest.
- Acceptance criteria:
  - File uploads from `backend/mvp_server.py` are saved to S3-compatible storage (MinIO for dev) with server-side encryption.
  - Signed/expiring URLs are used for downloads.
  - Local dev fallback to filesystem documented and disabled for production.
- Estimate: 1d
- Labels: backend, infra, security

---

### 3) Admin auth & RBAC

- Title: Admin auth + RBAC for admin endpoints
- User story: As an admin I need secure login and role-based access so only authorized staff can view/modify claims.
- Acceptance criteria:
  - Add token-based admin auth (simple bearer token or JWT for MVP) protecting `/api/admin/*` endpoints.
  - Add `users` table, seed a dev admin user, and implement role checks for admin actions.
  - Document how to rotate/replace tokens.
- Estimate: 1d
- Labels: backend, security

---

### 4) KYC provider integration (sandbox)

- Title: KYC integration (sandbox)
- User story: As a compliance operator I need identity verification to reduce fraud and confirm claimants for high-value claims.
- Acceptance criteria:
  - Integrate with a KYC provider sandbox (Persona/Onfido/Veriff) with request & webhook handlers.
  - Store KYC results in `kyc_checks` table and surface status on claim record.
  - Add a test flow that simulates success and failure.
- Estimate: 3d
- Labels: backend, integrations, security

---

### 5) PDF generation & e-sign flow

- Title: Finder Agreement and POA PDF generation + signing
- User story: As a claimant I want to sign a Finder Agreement/POA so the company can file on my behalf and we keep signed records.
- Acceptance criteria:
  - Template engine (Jinja2) outputs a populated PDF for Finder Agreement and POA.
  - Generate PDFs server-side and store encrypted copies in object storage.
  - Provide an e-sign redirect URL (DocuSign/HelloSign placeholder) or in-app signing link for MVP.
- Estimate: 2d
- Labels: backend, legal, integrations

---

### 6) Payment / escrow integration (sandbox)

- Title: Payout & escrow ledger (sandbox)
- User story: As a finance operator I need to record payouts and support sandbox ACH or check issuance to send claimant funds net of fees.
- Acceptance criteria:
  - Implement payouts table and simple escrow ledger entries.
  - Integrate with Stripe ACH sandbox (or manual check flow) for payouts.
  - Provide reconciliation report for completed payouts.
- Estimate: 3d
- Labels: backend, finance, integrations

---

### 7) Claim discovery & state lookup worker

- Title: Claim discovery worker and state lookup
- User story: As an operator I want automated lookups against Texas Comptroller and NAUPA (or MissingMoney) to discover matches for submitted claimants.
- Acceptance criteria:
  - Background worker (Celery/RQ) performs search tasks and stores search results with scoring.
  - Worker exposes a dry-run mode and a job queue metric.
  - Document manual fallback steps for counties without an API.
- Estimate: 4d
- Labels: backend, worker, data

---

### 8) Admin reconciliation UI & workflows

- Title: Admin reconciliation UI
- User story: As an operations staff I need a simple admin UI to review matches, approve submissions, and reconcile payouts.
- Acceptance criteria:
  - A protected admin page lists claims with filters (status, date range, estimated payout).
  - Admin can mark claims as `approved_for_submission`, `submitted`, `paid`, and add audit notes.
  - Export CSV of reconciled payouts.
- Estimate: 3d
- Labels: frontend, backend, ops

---

### 9) CI / tests / GitHub Actions

- Title: CI: tests and linting (GitHub Actions)
- User story: As a developer I want automated tests and linting on PRs so we catch regressions early.
- Acceptance criteria:
  - Add GitHub Actions workflow that runs unit tests (`pytest`) and linters (flake8/ruff or similar) on PRs.
  - Test matrix includes Python 3.11/3.12 and SQLite.
  - Failing tests block merge to main.
- Estimate: 1d
- Labels: ci, tests

---

### 10) Containerize services & deployment manifest

- Title: Dockerize app + deploy manifest
- User story: As an ops engineer I want each service containerized and a deploy manifest so we can deploy to Render/Cloud Run/ECS.
- Acceptance criteria:
  - Dockerfile(s) for web app and worker.
  - `render.yaml` or Cloud Run manifest example included with env variables documented.
  - Basic health check endpoints implemented.
- Estimate: 2d
- Labels: infra, docker, deploy

---

### 11) Monitoring, logs, and error tracking

- Title: Observability: metrics & error tracking
- User story: As an SRE I need monitoring and error reporting to alert on failures and measure system health.
- Acceptance criteria:
  - Integrate Sentry for exceptions and a metrics exporter (Prometheus style) for queue depth and request latency.
  - Add Grafana/Datadog guidance and sample dashboards (or document how to connect to the provider).
- Estimate: 2d
- Labels: infra, monitoring

---

### 12) Security hardening & encryption

- Title: Security & PII protections
- User story: As a security officer I need PII encrypted and access control in place so claimants' data is protected.
- Acceptance criteria:
  - Database field-level encryption or clear guidance for encrypting SSNs and sensitive fields.
  - S3 server-side encryption enabled; access keys rotated guidance added.
  - RBAC and MFA guidance for admins documented.
- Estimate: 2d
- Labels: security, compliance

---

### 13) Legal review & documentation

- Title: Legal review of Finder Agreement and Fee Disclosure
- User story: As the business owner I want the Finder Agreement and Fee Disclosure reviewed by a Texas-licensed attorney so we avoid regulatory exposure.
- Acceptance criteria:
  - Create a `legal/` folder with final contract templates and change log.
  - Add checklist of items for attorney review (fee language, POA language, retention period).
  - Verify investigator licensure and role: confirm that the son-in-law's existing security license satisfies Texas requirements for investigator work, or identify additional licenses/registrations necessary.
  - Draft Investigator Agreement and employment/classification recommendation for counsel review.
  - Track attorney sign-off in the issue.
- Estimate: 2d
- Labels: legal, compliance

---

### 14) Spanish translation & bilingual UX

- Title: Spanish translation of intake & disclosures
- User story: As a claimant who prefers Spanish I want the intake and fee disclosure in Spanish so I can understand the terms.
- Acceptance criteria:
  - `web/mvp/intake.html` and `docs/Fee_Disclosure.md` have Spanish versions or toggles.
  - Translation verified and stored in `i18n/` folder.
- Estimate: 1d
- Labels: frontend, i18n

---

### 15) Tests & QA for payout flows

- Title: End-to-end tests for payout flow
- User story: As a QA engineer I want end-to-end tests that simulate intake → KYC → submission → payout to ensure the business logic works.
- Acceptance criteria:
  - End-to-end test harness (pytest + localstack/minio) runs and verifies net payout calculations and state transitions.
  - Tests included in CI matrix.
- Estimate: 3d
- Labels: tests, e2e

---

If you want, I can also generate these issues automatically in GitHub for you (I already have CLI access), or I can break any of these into smaller subtasks. Tell me which format you prefer for creation (create all now / create prioritized subset / only create skeletons) and I will proceed when you confirm.

---

### Experiments added from Revenue Strategist plan

The following experiment issues were added as actionable tasks (small, testable, with estimated effort). Use the Backlog progress checklist to mark them when complete.

#### EXP-1: State & county integration pilot (Houston-first)

- Hypothesis: Direct integration with Texas Comptroller search/API increases discovery_success_rate from ~10% to ~25% for Houston claims.
- Acceptance criteria:
  - Implement a connector/service that queries Texas Comptroller (or simulated API) for name-based search.
  - End-to-end test that shows discovery_success_rate uplift on a sample dataset.
  - Document manual fallback for counties without API.
- Estimate: 5d
- Labels: backend, integrations, data, priority-high

#### EXP-2: Community partnership referrals (title companies & nonprofits)

- Hypothesis: Partner referrals yield CAC_per_signed << paid channels (~$20–$50).
- Acceptance criteria:
  - Pilot agreement with at least 1 partner.
  - Instrument partner channel (utm/campaign) and report CAC for the channel.
  - At least 10 referred leads processed.
- Estimate: 7d
- Labels: growth, partnerships, ops

#### EXP-3: Low-touch self-service funnel for claims < $600

- Hypothesis: Automating intake & e-sign reduces average cost-per-handled-claim by 3–4x and increases conversion for low-value claims.
- Acceptance criteria:
  - Self-service UX implemented at `/mvp/intake-self-service`.
  - Automated PDF + e-sign flow stub integrated and tested end-to-end.
  - Track fulfillment cost per claim and conversion uplift.
- Estimate: 14d
- Labels: frontend, backend, product

#### EXP-4: Discovery-before-sign pre-qualification

- Hypothesis: Running discovery before signature increases the fraction of signers who have discoverable payouts and reduces wasted CAC.
- Acceptance criteria:
  - Add a lightweight pre-qualification endpoint (done: `/api/claims/qualify`), connected to intake flow.
  - Measure fraction of signers with discoverable payouts vs. control group.
  - If uplift > X% (tunable), roll out pre-qualification as default.
- Estimate: 7d
- Labels: backend, product, data

#### EXP-5: Content & SEO for unclaimed-money queries by county

- Hypothesis: High-quality localized content drives organic leads with CAC << paid channels.
- Acceptance criteria:
  - Publish 5 county-targeted pages with structured schema and local FAQ.
  - Track organic leads/month and CAC for organic channel.
  - At least one county page ranks on page 1 for target query within 90 days (measure via SERP tracker).
- Estimate: ongoing (30d initial)
- Labels: growth, content, seo

#### EXP-6: Enterprise B2B lead / data pilot

- Hypothesis: Some partners will pay per-processed-lead or subscription for data access, creating non-consumer revenue.
- Acceptance criteria:
  - Define data product and partner legal consent language.
  - Pilot with 1 partner and collect revenue data.
  - Ensure consumer-fee cap (10%) remains unaffected for claimants.
- Estimate: 21d
- Labels: bizdev, legal, growth
