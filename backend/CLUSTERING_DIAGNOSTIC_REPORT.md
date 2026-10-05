# CIVIC PULSE: CLUSTERING DIAGNOSTIC REPORT

## 1. Canonical Dataset Test
- **Total Complaints:** 20
- **Total Clusters:** 1
- **Unassigned Complaints:** 0

### Waterlogging Cluster - Baner
- **Cluster Size:** 20 complaints
- **Incident Count (Episodes):** 3
- **Confidence:** 0.99 (HIGH)
- **Evidence Strength:** STRONG
- **Rationale:** Clustered 20 complaints based on multi-signal evidence. Strongest signals: spatial proximity, category/semantic relationship, temporal coherence. 3 distinct incident episodes identified.
#### Relationship Evidence
```json
{
  "spatial": 0.922,
  "temporal": 0.695,
  "semantic": 0.824,
  "event": "Correlated based on 48h windows",
  "infrastructure": 0.824
}
```

## 2. Complaint Diagnostic Table
| ID | Category | Reported At | Severity | Assigned Cluster | Reason |
|---|---|---|---|---|---|
| 425d41 | WATERLOGGING | 2026-06-14 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| 4dc1bd | DRAINAGE | 2026-06-14 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| e18375 | TRAFFIC_DISRUPTION | 2026-06-14 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| 13b1aa | FLOODING | 2026-06-14 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| 870265 | BLOCKED_INLET | 2026-06-15 | MEDIUM | Waterlogging Cluster - Baner | Multi-signal affinity |
| f4a70f | WATERLOGGING | 2026-07-03 | MEDIUM | Waterlogging Cluster - Baner | Multi-signal affinity |
| 35562e | SURFACE_RUNOFF | 2026-07-03 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| 33aa9f | TRAFFIC_DISRUPTION | 2026-07-03 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| 4fe613 | WATERLOGGING | 2026-07-04 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| 594154 | DRAINAGE | 2026-07-04 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| 2244c7 | PEDESTRIAN_DISRUPTION | 2026-07-04 | MEDIUM | Waterlogging Cluster - Baner | Multi-signal affinity |
| 677e4f | FLOODING | 2026-07-04 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| e9f0d9 | PRE_RAIN_RISK | 2026-08-11 | MEDIUM | Waterlogging Cluster - Baner | Multi-signal affinity |
| 9a87df | WATERLOGGING | 2026-08-11 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| 320767 | DRAINAGE | 2026-08-11 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| c31a10 | TRAFFIC_DISRUPTION | 2026-08-11 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| 6ea63c | WATERLOGGING | 2026-08-12 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| 31bcff | BLOCKED_INLET | 2026-08-12 | MEDIUM | Waterlogging Cluster - Baner | Multi-signal affinity |
| 1c2d17 | TRAFFIC_DISRUPTION | 2026-08-12 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
| 0871d4 | FLOODING | 2026-08-12 | HIGH | Waterlogging Cluster - Baner | Multi-signal affinity |
