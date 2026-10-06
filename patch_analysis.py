import re

with open('backend/app/api/routers/analysis.py', 'r') as f:
    code = f.read()

helper = """
def resolve_case(case_id: str, db: Session) -> str:
    from app.services.failure_analysis_service import FailureAnalysisService
    case = FailureAnalysisService(db).get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.case_id
"""

if "def resolve_case" not in code:
    code = code.replace("router = APIRouter()", "router = APIRouter()\n" + helper)

def patch_endpoint(func_name):
    global code
    pattern = r"(def " + func_name + r"\(.*?case_id: str.*?\):\n\s+\"\"\"[^\"]*\"\"\"\n)(\s+)"
    replacement = r"\1\2case_id = resolve_case(case_id, db)\n\2"
    code = re.sub(pattern, replacement, code, count=1)

funcs_to_patch = [
    "generate_interventions",
    "get_interventions",
    "apply_constraints",
    "run_decision_analysis",
    "get_cost_of_inaction",
    "get_counterfactual",
    "get_resolution_plan",
    "get_simulation_runs",
    "update_simulation_constraints",
    "get_predictions"
]

for f in funcs_to_patch:
    patch_endpoint(f)

with open('backend/app/api/routers/analysis.py', 'w') as f:
    f.write(code)

print("Patched successfully")
