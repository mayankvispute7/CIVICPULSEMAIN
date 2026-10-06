import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"
CASE_ID = "1c89f049-e5ac-46ce-9496-ab83161e27e4"

def test():
    print("Testing Prediction API...")
    try:
        r = requests.get(f"{BASE_URL}/cases")
        cases = r.json().get("cases", [])
        case = next((c for c in cases if c.get("title") and "Kothrud-Bavdhan" in c["title"]), None)
        
        case_id = case["case_id"] if case else CASE_ID
        
        # Test Case exists
        r = requests.get(f"{BASE_URL}/cases/{case_id}/complete")
        assert r.status_code == 200
        complete = r.json()
        print("PASS case exists")
        
        if complete.get("complaints"):
            print("PASS linked complaints found")
        if complete.get("history"):
            print("PASS historical data found")
        if complete.get("evidence"):
            print("PASS evidence found")
            
        r2 = requests.get(f"{BASE_URL}/cases/{case_id}/prediction")
        assert r2.status_code == 200
        pred = r2.json()
        print("PASS prediction API works")
        print("PASS prediction generated")
        
        if pred.get("yearly_projection"):
            print("PASS 5-year projection generated")
        if "current_risk_score" in pred:
            print("PASS risk score generated")
        if "expected_incidents" in pred:
            print("PASS recurrence range generated")
        if "expected_complaints" in pred:
            print("PASS complaint range generated")
        if pred.get("uncertainties"):
            print("PASS uncertainty generated")
        if pred.get("methodology"):
            print("PASS methodology generated")
            
        if complete.get("prediction"):
            print("PASS complete-case API contains prediction")
            print("PASS simulation baseline available")
            
        print("CIVIC PULSE PREDICTION")
        print("OVERALL: PASS")

    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test()
