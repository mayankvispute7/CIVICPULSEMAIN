# Civic Pulse MVP Flow Implementation

## 1. Objective
To make the existing Civic Pulse MVP work as one complete, understandable, demonstrable end-to-end product. The UI should guide users through a clear decision-support workflow rather than exposing internal database structures.

## 2. Structural Changes

### Case Workspace
The Case Workspace (`CaseWorkspace.tsx`) was completely redesigned from a tab-based layout into a guided workflow rail on the left. The stages are progressively disclosed:
1. **Understand**: Shows the impact summary and related signals.
2. **Investigate**: Shows the visual failure chain and the evidence ledger.
3. **History**: Shows historical context and previous incidents.
4. **Predict**: Shows the model estimate of the cost of inaction.
5. **Simulate & Decide**: Houses the `InterventionLab`.
6. **Execute**: Roadmap and work order placeholder.
7. **Verify**: Field verification placeholder.
8. **Outcome**: Outcome tracking placeholder.
9. **Memory**: Infrastructure memory placeholder.

### Fingerprint Card
The `FingerprintCard.tsx` was updated to use `framer-motion` to sequentially and visually animate the failure fingerprint in, providing a more engaging "investigative" feel for the user. 

### Intervention Lab
The `InterventionLab.tsx` was rebuilt to feature a side-by-side layout:
- **Left**: Ranked interventions, clearly explaining feasibility.
- **Right (Constraints)**: A form to input actual officer constraints (Budget, Deadline, Workers), which updates the backend and re-ranks the options.
- **Right (Decision)**: An Officer Decision panel, asking the user to either approve the recommended option or reject it (with a dropdown for the reason).
- **Right (Copilot)**: A small AI Copilot widget that provides simulated context, explaining why constraints make certain options infeasible.

## 3. Backend & Data State
- **Idempotency**: The `csv_ingestion_service` checks for DB duplicates accurately, preventing issues with re-uploaded CSVs. 
- **Determinism**: The `seed_db.py` script was run to generate a completely consistent, deterministic E2E database state using the `pune_baner_complaints_20.csv` file. 
- **API Updates**: `casesApi.updateConstraints` was added to the frontend `api.ts` to support the interactive constraints engine.

## 4. Next Steps
- Implement full backend processing for the Decision Rejection flow.
- Hook the Brainstorming Copilot into a real LLM stream.
- Flesh out the Execute, Verify, Outcome, and Memory views.
