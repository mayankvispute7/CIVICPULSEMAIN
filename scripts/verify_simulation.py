import os
import sys

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.intervention_engine import InterventionEngine
from app.schemas.api_schemas import SimulationRequest

def verify_simulation():
    db: Session = SessionLocal()
    try:
        case_id = "1c89f049-e5ac-46ce-9496-ab83161e27e4"
        engine = InterventionEngine(db)
        
        print("1. Testing baseline generation...")
        baseline = engine.generate_baseline_prediction(case_id)
        if not baseline:
            print("Failed to generate baseline.")
            return
        
        print(f"Baseline risk score: {baseline.get('current_risk_score')}")
        print(f"Baseline risk level: {baseline.get('risk_level')}")
        
        # Get interventions
        interventions = engine.get_interventions(case_id)
        if not interventions:
            print("No interventions found. Generating...")
            interventions = engine.generate_interventions(case_id)
            
        print(f"Found {len(interventions)} interventions.")
        
        if not interventions:
            print("Still no interventions. Aborting.")
            return
            
        # Try a simulation that should be feasible
        intervention = interventions[0]
        print(f"\n2. Testing Simulation (FEASIBLE) for {intervention.title}...")
        
        req_feasible = SimulationRequest(
            intervention_id=intervention.intervention_id,
            budget=intervention.estimated_cost + 100000,
            deadline_days=intervention.estimated_duration_days + 10,
            workers=intervention.workers_required + 5
        )
        
        res_feasible = engine.run_simulation(case_id, req_feasible)
        
        print(f"Feasibility: {res_feasible['feasibility']}")
        print(f"Risk before: {res_feasible['risk_before']}")
        print(f"Risk after: {res_feasible['risk_after']}")
        print(f"Risk reduction: {res_feasible['risk_reduction']}")
        assert res_feasible['feasibility'] == "FEASIBLE"
        assert res_feasible['risk_after'] < res_feasible['risk_before'] or res_feasible['risk_before'] == 0
        
        print(f"\n3. Testing Simulation (INFEASIBLE) for {intervention.title}...")
        req_infeasible = SimulationRequest(
            intervention_id=intervention.intervention_id,
            budget=intervention.estimated_cost - 1000, # Too low budget
            deadline_days=intervention.estimated_duration_days + 10,
            workers=intervention.workers_required + 5
        )
        
        res_infeasible = engine.run_simulation(case_id, req_infeasible)
        
        print(f"Feasibility: {res_infeasible['feasibility']}")
        print(f"Reasons: {res_infeasible['reasons']}")
        assert res_infeasible['feasibility'] == "NOT FEASIBLE"
        
        print("\n4. Checking simulation run history persistence...")
        runs = engine.get_simulation_runs(case_id)
        print(f"Found {len(runs)} simulation runs.")
        assert len(runs) >= 2
        
        print("\n✅ Simulation engine verification successful!")

    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_simulation()
