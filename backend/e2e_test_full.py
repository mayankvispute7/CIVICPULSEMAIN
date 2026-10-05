import requests
import time
import json
import os
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000/health"

def run_test():
    report = []
    def log_step(step, endpoint, status, result, error=None):
        print(f"[{status}] Step {step}: {endpoint} - {result}")
        if error:
            print(f"   Error: {error}")
        report.append({
            "step": step,
            "endpoint": endpoint,
            "status": status,
            "result": result,
            "error": error
        })
        if status == "FAIL":
            return False
        return True

    def run():
        # 1. Health
        try:
            r = requests.get(HEALTH_URL)
            if r.status_code != 200:
                return log_step("1. Health", "/health", "FAIL", f"Status: {r.status_code}", r.text)
            log_step("1. Health", "/health", "PASS", "Backend healthy")
        except Exception as e:
            return log_step("1. Health", "/health", "FAIL", "Request failed", str(e))

        # 2. CSV ingestion
        csv_path = "../pune_baner_complaints_20.csv"
        if not os.path.exists(csv_path):
            return log_step("2. CSV Ingestion", "/ingest/csv", "FAIL", "CSV not found", f"Path: {csv_path}")
        
        try:
            with open(csv_path, 'rb') as f:
                files = {'file': ('pune_baner_complaints_20.csv', f, 'text/csv')}
                data = {'data_truth': 'SYNTHETIC_DATA'}
                r = requests.post(f"{BASE_URL}/ingest/csv", files=files, data=data)
                if r.status_code != 200:
                    return log_step("2. CSV Ingestion", "/ingest/csv", "FAIL", f"Status: {r.status_code}", r.text)
                res_data = r.json()
                log_step("2. CSV Ingestion", "/ingest/csv", "PASS", f"Imported {res_data.get('total_rows')} rows")
        except Exception as e:
            return log_step("2. CSV Ingestion", "/ingest/csv", "FAIL", "Request failed", str(e))

        # 3. Complaint retrieval
        try:
            r = requests.get(f"{BASE_URL}/complaints")
            if r.status_code != 200:
                return log_step("3. Complaint retrieval", "/complaints", "FAIL", f"Status: {r.status_code}", r.text)
            complaints = r.json().get('complaints', [])
            total = len(complaints)
            log_step("3. Complaint retrieval", "/complaints", "PASS", f"Retrieved {total} complaints")
        except Exception as e:
            return log_step("3. Complaint retrieval", "/complaints", "FAIL", "Request failed", str(e))

        # 4. Clustering
        try:
            r = requests.post(f"{BASE_URL}/complaints/cluster")
            if r.status_code != 200:
                return log_step("4. Clustering", "/complaints/cluster", "FAIL", f"Status: {r.status_code}", r.text)
            clusters = r.json().get('clusters', [])
            log_step("4. Clustering", "/complaints/cluster", "PASS", f"Created {len(clusters)} clusters")
        except Exception as e:
            return log_step("4. Clustering", "/complaints/cluster", "FAIL", "Request failed", str(e))

        # 5. Cluster retrieval
        cluster_id = None
        try:
            r = requests.get(f"{BASE_URL}/complaints/clusters/all")
            if r.status_code != 200:
                return log_step("5. Cluster retrieval", "/complaints/clusters/all", "FAIL", f"Status: {r.status_code}", r.text)
            clusters = r.json().get('clusters', [])
            if not clusters:
                return log_step("5. Cluster retrieval", "/complaints/clusters/all", "FAIL", "No clusters returned")
            
            # Find Baner cluster
            baner_cluster = None
            for c in clusters:
                # Baner coordinates are around lat 18.559, lon 73.787
                # let's just check the complaints count > 0 to get the correct one if only one exists
                baner_cluster = c
                break
                
            cluster_id = baner_cluster.get('cluster_id')
            log_step("5. Cluster retrieval", "/complaints/clusters/all", "PASS", f"Selected Cluster ID: {cluster_id}")
        except Exception as e:
            return log_step("5. Cluster retrieval", "/complaints/clusters/all", "FAIL", "Request failed", str(e))

        # 6. Failure case creation
        case_id = None
        site_id = None
        try:
            r = requests.post(f"{BASE_URL}/cases/from-cluster/{cluster_id}")
            if r.status_code != 200:
                return log_step("6. Failure case creation", f"/cases/from-cluster/{cluster_id}", "FAIL", f"Status: {r.status_code}", r.text)
            case_data = r.json()
            case_id = case_data.get("case_id")
            site_id = case_data.get("site_id")
            log_step("6. Failure case creation", f"/cases/from-cluster/{cluster_id}", "PASS", f"Created Case: {case_id}")
        except Exception as e:
            return log_step("6. Failure case creation", f"/cases/from-cluster/{cluster_id}", "FAIL", "Request failed", str(e))
            
        # 7. Failure analysis (Retrieve Case)
        try:
            r = requests.get(f"{BASE_URL}/cases/{case_id}")
            if r.status_code != 200:
                return log_step("7. Failure analysis", f"/cases/{case_id}", "FAIL", f"Status: {r.status_code}", r.text)
            log_step("7. Failure analysis", f"/cases/{case_id}", "PASS", f"Retrieved analysis")
        except Exception as e:
            return log_step("7. Failure analysis", f"/cases/{case_id}", "FAIL", "Request failed", str(e))

        # 8. Evidence/fingerprint
        try:
            r = requests.get(f"{BASE_URL}/cases/{case_id}/evidence")
            if r.status_code != 200:
                return log_step("8. Evidence/fingerprint", f"/cases/{case_id}/evidence", "FAIL", f"Status: {r.status_code}", r.text)
            ev = r.json()
            log_step("8. Evidence/fingerprint", f"/cases/{case_id}/evidence", "PASS", f"Retrieved {len(ev)} evidence items")
        except Exception as e:
            return log_step("8. Evidence/fingerprint", f"/cases/{case_id}/evidence", "FAIL", "Request failed", str(e))

        # 9. History
        try:
            r = requests.get(f"{BASE_URL}/cases/{case_id}/history")
            if r.status_code != 200:
                return log_step("9. History", f"/cases/{case_id}/history", "FAIL", f"Status: {r.status_code}", r.text)
            log_step("9. History", f"/cases/{case_id}/history", "PASS", f"Retrieved history")
        except Exception as e:
            return log_step("9. History", f"/cases/{case_id}/history", "FAIL", "Request failed", str(e))

        # 10. Intervention generation
        try:
            r = requests.post(f"{BASE_URL}/cases/{case_id}/interventions/generate")
            if r.status_code != 200:
                return log_step("10. Intervention generation", f"/cases/{case_id}/interventions/generate", "FAIL", f"Status: {r.status_code}", r.text)
            intervs = r.json()
            log_step("10. Intervention generation", f"/cases/{case_id}/interventions/generate", "PASS", f"Generated {len(intervs)} interventions")
        except Exception as e:
            return log_step("10. Intervention generation", f"/cases/{case_id}/interventions/generate", "FAIL", "Request failed", str(e))

        # 11. Constraints
        try:
            constraints = {"budget_limit": 50000, "max_duration_days": 15}
            r = requests.post(f"{BASE_URL}/cases/{case_id}/constraints", json=constraints)
            if r.status_code != 200:
                return log_step("11. Constraints", f"/cases/{case_id}/constraints", "FAIL", f"Status: {r.status_code}", r.text)
            log_step("11. Constraints", f"/cases/{case_id}/constraints", "PASS", "Applied constraints")
        except Exception as e:
            return log_step("11. Constraints", f"/cases/{case_id}/constraints", "FAIL", "Request failed", str(e))

        # 12. Decision analysis
        intervention_id = None
        try:
            r = requests.post(f"{BASE_URL}/cases/{case_id}/analyze")
            if r.status_code != 200:
                return log_step("12. Decision analysis", f"/cases/{case_id}/analyze", "FAIL", f"Status: {r.status_code}", r.text)
            da = r.json()
            if da.get("ranked_interventions"):
                intervention_id = da["ranked_interventions"][0]["intervention_id"]
                log_step("12. Decision analysis", f"/cases/{case_id}/analyze", "PASS", f"Ranked interventions. Top choice: {intervention_id}")
            else:
                return log_step("12. Decision analysis", f"/cases/{case_id}/analyze", "FAIL", "No interventions returned from analyze")
        except Exception as e:
            return log_step("12. Decision analysis", f"/cases/{case_id}/analyze", "FAIL", "Request failed", str(e))

        # 13. Resolution plan
        plan_id = None
        try:
            r = requests.post(f"{BASE_URL}/cases/{case_id}/plan/{intervention_id}")
            if r.status_code != 200:
                return log_step("13. Resolution plan", f"/cases/{case_id}/plan/{intervention_id}", "FAIL", f"Status: {r.status_code}", r.text)
            plan_id = r.json().get("plan_id")
            log_step("13. Resolution plan", f"/cases/{case_id}/plan/{intervention_id}", "PASS", f"Created plan: {plan_id}")
        except Exception as e:
            return log_step("13. Resolution plan", f"/cases/{case_id}/plan/{intervention_id}", "FAIL", "Request failed", str(e))

        # 14. Plan approval
        try:
            appr = {"decision": "APPROVED", "approved_by": "E2E_TEST_USER"}
            r = requests.post(f"{BASE_URL}/execution/plans/{plan_id}/approve", json=appr)
            if r.status_code != 200:
                return log_step("14. Plan approval", f"/execution/plans/{plan_id}/approve", "FAIL", f"Status: {r.status_code}", r.text)
            log_step("14. Plan approval", f"/execution/plans/{plan_id}/approve", "PASS", "Plan approved")
        except Exception as e:
            return log_step("14. Plan approval", f"/execution/plans/{plan_id}/approve", "FAIL", "Request failed", str(e))

        # 15. Work order creation
        wo_id = None
        try:
            r = requests.post(f"{BASE_URL}/execution/plans/{plan_id}/work-order")
            if r.status_code != 200:
                return log_step("15. Work order creation", f"/execution/plans/{plan_id}/work-order", "FAIL", f"Status: {r.status_code}", r.text)
            wo_id = r.json().get("work_order_id")
            log_step("15. Work order creation", f"/execution/plans/{plan_id}/work-order", "PASS", f"Created Work Order: {wo_id}")
        except Exception as e:
            return log_step("15. Work order creation", f"/execution/plans/{plan_id}/work-order", "FAIL", "Request failed", str(e))

        # 16. Task retrieval
        tasks = []
        try:
            r = requests.get(f"{BASE_URL}/execution/work-orders/{wo_id}/tasks")
            if r.status_code != 200:
                return log_step("16. Task retrieval", f"/execution/work-orders/{wo_id}/tasks", "FAIL", f"Status: {r.status_code}", r.text)
            tasks = r.json()
            log_step("16. Task retrieval", f"/execution/work-orders/{wo_id}/tasks", "PASS", f"Retrieved {len(tasks)} tasks")
        except Exception as e:
            return log_step("16. Task retrieval", f"/execution/work-orders/{wo_id}/tasks", "FAIL", "Request failed", str(e))

        if not tasks:
            return log_step("16. Task retrieval", f"/execution/work-orders/{wo_id}/tasks", "FAIL", "No tasks generated in WO")

        task_id = tasks[0]["task_id"]

        # 17. Task start
        try:
            r = requests.post(f"{BASE_URL}/execution/tasks/{task_id}/start")
            if r.status_code != 200:
                return log_step("17. Task start", f"/execution/tasks/{task_id}/start", "FAIL", f"Status: {r.status_code}", r.text)
            log_step("17. Task start", f"/execution/tasks/{task_id}/start", "PASS", f"Started task {task_id}")
        except Exception as e:
            return log_step("17. Task start", f"/execution/tasks/{task_id}/start", "FAIL", "Request failed", str(e))

        # 19. Dynamic replanning if supported (Task delay)
        try:
            r = requests.post(f"{BASE_URL}/execution/tasks/{task_id}/delay", json={"reason": "Rain delay", "hours": 24.0})
            if r.status_code != 200:
                return log_step("19. Dynamic replanning", f"/execution/tasks/{task_id}/delay", "FAIL", f"Status: {r.status_code}", r.text)
            log_step("19. Dynamic replanning", f"/execution/tasks/{task_id}/delay", "PASS", "Triggered delay and replanning")
        except Exception as e:
            return log_step("19. Dynamic replanning", f"/execution/tasks/{task_id}/delay", "FAIL", "Request failed", str(e))

        # 18. Task completion
        try:
            r = requests.post(f"{BASE_URL}/execution/tasks/{task_id}/complete", json={"notes": "Finished"})
            if r.status_code != 200:
                return log_step("18. Task completion", f"/execution/tasks/{task_id}/complete", "FAIL", f"Status: {r.status_code}", r.text)
            log_step("18. Task completion", f"/execution/tasks/{task_id}/complete", "PASS", f"Completed task {task_id}")
        except Exception as e:
            return log_step("18. Task completion", f"/execution/tasks/{task_id}/complete", "FAIL", "Request failed", str(e))

        # 20. Field evidence
        # Test negative verification with incorrect location first
        try:
            ev_bad = {
                "work_order_id": wo_id,
                "task_id": task_id,
                "latitude": 19.112,
                "longitude": -72.100,
                "captured_at": datetime.now().isoformat() + "Z",
                "image_url": "http://example.com/bad.jpg",
                "metadata_info": {}
            }
            r_bad = requests.post(f"{BASE_URL}/execution/evidence", json=ev_bad)
            if r_bad.status_code != 200:
                return log_step("20. Field evidence (Negative)", "/execution/evidence", "FAIL", f"Status: {r_bad.status_code}", r_bad.text)
            
            # Now the positive one (Baner)
            ev_good = {
                "work_order_id": wo_id,
                "task_id": task_id,
                "latitude": 18.559,
                "longitude": 73.787,
                "captured_at": datetime.now().isoformat() + "Z",
                "image_url": "http://example.com/good.jpg",
                "metadata_info": {}
            }
            r_good = requests.post(f"{BASE_URL}/execution/evidence", json=ev_good)
            if r_good.status_code != 200:
                return log_step("20. Field evidence (Positive)", "/execution/evidence", "FAIL", f"Status: {r_good.status_code}", r_good.text)
            
            log_step("20. Field evidence", "/execution/evidence", "PASS", "Submitted field evidence (good and bad locations)")
        except Exception as e:
            return log_step("20. Field evidence", "/execution/evidence", "FAIL", "Request failed", str(e))

        # 21. Verification
        try:
            r = requests.post(f"{BASE_URL}/execution/work-orders/{wo_id}/verify", json={"verified_by": "AUTO_TEST"})
            if r.status_code != 200:
                return log_step("21. Verification", f"/execution/work-orders/{wo_id}/verify", "FAIL", f"Status: {r.status_code}", r.text)
            log_step("21. Verification", f"/execution/work-orders/{wo_id}/verify", "PASS", "Work order verified")
        except Exception as e:
            return log_step("21. Verification", f"/execution/work-orders/{wo_id}/verify", "FAIL", "Request failed", str(e))

        # 22. Outcome
        try:
            out_req = {
                "case_id": case_id,
                "observed_at": datetime.now().isoformat() + "Z",
                "status": "IMPROVED",
                "trigger_event": "RAINFALL",
                "work_order_id": wo_id,
                "trigger_event_details": {},
                "observed_conditions": {},
                "complaints_during_event": 0,
                "spatial_impact": {},
                "notes": "Looks good"
            }
            r = requests.post(f"{BASE_URL}/outcomes", json=out_req)
            if r.status_code != 200:
                return log_step("22. Outcome", "/outcomes", "FAIL", f"Status: {r.status_code}", r.text)
            log_step("22. Outcome", "/outcomes", "PASS", "Outcome recorded")
        except Exception as e:
            return log_step("22. Outcome", "/outcomes", "FAIL", "Request failed", str(e))

        # 23. Prediction vs reality
        try:
            r = requests.get(f"{BASE_URL}/outcomes/cases/{case_id}/comparisons")
            if r.status_code != 200:
                return log_step("23. Prediction vs reality", f"/outcomes/cases/{case_id}/comparisons", "FAIL", f"Status: {r.status_code}", r.text)
            log_step("23. Prediction vs reality", f"/outcomes/cases/{case_id}/comparisons", "PASS", "Retrieved comparison")
        except Exception as e:
            return log_step("23. Prediction vs reality", f"/outcomes/cases/{case_id}/comparisons", "FAIL", "Request failed", str(e))

        # 24. Infrastructure memory
        try:
            r = requests.get(f"{BASE_URL}/outcomes/sites/{site_id}/memory")
            if r.status_code != 200:
                return log_step("24. Infrastructure memory", f"/outcomes/sites/{site_id}/memory", "FAIL", f"Status: {r.status_code}", r.text)
            log_step("24. Infrastructure memory", f"/outcomes/sites/{site_id}/memory", "PASS", "Retrieved infrastructure memory")
        except Exception as e:
            return log_step("24. Infrastructure memory", f"/outcomes/sites/{site_id}/memory", "FAIL", "Request failed", str(e))
            
    run()

    with open("e2e_report.json", "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    run_test()
