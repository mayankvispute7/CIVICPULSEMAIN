# CIVIC PULSE — INTEGRATION CHECKLIST

Version: 1.0

Purpose:

Ensure backend and frontend connect completely after independent development.

The project is NOT considered complete until this checklist passes.

---

# 1. REPOSITORY

[ ] Clean repository created

[ ] backend/ exists

[ ] frontend/ exists

[ ] ARCHITECTURE.md exists

[ ] API_CONTRACT.md exists

[ ] DATA_CONTRACT.md exists

[ ] INTEGRATION_CHECKLIST.md exists

[ ] No authentication required

[ ] No unnecessary rebuild of old prototype

---

# 2. DOCUMENTATION

[ ] Backend follows ARCHITECTURE.md

[ ] Frontend follows ARCHITECTURE.md

[ ] Backend follows API_CONTRACT.md

[ ] Frontend follows API_CONTRACT.md

[ ] Backend follows DATA_CONTRACT.md

[ ] Frontend follows DATA_CONTRACT.md

---

# 3. ENTITY INTEGRITY

Verify stable IDs:

[ ] complaint_id

[ ] site_id

[ ] cluster_id

[ ] case_id

[ ] evidence_id

[ ] hypothesis_id

[ ] intervention_id

[ ] work_order_id

[ ] task_id

[ ] verification_id

[ ] outcome_id

[ ] memory_id

---

# 4. API CONTRACT

For every endpoint:

[ ] Endpoint exists

[ ] HTTP method matches

[ ] Request schema matches

[ ] Response schema matches

[ ] Field names match

[ ] Data types match

[ ] Required/optional status matches

[ ] Error response matches

[ ] Backend test exists

[ ] Frontend service exists

[ ] Frontend TypeScript type exists

[ ] Mock response matches

---

# 5. FRONTEND API INTEGRATION

[ ] All API calls go through service layer

[ ] No hardcoded production API URL

[ ] API URL comes from environment variable

[ ] Loading states exist

[ ] Empty states exist

[ ] Error states exist

[ ] Retry behavior exists where appropriate

[ ] No component invents backend fields

[ ] No duplicate API models exist

---

# 6. COMPLAINT PIPELINE

Test:

PDF
→ extraction
→ complaints
→ geolocation
→ site
→ cluster

[ ] PDF upload works

[ ] extraction works

[ ] complaints created

[ ] coordinates generated

[ ] site assigned

[ ] clusters generated

[ ] cluster IDs persist

[ ] frontend displays results

---

# 7. INVESTIGATION PIPELINE

[ ] cluster opens case

[ ] case has fingerprint

[ ] fingerprint has hypotheses

[ ] hypotheses reference evidence

[ ] failure chain loads

[ ] history loads

[ ] site context loads

[ ] evidence ledger loads

[ ] satellite/spatial evidence loads

---

# 8. DECISION PIPELINE

[ ] intervention options generated

[ ] constraints accepted

[ ] options ranked

[ ] scoring factors visible

[ ] assumptions visible

[ ] counterfactual generated

[ ] cost of inaction generated

[ ] decision readiness generated

---

# 9. EXECUTION PIPELINE

[ ] intervention selected

[ ] resolution plan generated

[ ] tasks generated

[ ] work order created

[ ] human approval recorded

[ ] task can be started

[ ] task can be completed

[ ] delay can be recorded

[ ] replan can be triggered

[ ] revised plan is returned

---

# 10. VERIFICATION PIPELINE

[ ] field photo upload works

[ ] GPS received

[ ] timestamp received

[ ] work-order location checked

[ ] duplicate check executed

[ ] visual change check executed

[ ] verification result displayed

[ ] manual review state works

---

# 11. OUTCOME PIPELINE

[ ] next comparable event can be recorded

[ ] predicted outcome stored

[ ] observed outcome stored

[ ] prediction vs reality displayed

[ ] recurrence recorded

[ ] outcome stored

---

