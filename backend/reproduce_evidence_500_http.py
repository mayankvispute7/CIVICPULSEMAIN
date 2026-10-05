import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

r = requests.get(f"{BASE_URL}/complaints/clusters/all")
clusters = r.json().get('clusters', [])
cluster_id = clusters[0]['cluster_id']

r = requests.post(f"{BASE_URL}/cases/from-cluster/{cluster_id}")
case_id = r.json().get("case_id")

r = requests.post(f"{BASE_URL}/cases/{case_id}/interventions/generate")
r = requests.post(f"{BASE_URL}/cases/{case_id}/analyze")
intervention_id = r.json()["ranked_interventions"][0]["intervention_id"]

r = requests.post(f"{BASE_URL}/cases/{case_id}/plan/{intervention_id}")
plan_id = r.json().get("plan_id")

requests.post(f"{BASE_URL}/execution/plans/{plan_id}/approve", json={"decision": "APPROVED", "approved_by": "test"})
r = requests.post(f"{BASE_URL}/execution/plans/{plan_id}/work-order")
wo_id = r.json().get("work_order_id")

r = requests.get(f"{BASE_URL}/execution/work-orders/{wo_id}/tasks")
tasks = r.json()
task_id = tasks[0]["task_id"]

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
print(r_bad.status_code)
print(r_bad.text)
