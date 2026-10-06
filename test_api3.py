import requests, json, datetime

res1 = requests.post('http://localhost:8000/api/v1/outcomes', json={
  'case_id': 'f271b76e-5a73-402a-b237-2718c352bf8f',
  'work_order_id': 'test',
  'observed_at': datetime.datetime.now().isoformat(),
  'status': 'IMPROVED',
  'trigger_event': 'test'
})
print(res1.text)
