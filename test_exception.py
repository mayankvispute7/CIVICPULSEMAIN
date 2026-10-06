import requests, json
payload = {
  'case_id': 'f271b76e-5a73-402a-b237-2718c352bf8f',
  'work_order_id': '894dfdfa-34f3-45bc-ae41-71cc18cde66e',
  'observed_at': '2026-10-06T12:00:00Z',
  'status': 'IMPROVED',
  'trigger_event': 'test',
  'trigger_event_details': {'rainfall_mm_per_hr': 45, 'duration_hours': 3},
  'observed_conditions': {'before_complaints': 12, 'after_complaints': 0, 'waterlogging_duration_mins': 15},
  'complaints_during_event': 0,
  'notes': 'Post-intervention monitoring shows no severe waterlogging during peak monsoon burst.'
}
res = requests.post('http://localhost:8000/api/v1/outcomes', json=payload)
print(res.status_code, res.text)
