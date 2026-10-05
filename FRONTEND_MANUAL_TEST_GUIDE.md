# FRONTEND MANUAL TEST GUIDE

This guide explains how to manually test the complete Civic Pulse frontend application alongside the backend.

## 1. Setup & Environment
1. Start the backend:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```
2. Configure frontend environment:
   ```bash
   cd frontend
   cp .env.example .env.local
   # Ensure NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. Start the frontend:
   ```bash
   npm run dev
   ```
4. Open your browser to `http://localhost:3000`. You will be redirected to the Intake screen.

## 2. Intake Flow
**TEST NAME:** CSV Upload
- **ACTION:** Drag and drop `data/demo/pune_baner_complaints_20.csv` into the upload zone on the `/intake` page.
- **EXPECTED RESULT:** Upload processing state should show. Then a success screen should appear displaying "Records Received", "Accepted", and "Rejected".
- **FAILURE TO WATCH FOR:** Upload fails silently, or the UI does not transition to the completed summary screen.

## 3. Situation Map
**TEST NAME:** Map and Clusters
- **ACTION:** Click "View Situation Map" after upload (or navigate to `/situation`).
- **EXPECTED RESULT:** The Leaflet map should load. Cluster markers should appear (using red/orange coloring based on confidence).
- **FAILURE TO WATCH FOR:** Map crashes due to "window is not defined" (SSR error), or markers do not appear.

## 4. Case Workspace
**TEST NAME:** Case Investigation
- **ACTION:** Click on a cluster marker on the map, then click "OPEN CASE" in the popup.
- **EXPECTED RESULT:** You navigate to `/cases/[case_id]`. The Case Workspace should load the specific case data.
- **FAILURE TO WATCH FOR:** The page errors out, or data remains in a perpetual loading state.

## 5. Fingerprint & Evidence
**TEST NAME:** Inspect Evidence
- **ACTION:** On the Case Workspace, verify the Left Panel shows the "Failure Fingerprint" (magnitude, confidence, characteristics). Click the "Evidence" tab.
- **EXPECTED RESULT:** The Evidence Ledger should list all supporting evidence (Rainfall, Complaints, etc.) with explicit truth labels (e.g., REAL_DATA, SYNTHETIC_DATA) and confidence scores.
- **FAILURE TO WATCH FOR:** Missing icons or unformatted JSON strings in the fingerprint list.

## 6. Intervention Lab
**TEST NAME:** Compare Interventions
- **ACTION:** Click the "Intervention Lab" tab in the Case Workspace.
- **EXPECTED RESULT:** Multiple intervention options should be displayed, ranked by their overall score. The recommended option should be highlighted. You should see cost, duration, impact, and risk reduction metrics.
- **FAILURE TO WATCH FOR:** Hardcoded 3 options instead of dynamic backend responses, or missing budget/deadline filters.

## 7. Execution & Memory
**TEST NAME:** Post-Decision State
- **ACTION:** Navigate to `/execution` and `/memory`.
- **EXPECTED RESULT:** The UI should display the shell for tracking active work orders and historical infrastructure memory.
- **FAILURE TO WATCH FOR:** Broken layout or inaccessible navigation links.
