# CIVIC PULSE — DATA SOURCES

Version: 1.0
Status: ACTIVE

This document defines the data required by Civic Pulse, its intended source, and whether it is real, synthetic, estimated, or optional.

---

## 1. DATA TRUTH POLICY

Every dataset must be classified as:

REAL_DATA
SYNTHETIC_DATA
MODEL_ESTIMATION
AI_GENERATED_TEXT
EVIDENCE
ASSUMPTION

Never present synthetic data as official municipal data.

---

# 2. COMPLAINT DATA

Purpose:

Initial incident/complaint ingestion.

Preferred sources:

- municipal complaint PDFs
- structured municipal complaint exports
- CSV/JSON
- synthetic demo complaints

MVP:

Use a realistic synthetic complaint dataset if official complaint data is unavailable.

Required fields:

complaint_id
description
incident_type
reported_at
location/address
severity
source
data_truth

---

# 3. GEOSPATIAL DATA

## OpenStreetMap

Use for:

- roads
- buildings
- amenities
- infrastructure where available
- critical facilities
- geographic context

Status:

REAL_DATA

Provider:

OpenStreetMap

Implementation:

Use appropriate OSM APIs/downloads and cache data where appropriate.

Do not repeatedly query public APIs unnecessarily.

---

# 4. ROAD NETWORK

Source:

OpenStreetMap or another legally usable open road dataset.

Use for:

- road classification
- road segments
- corridor context
- affected-road estimation

Important:

Road exposure is a proxy unless actual traffic data exists.

Do not claim exact vehicle delay without traffic data.

---

# 5. DRAINAGE DATA

Potential source:

OpenStreetMap where mapped.

Additional options:

curated demo drainage network
synthetic drainage network
municipal/open drainage data where legally available

MVP:

Use real mapped data where available and synthetic/curated demo data where coverage is insufficient.

Always label synthetic drainage data.

Do not claim that synthetic drains represent actual municipal infrastructure.

---

# 6. TERRAIN / DEM

Potential source:

Copernicus DEM or another openly usable DEM.

Use for:

- elevation
- slope
- terrain depression
- runoff context
- catchment screening

Classification:

REAL_DATA

Important:

DEM is supporting spatial evidence.

Do not claim centimeter-level site measurements from coarse DEM data.

---

# 7. LAND COVER

Potential sources:

ESA WorldCover
Sentinel-derived land-cover products

Use for:

- impervious surface context
- runoff assumptions
- land-use analysis

Classification:

REAL_DATA

---

# 8. RAINFALL

Potential sources:

Open-Meteo historical/archive data
other openly usable meteorological datasets

Use for:

- rainfall correlation
- event detection
- recurrence analysis
- screening-level runoff estimation

Classification:

REAL_DATA

Important:

Verify current licensing/usage terms before production deployment.

Do not claim station-level accuracy when using gridded/reanalysis data.

---

# 9. EARTH OBSERVATION

Potential sources:

Sentinel-1
Sentinel-2
Copernicus Data Space
STAC-compatible public datasets

Use for:

- environmental context
- surface/wetness signals
- spatial change
- land-cover context
- supporting evidence

Classification:

REAL_DATA

Important:

Satellite evidence is supporting evidence.

Never claim:

"Satellite proves contractor completed the work."

Use:

"Independent spatial evidence supports/does not support the reported change."

---

# 10. BUILDINGS

Potential sources:

OpenStreetMap
other openly usable building datasets

Use for:

- affected-building count
- exposure estimation
- local context

Important:

Building count is exposure, not proof of property damage.

---

# 11. POPULATION

Potential sources:

WorldPop
GHSL
other openly usable population datasets

Use for:

coarse exposure estimates.

Do not claim exact people affected unless authoritative data exists.

---

# 12. CRITICAL FACILITIES

Potential source:

OpenStreetMap

Examples:

- hospitals
- schools
- emergency services
- public facilities

Use for:

criticality/exposure analysis.

---

# 13. HISTORICAL COMPLAINTS

Preferred:

real municipal historical data where available.

MVP:

synthetic historical incidents.

Classification:

SYNTHETIC_DATA if generated for demonstration.

Synthetic history must be clearly labelled.

---

# 14. PREVIOUS INTERVENTIONS

Preferred:

real municipal work-order/history data.

MVP:

synthetic historical interventions.

Classification:

SYNTHETIC_DATA

Never present synthetic work orders as actual government work.

---

# 15. FIELD PHOTOS

Source:

Civic Pulse field-capture workflow.

Use:

- work verification
- before/after comparison
- evidence integrity

Classification:

EVIDENCE

The system should record:

GPS
timestamp
task/work-order reference
capture metadata

---

# 16. CROSS-CITY CASE LIBRARY

Use curated public sources describing infrastructure interventions elsewhere.

Store:

city
problem
intervention
reported outcome
conditions
source/reference
applicability notes

Classification:

EVIDENCE

Important:

A successful intervention elsewhere is not proof that it will work locally.

---

# 17. SYNTHETIC DEMO DATA

Synthetic data is allowed for:

- complaints
- historical incidents
- previous interventions
- work orders
- field execution
- outcomes

Synthetic data must:

1. have stable IDs
2. preserve realistic relationships
3. be reproducible
4. be labelled SYNTHETIC_DATA
5. never be represented as official municipal data

---

# 18. REAL + SYNTHETIC HYBRID

Recommended demo strategy:

REAL:

- basemap
- roads
- buildings
- terrain
- rainfall
- land cover
- satellite observations where available

SYNTHETIC:

- complaints
- historical municipal interventions
- work orders
- execution history
- outcome history

This provides geographic realism without fabricating government records.

---

# 19. API KEYS

Do not put API keys inside this document.

Keys belong in environment variables.

See:

ENVIRONMENT.md

---

# 20. DATA PROVIDER FAILURE

Every external data source must have:

primary provider
fallback provider or cached dataset
clear failure behavior

The application must not completely fail because one external dataset is temporarily unavailable.

---

# 21. DATA CACHING

Cache:

- geocoding
- OSM results
- satellite observations
- DEM windows
- rainfall queries

where appropriate and legally permitted.

Do not repeatedly request identical external data during a demo.

---

# 22. DATA PROVENANCE

For important external observations store:

source
retrieved_at
dataset/product
location/AOI
observation time
data_truth

---

# 23. FINAL RULE

Before adding any external dataset:

document:

DATASET
→ SOURCE
→ PURPOSE
→ API/DOWNLOAD METHOD
→ PROCESSING
→ OUTPUT
→ LICENSE/TERMS
→ FALLBACK

No undocumented external dependency should be introduced.