# FRONTEND HANDOFF

Welcome to the Civic Pulse Frontend.

## 1. What is Complete
- Next.js App Router initialization with Tailwind CSS, TypeScript, and React Query.
- API service layer strictly typed against the backend Pydantic models (`src/types/api.ts` & `src/services/api/`).
- App Layout and Navbar with proper responsive scaling and Dark Mode support.
- **Intake**: CSV drag-and-drop upload and progress indicator.
- **Situation**: Dynamic Leaflet map displaying Failure Clusters based on backend data.
- **Case Workspace**: 
  - Progressive layout structure.
  - Failure Fingerprint rendering dynamic metadata.
  - Evidence Ledger with audit-trail UI.
  - Intervention Lab displaying ranked backend recommendations and cost estimations.

## 2. What is Incomplete
- **Visual Failure Chain**: The UI renders a linear sequence, but a graph visualization library might be required if the backend chain becomes highly branched.
- **Execution & Memory Data Binding**: The pages exist (`/execution` and `/memory`), but detailed inner dashboard components connecting to `executionApi` and `outcomesApi` require mapping actual task timelines and historical cards.
- **Dynamic Constraint Updates**: The Intervention Lab has a button for constraints, but the form to POST updated constraints back to the API and invalidate the `case-interventions` query needs to be built out.

## 3. Where Things Live
- **API Services**: `src/services/api/` (Centralized fetch wrapper and endpoint methods)
- **Types**: `src/types/api.ts` (Mirror of Pydantic schemas)
- **Pages**: `src/app/`
  - `/intake`
  - `/situation`
  - `/cases/[id]`
  - `/execution`
  - `/memory`
- **Components**: `src/components/`
  - `/layout`
  - `/intake`
  - `/maps`
  - `/cases`

## 4. How Maps Work
Because Leaflet accesses the `window` object, it causes Next.js SSR (Server-Side Rendering) to crash if imported directly.
**Always use the `DynamicMap` wrapper (`src/components/maps/DynamicMap.tsx`)** which uses `next/dynamic` with `ssr: false` to lazy-load the actual `SituationMap` component.

## 5. How the Backend is Connected
We do not use raw `fetch` calls in UI components. 
- Use the typed wrappers in `src/services/api/*.ts`.
- Components use `@tanstack/react-query` hooks (e.g., `useQuery`, `useMutation`) passing the API service functions. 
- Environment variable `NEXT_PUBLIC_API_URL` dictates the backend location.

## 6. Commands to Run
```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build
```

## 7. Next Recommended Improvements
1. Add a rich Gantt-chart visualization for the Execution/Work Orders screen.
2. Implement WebSocket/Server-Sent Events for real-time Dynamic Replanning updates.
3. Hook up the constraint editor form in the Intervention Lab to recalculate scores live.