# 12. LEARNING PIPELINE

[ ] learning endpoint works

[ ] intervention outcome updates memory

[ ] hypothesis confidence can be updated

[ ] recurrence history is preserved

[ ] previous records are not overwritten

---

# 13. INFRASTRUCTURE MEMORY

[ ] site memory loads

[ ] previous complaints appear

[ ] previous cases appear

[ ] previous interventions appear

[ ] previous outcomes appear

[ ] recurrence history appears

[ ] similar cases appear where available

---

# 14. FULL END-TO-END TEST

Perform one complete test:

PDF
↓
Complaint Extraction
↓
Complaints
↓
Geospatial Mapping
↓
Clustering
↓
Failure Case
↓
Failure Fingerprint
↓
History
↓
Evidence
↓
Decision Readiness
↓
Intervention Options
↓
Constraints
↓
Ranking
↓
Counterfactual
↓
Prediction
↓
Resolution Plan
↓
Work Order
↓
Task Execution
↓
Delay
↓
Dynamic Replanning
↓
Field Evidence
↓
Verification
↓
Next Event
↓
Outcome
↓
Prediction vs Reality
↓
Learning
↓
Infrastructure Memory

Every step must use the output of the previous step.

No disconnected demo screens are allowed.

---

# 15. DATA FLOW TEST

Confirm:

PDF ID
→ complaint IDs
→ site ID
→ cluster ID
→ case ID
→ evidence IDs
→ intervention ID
→ work order ID
→ task IDs
→ verification ID
→ outcome ID
→ memory ID

No orphaned records.

---

# 16. MOCK DATA PARITY

[ ] Frontend mock data follows DATA_CONTRACT.md

[ ] Mock API responses follow API_CONTRACT.md

[ ] Real API can replace mocks without changing UI components

[ ] No mock-only fields are required by frontend

---

# 17. UI QUALITY

[ ] No excessive cards

[ ] No excessive pills

[ ] No childish design

[ ] No generic AI dashboard appearance

[ ] No excessive gradients

[ ] No unnecessary neon/glow effects

[ ] No giant empty areas

[ ] No tiny unreadable text

[ ] Good spacing

[ ] Clear hierarchy

[ ] Light mode polished

[ ] Dark mode polished

[ ] Maps have clear hierarchy

[ ] Progressive disclosure used

[ ] Officer can understand primary conclusion quickly

---

# 18. DEMO DATA TRUTH

[ ] Synthetic data is clearly labelled

[ ] Real open data is labelled

[ ] Model estimates are labelled

[ ] Assumptions are labelled

[ ] AI-generated text is distinguishable

[ ] No fabricated PMC records presented as real

---

# 19. SECURITY / CONFIGURATION

[ ] No API keys hardcoded

[ ] .env used

[ ] .env.example included

[ ] Secrets excluded from Git

[ ] Production URLs configurable

[ ] Upload validation exists

---

# 20. PERFORMANCE

[ ] Map does not load thousands of unnecessary objects

[ ] Spatial queries are indexed

[ ] Heavy processing is not performed unnecessarily on every page load

[ ] Satellite/demo observations can be cached

[ ] Large PDFs are handled safely

---

# 21. FINAL CONTRACT AUDIT

Before merging:

Compare:

ARCHITECTURE.md
API_CONTRACT.md
DATA_CONTRACT.md
backend schemas
backend endpoints
frontend types
frontend API services
frontend mocks

[ ] All consistent

---

# 22. FINAL RULE

If ANY checkbox above fails:

The integration is NOT complete.

Do not rebuild the product.

Fix the broken contract, endpoint, type, service, or connection.

Then rerun the affected integration test.

---

# 23. MERGE RULE

Backend branch:

backend-v1

Frontend branch:

frontend-v1

Merge:

backend-v1
+
frontend-v1
→
main

After merge:

ONLY integration fixes.

Do NOT rebuild the backend.

Do NOT rebuild the frontend.

Do NOT redesign the architecture.
