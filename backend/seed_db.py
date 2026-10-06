import sys
import os
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine, Base
from app.models.domain import (
    Site, Complaint, FailureCluster, FailureCase, Evidence,
    HistoricalIncident, Prediction, InterventionOption,
    InterventionConstraint, DecisionAnalysis, ResolutionPlan,
    WorkOrder, WorkOrderTask, ExecutionEvent, ReplanEvent,
    FieldEvidence, Verification, OutcomeObservation,
    PredictionRealityComparison, LearningRecord, InfrastructureMemory,
    generate_uuid
)
from app.models.enums import DataTruth, ApprovalState, WorkOrderStatus, TaskStatus, FailureType

def reset_demo_data():
    print("1. Clearing the database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        print("2. Generating Demo Site and Cluster...")
        site_id = generate_uuid()
        site = Site(
            site_id=site_id,
            site_label="Kothrud-Bavdhan",
            latitude=18.5089,
            longitude=73.7937,
            ward="Kothrud",
            neighborhood="Bavdhan Junction",
            terrain_elevation=560.5,
            terrain_slope=1.8,
            data_truth=DataTruth.SYNTHETIC_DATA.value
        )
        db.add(site)

        cluster_id = generate_uuid()
        cluster = FailureCluster(
            cluster_id=cluster_id,
            title="Kothrud-Bavdhan Recurring Waterlogging",
            complaint_count=18,
            incident_count=4,
            confidence=0.85,
            status="PROMOTED",
            site_id=site_id,
            centroid_lat=18.5089,
            centroid_lon=73.7937,
            spatial_radius_m=250.0,
            categories=["WATERLOGGING", "BLOCKED_INLET", "ROAD_DISRUPTION"],
            confidence_level="HIGH",
            evidence_strength="STRONG",
            data_truth=DataTruth.MODEL_ESTIMATION.value
        )
        db.add(cluster)

        print("3. Generating Complaints...")
        # 18 Complaints for this cluster
        base_time = datetime.utcnow() - timedelta(days=5)
        for i in range(18):
            comp = Complaint(
                complaint_id=generate_uuid(),
                title=f"Waterlogging report #{i+1}",
                description="Water accumulated near the road after heavy rainfall. Vehicles are unable to pass." if i % 2 == 0 else "Blocked inlet causing standing water and traffic disruption.",
                incident_type="WATERLOGGING",
                category="WATERLOGGING" if i % 2 == 0 else "BLOCKED_INLET",
                reported_at=base_time + timedelta(hours=i),
                latitude=18.5089 + (i * 0.0001),
                longitude=73.7937 + (i * 0.0001),
                address="Kothrud-Bavdhan Corridor",
                ward="Kothrud",
                severity="HIGH" if i % 3 == 0 else "MEDIUM",
                status="CLUSTERED",
                site_id=site_id,
                cluster_id=cluster_id,
                data_truth=DataTruth.IMPORTED_DATA.value
            )
            db.add(comp)

        print("4. Generating Primary Demo Case...")
        case_id = generate_uuid()
        case = FailureCase(
            case_id=case_id,
            cluster_id=cluster_id,
            site_id=site_id,
            title="Recurring Waterlogging",
            failure_type=FailureType.WATERLOGGING.value,
            recurrence_count=4,
            impact_summary="18 complaints are concentrated around the Kothrud-Bavdhan corridor. Most reports occurred during or shortly after heavy rainfall and describe water accumulation, drainage overflow and road disruption.",
            confidence=0.76,
            status="MONITORED",  # To show full loop
            fingerprint={
                "complaints_count": 18,
                "previous_incidents": 4,
                "affected_signals": 3,
                "observation_period_days": 222,
                "confidence_score": 0.76,
                "characteristics": [
                    {"label": "Rainfall association", "status": "HIGH"},
                    {"label": "Terrain accumulation", "status": "PRESENT"},
                    {"label": "Drainage constraint", "status": "POSSIBLE"},
                    {"label": "Historical recurrence", "status": "CONFIRMED"}
                ],
                "signals": [
                    {"label": "Waterlogging", "count": 9},
                    {"label": "Drainage", "count": 5},
                    {"label": "Blocked inlet", "count": 4},
                    {"label": "Traffic disruption", "count": 3}
                ]
            },
            failure_chain={
                "nodes": [
                    {"id": "heavy_rain", "label": "HEAVY RAINFALL", "type": "trigger"},
                    {"id": "high_runoff", "label": "HIGH RUNOFF", "type": "effect"},
                    {"id": "terrain", "label": "LOCAL TERRAIN ACCUMULATION", "type": "factor"},
                    {"id": "drainage", "label": "POSSIBLE DRAINAGE CONSTRAINT", "type": "factor"},
                    {"id": "water_accum", "label": "WATER ACCUMULATION", "type": "effect"},
                    {"id": "road_disrupt", "label": "ROAD DISRUPTION", "type": "impact"},
                    {"id": "complaints", "label": "MULTIPLE COMPLAINTS", "type": "outcome"}
                ],
                "edges": [
                    {"source": "heavy_rain", "target": "high_runoff"},
                    {"source": "high_runoff", "target": "terrain"},
                    {"source": "terrain", "target": "drainage"},
                    {"source": "drainage", "target": "water_accum"},
                    {"source": "water_accum", "target": "road_disrupt"},
                    {"source": "road_disrupt", "target": "complaints"}
                ]
            },
            data_truth=DataTruth.MODEL_ESTIMATION.value
        )
        db.add(case)

        print("5. Generating Evidence...")
        evidences = [
            Evidence(
                case_id=case_id,
                type="COMPLAINTS",
                title="Complaint concentration",
                source="Citizen Reports",
                description="18 related complaints within the corridor.",
                value={"count": 18},
                confidence=0.9,
                data_truth=DataTruth.IMPORTED_DATA.value
            ),
            Evidence(
                case_id=case_id,
                type="WEATHER",
                title="Rainfall correlation",
                source="Weather API",
                description="4 comparable rainfall events.",
                value={"correlation_strength": 0.78, "events": [{"event": "Event 1", "rain": "42 mm", "impact": "Waterlogging reported"}, {"event": "Event 2", "rain": "51 mm", "impact": "Waterlogging reported"}, {"event": "Event 3", "rain": "47 mm", "impact": "Drain overflow reported"}, {"event": "Event 4", "rain": "55 mm", "impact": "Road disruption reported"}]},
                confidence=0.85,
                data_truth=DataTruth.SYNTHETIC_DATA.value
            ),
            Evidence(
                case_id=case_id,
                type="TOPOGRAPHY",
                title="Terrain",
                source="GIS System",
                description="Local depression detected.",
                value={"slope": "1.8%"},
                confidence=0.9,
                data_truth=DataTruth.SYNTHETIC_DATA.value
            ),
            Evidence(
                case_id=case_id,
                type="INFRASTRUCTURE",
                title="Drainage",
                source="Infrastructure Model",
                description="Estimated capacity ratio: 0.67",
                value={"capacity_ratio": 0.67},
                confidence=0.75,
                data_truth=DataTruth.MODEL_ESTIMATION.value
            ),
            Evidence(
                case_id=case_id,
                type="HISTORY",
                title="Historical recurrence",
                source="Incident DB",
                description="4 previous incidents.",
                value={"incidents": 4},
                confidence=0.95,
                data_truth=DataTruth.SYNTHETIC_DATA.value
            ),
            Evidence(
                case_id=case_id,
                type="MAINTENANCE",
                title="Previous intervention",
                source="Work Order DB",
                description="Drain cleaning. Outcome: Temporary improvement.",
                value={"outcome": "Temporary improvement"},
                confidence=0.8,
                data_truth=DataTruth.SYNTHETIC_DATA.value
            )
        ]
        db.add_all(evidences)

        print("6. Generating History...")
        histories = [
            HistoricalIncident(
                case_id=case_id,
                site_id=site_id,
                title="Waterlogging after heavy rainfall",
                occurred_at=datetime(2024, 7, 15),
                intervention_taken="Drain cleaning",
                intervention_outcome="Temporary improvement",
                data_truth=DataTruth.SYNTHETIC_DATA.value
            ),
            HistoricalIncident(
                case_id=case_id,
                site_id=site_id,
                title="Water accumulation returned",
                occurred_at=datetime(2025, 8, 22),
                intervention_taken="Drain maintenance",
                intervention_outcome="Partial improvement",
                data_truth=DataTruth.SYNTHETIC_DATA.value
            )
        ]
        db.add_all(histories)

        print("7. Generating Predictions (Do Nothing Baseline)...")
        pred_do_nothing = Prediction(
            case_id=case_id,
            predicted_metric="5_year_exposure",
            predicted_value=1.0, # normalized max risk
            confidence=0.8,
            horizon_days=1825,
            assumptions=["High recurrence exposure for Year 1-5"],
            data_truth=DataTruth.MODEL_ESTIMATION.value
        )
        db.add(pred_do_nothing)
        db.commit()

        print("8. Generating Interventions (Using InterventionEngine)...")
        from app.services.intervention_engine import InterventionEngine
        ie = InterventionEngine(db)
        ie.generate_interventions(case_id)
        
        # Add constraints
        constraints = ie.apply_constraints(case_id, {
            "budget_limit": 500000,
            "deadline": datetime.utcnow() + timedelta(days=7),
            "available_workers": 4
        })

        decision_analysis = ie.score_interventions(case_id)
        
        # Let's say user rejected the first one, selected the second one ("Drain Repair" which is index 2 in our templates)
        interventions = db.query(InterventionOption).filter(InterventionOption.case_id == case_id).all()
        drain_repair_opt = next((i for i in interventions if i.intervention_type == "drain_repair"), None)
        
        if drain_repair_opt:
            print("9. Approving Plan & Generating Execution Data...")
            plan = ie.create_resolution_plan(case_id, drain_repair_opt.intervention_id)
            plan.approval_state = ApprovalState.APPROVED.value
            plan.approved_by = "DEMO_OFFICER"
            db.commit()

            wo = WorkOrder(
                work_order_id=generate_uuid(),
                plan_id=plan.plan_id,
                intervention_id=drain_repair_opt.intervention_id,
                case_id=case_id,
                title="WO-2026-001: Drain Repair",
                description="Drain Repair at Kothrud-Bavdhan",
                status=WorkOrderStatus.COMPLETED.value,
                approval_state=ApprovalState.APPROVED.value,
                planned_start=datetime.utcnow() - timedelta(days=6),
                planned_end=datetime.utcnow() + timedelta(days=1),
                actual_start=datetime.utcnow() - timedelta(days=6),
                actual_end=datetime.utcnow() - timedelta(days=1)
            )
            db.add(wo)
            db.commit()

            tasks = [
                WorkOrderTask(
                    task_id=generate_uuid(),
                    work_order_id=wo.work_order_id,
                    title="Site inspection",
                    sequence=1,
                    status=TaskStatus.COMPLETED.value
                ),
                WorkOrderTask(
                    task_id=generate_uuid(),
                    work_order_id=wo.work_order_id,
                    title="Drain repair",
                    sequence=2,
                    status=TaskStatus.COMPLETED.value
                )
            ]
            db.add_all(tasks)

            # Replanning Event
            replan = ReplanEvent(
                replan_id=generate_uuid(),
                work_order_id=wo.work_order_id,
                reason="1 worker unavailable due to illness.",
                new_plan={"revised_duration": "9 days", "workers": 3},
                recommended_actions=["Extend deadline", "Reallocate workers", "Additional shift"],
                approved=True
            )
            db.add(replan)

            print("10. Field Verification & Outcome...")
            fe = FieldEvidence(
                evidence_id=generate_uuid(),
                work_order_id=wo.work_order_id,
                captured_at=datetime.utcnow() - timedelta(days=1),
                latitude=18.5089,
                longitude=73.7937,
                image_url="/demo/verification.jpg",
                visual_change="Detected",
                overall_consistency="HIGH"
            )
            db.add(fe)

            verif = Verification(
                verification_id=generate_uuid(),
                work_order_id=wo.work_order_id,
                status="PASSED",
                overall_consistency="HIGH",
                evidence_ids=[fe.evidence_id],
                verified_by="DEMO_INSPECTOR",
                verified_at=datetime.utcnow() - timedelta(days=1)
            )
            db.add(verif)

            outcome = OutcomeObservation(
                outcome_id=generate_uuid(),
                case_id=case_id,
                work_order_id=wo.work_order_id,
                observed_at=datetime.utcnow(),
                status="IMPROVED",
                trigger_event="NEXT COMPARABLE RAIN EVENT",
                observed_conditions={"before_complaints": 18, "after_complaints": 6, "comparable_event_complaints": 2, "disruption": "Reduced"},
                notes="OUTCOME CONSISTENT WITH EXPECTATION",
                data_truth=DataTruth.SYNTHETIC_DATA.value
            )
            db.add(outcome)

            print("11. Infrastructure Memory...")
            memory = InfrastructureMemory(
                memory_id=generate_uuid(),
                site_id=site_id,
                title="Kothrud-Bavdhan Drainage Action",
                summary="Previous drain cleaning provided temporary improvement. Current intervention (Drain Repair) produced lower recurrence in the demonstration outcome.",
                total_complaints=24,
                total_cases=1,
                total_interventions=3,
                total_recurrences=1,
                last_intervention_at=datetime.utcnow(),
                learned_patterns=["Drain cleaning is insufficient for structural blockages.", "Drain repair effectively handles standard rainfall events."]
            )
            db.add(memory)

            db.commit()

        print("=== DEMO DATA GENERATION COMPLETE ===")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_demo_data()
