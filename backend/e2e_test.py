import requests
import time
import json
import os

BASE_URL = "http://localhost:8000/api/v1"

def run_test():
    report = []
    def log_step(step, endpoint, status, result, error=None, request_data=None):
        print(f"[{status}] Step {step}: {endpoint} - {result}")
        if error:
            print(f"   Error: {error}")
        report.append({
            "step": step,
            "endpoint": endpoint,
            "status": status,
            "result": result,
            "error": error,
            "request_data": request_data
        })
        if status == "FAIL":
            # stop on first fail for now
            return False
        return True

    # 1. Health
    try:
        r = requests.get(f"http://localhost:8000/health")
        if r.status_code == 200:
            log_step("1. Health", "/health", "PASS", "Backend healthy")
        else:
            if not log_step("1. Health", "/health", "FAIL", f"Status: {r.status_code}", r.text): return report
    except Exception as e:
        if not log_step("1. Health", "/health", "FAIL", "Request failed", str(e)): return report

    # 2. CSV ingestion
    csv_path = "../pune_baner_complaints_20.csv"
    if not os.path.exists(csv_path):
        if not log_step("2. CSV Ingestion", "/ingest/csv", "FAIL", "CSV not found", f"Path: {csv_path}"): return report
    
    try:
        with open(csv_path, 'rb') as f:
            files = {'file': ('pune_baner_complaints_20.csv', f, 'text/csv')}
            data = {'data_truth': 'SYNTHETIC_DATA'}
            r = requests.post(f"{BASE_URL}/ingest/csv", files=files, data=data)
            if r.status_code == 200:
                res_data = r.json()
                log_step("2. CSV Ingestion", "/ingest/csv", "PASS", f"Imported {res_data.get('total_rows')} rows")
            else:
                if not log_step("2. CSV Ingestion", "/ingest/csv", "FAIL", f"Status: {r.status_code}", r.text): return report
    except Exception as e:
        if not log_step("2. CSV Ingestion", "/ingest/csv", "FAIL", "Request failed", str(e)): return report

    # 3. Complaint retrieval
    try:
        r = requests.get(f"{BASE_URL}/complaints")
        if r.status_code == 200:
            complaints = r.json().get('complaints', [])
            total = len(complaints)
            log_step("3. Complaint retrieval", "/complaints", "PASS", f"Retrieved {total} complaints")
        else:
            if not log_step("3. Complaint retrieval", "/complaints", "FAIL", f"Status: {r.status_code}", r.text): return report
    except Exception as e:
        if not log_step("3. Complaint retrieval", "/complaints", "FAIL", "Request failed", str(e)): return report

    # 4. Clustering
    try:
        r = requests.post(f"{BASE_URL}/complaints/cluster")
        if r.status_code == 200:
            clusters = r.json().get('clusters', [])
            log_step("4. Clustering", "/complaints/cluster", "PASS", f"Created {len(clusters)} clusters")
        else:
            if not log_step("4. Clustering", "/complaints/cluster", "FAIL", f"Status: {r.status_code}", r.text): return report
    except Exception as e:
        if not log_step("4. Clustering", "/complaints/cluster", "FAIL", "Request failed", str(e)): return report

    # 5. Cluster retrieval
    cluster_id = None
    try:
        r = requests.get(f"{BASE_URL}/complaints/clusters/all")
        if r.status_code == 200:
            clusters = r.json().get('clusters', [])
            if clusters:
                cluster_id = clusters[0].get('cluster_id')
                log_step("5. Cluster retrieval", "/complaints/clusters/all", "PASS", f"Cluster ID: {cluster_id}")
            else:
                if not log_step("5. Cluster retrieval", "/complaints/clusters/all", "FAIL", "No clusters returned", ""): return report
        else:
            if not log_step("5. Cluster retrieval", "/complaints/clusters/all", "FAIL", f"Status: {r.status_code}", r.text): return report
    except Exception as e:
        if not log_step("5. Cluster retrieval", "/complaints/clusters/all", "FAIL", "Request failed", str(e)): return report

    # 6. Failure case creation
    case_id = None
    try:
        # Check routers to see how a case is created. We will do this dynamically by checking endpoints.
        r = requests.post(f"{BASE_URL}/cases", json={"cluster_id": cluster_id})
        if r.status_code == 200:
            case_id = r.json().get("case_id")
            log_step("6. Failure case creation", "/cases", "PASS", f"Created Case: {case_id}")
        else:
            if not log_step("6. Failure case creation", "/cases", "FAIL", f"Status: {r.status_code}", r.text): return report
    except Exception as e:
        if not log_step("6. Failure case creation", "/cases", "FAIL", "Request failed", str(e)): return report
        
    with open("e2e_report.json", "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    run_test()
